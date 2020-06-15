import datetime
import argparse
import os
from datetime import date
from pprint import pprint
from client.models import Document
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from pprint import pprint
import PyPDF2

from src.utils.logging import init_logger
from client.forms import DocumentForm
from client.models import Summary
from client import extraction
from src.train_abstractive import test_text_abs


def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


class parser:
    #parser.add_argument("-task", default='abs', type=str, choices=['ext', 'abs'])
    #parser.add_argument("-large", type=str2bool, nargs='?',const=True,default=False)
    #parser.add_argument("-sep_optim", type=str2bool, nargs='?',const=True,default=False)
    #parser.add_argument("-use_bert_emb", type=str2bool, nargs='?',const=True,default=False)


    task = 'abs'
    encode='bert' # type=str, choices=['bert', 'baseline'])
    mode='test_text' # type=str, choices=['train', 'validate', 'test', 'test_text'])
    test_from = 'base_model.pt'
    result_path =  f'./results/{str(datetime.datetime.now())}'
    log_file = './logs/abs/'
    visible_gpus='-1' # type=str)

    bert_data_path='./bert_data_new/cnndm'
    model_path='./models/'
    temp_dir='./temp'
    text_tgt=''

    batch_size=140 # type=int)
    test_batch_size=200 # type=int)
    max_ndocs_in_batch=6 # type=int)

    max_pos=512 # type=int)
    use_interval=True
    large=False
    load_from_extractive='' # type=str)

    sep_optim=False
    lr_bert=2e-3 # type=float)
    lr_dec=2e-3 # type=float)
    use_bert_emb=False

    share_emb=False
    finetune_bert=True
    dec_dropout=0.2 # type=float)
    dec_layers=6 # type=int)
    dec_hidden_size=768 # type=int)
    dec_heads=8 # type=int)
    dec_ff_size=2048 # type=int)
    enc_hidden_size=512 # type=int)
    enc_ff_size=512 # type=int)
    enc_dropout=0.2 # type=float)
    enc_layers=6 # type=int)

    # params for EXT
    ext_dropout=0.2 # type=float)
    ext_layers=2 # type=int)
    ext_hidden_size=768 # type=int)
    ext_heads=8 # type=int)
    ext_ff_size=2048 # type=int)

    label_smoothing=0.1 # type=float)
    generator_shard_size=32 # type=int)
    alpha=0.6 # type=float)
    beam_size=5 # type=int)
    min_length=15 # type=int)
    max_length=150 # type=int)
    max_tgt_len=140 # type=int)

    param_init=0 # type=float)
    param_init_glorot=True
    optim='adam' # type=str)
    lr=1 # type=float)
    beta1= 0.9 # type=float)
    beta2=0.999 # type=float)
    warmup_steps=8000 # type=int)
    warmup_steps_bert=8000 # type=int)
    warmup_steps_dec=8000 # type=int)
    max_grad_norm=0 # type=float)

    save_checkpoint_steps=5 # type=int)
    accum_count=1 # type=int)
    report_every=1 # type=int)
    train_steps=1000 # type=int)
    recall_eval=False

    gpu_ranks='0' # type=str)
    seed=666 # type=int)

    test_all=False
    test_start_from=-1 # type=int)

    train_from=''
    report_rouge=True
    block_trigram=True

args = parser

args.gpu_ranks = [int(i) for i in range(len(args.visible_gpus.split(',')))]
args.world_size = len(args.gpu_ranks)
os.environ["CUDA_VISIBLE_DEVICES"] = args.visible_gpus

init_logger(args.log_file)
device = "cpu" if args.visible_gpus == '-1' else "cuda"
device_id = 0 if device == "cuda" else -1


def summarize_pdf(pdf_file, sent_percentage):
    pdf_file_obj = open(pdf_file, 'rb')
    pdf_reader = PyPDF2.PdfFileReader(pdf_file_obj)
    title = pdf_reader.getDocumentInfo().title
    summary_title = "Summary"
    if title is not None:
        summary_title = title+' - '+summary_title
    num_of_pages = pdf_reader.numPages
    body = ''
    for i in range(num_of_pages):
        pageobj = pdf_reader.getPage(i)
        body = body + "\n\n" + pageobj.extractText()

    pdf_file_obj.close()

    summary = test_text_abs(parser, body)

    summary = summary_title+"\r\n\r\n"+summary

    return summary


def index(request):
    return render(request, 'client/index.html')


def summarize_page(request):
    url = request.GET.get('url')
    long_text = request.GET.get('message')
    sentence_no = int(request.GET.get('phone'))
    algorithm = request.GET.get('algorithm')
    result_list = []

    if url:
        long_text = extraction.extract(url)  # text extraction using BS
        original_text = url
    else:
        original_text = long_text
        long_text = long_text.replace('\n', ' ').replace('\r', '')
        print (long_text)

    #result_list = scoring_algorithm.scoring_main(long_text, sentence_no)
    results = test_text_abs(args, long_text)

    #summary = ' '.join(result_list)

    context = {'data': 'done', 'original_text': original_text}
    return render(request, "client/index.html", context)


@login_required
def save_summary(request):
    summary = request.POST.get('summary')
    topic = request.POST.get('topic')
    if len(topic) < 50:
        heading = topic
    else:
        heading = topic[:50] + '...'

    summaryTb = Summary(user=request.user, body=summary, original_link=heading, date_created=date.today())
    summaryTb.save()
    context = {'message': 'success'}
    return render(request, "summarizer/index.html", context)


def history(request):
    summary = Summary.objects.filter(user=request.user).order_by('-id')
    context = {'data': summary}
    return render(request, "summarizer/history.html", context)


def history_topic(request):
    if request.method == 'GET':
        topic = request.GET.get('topic')
        summary = request.GET.get('body')
        context = {'topic': topic, 'body': summary}
        return render(request, "summarizer/history_topic.html", context)


def file_form_upload(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            summary_p = form.cleaned_data['summary_p']
            file_name = form.cleaned_data['document'].name
            file_name = file_name.replace(' ', '_')
            outputfile = file_name[:-4]
            out_file_name = outputfile+'.txt'

            form.save()

            media_root = getattr(settings, 'MEDIA_ROOT', None)
            file_location = os.path.join(media_root, file_name)

            summary = summarize_pdf(file_location, summary_p)
            response = HttpResponse(summary, content_type='text/plain')
            response['Content-Disposition'] = 'attachment; filename={0}'.format(out_file_name)

            os.remove(os.path.join(media_root, file_location))

            Document.objects.all().delete()

            return response
    else:
        form = DocumentForm()
    return render(request, 'news/file_form.html', {
        'form': form
    })
