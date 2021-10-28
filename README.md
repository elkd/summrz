# Summrz

This is a web app built with Django that provides a nice user interface to the state-of-the-art abstractive summarization work, Text Summarization with Pretrained Encoders 
[Published here by Yang Liu and Mirella Lapata in 2019](https://arxiv.org/abs/1908.08345). Instead of the common seq2seq, this work applies Encoder Representations Transformers (BERT) for the summarization task.

Most breaking through research works takes forever to be appreciated and getting deployed for real-world application. 
I felt much more on the summarization task, I couldn't find a single website or service offering abtractive summarization. 
This work is still far from perfect but quite powerful, the model is able to not only extract sentences from original piece of text but use its own words where necessary to produce a summary.
This is my attempt to deploy a working example for people to easily play with the models and see how far this field has gone.


## Downloading Trained Models
This project has four ready trained models that you can directly install and work with them. First model is BERT Extractive only, second is both extractive and abstractive (BERT), third is abstractive only.
These 3 uses CNN and Daily Mail data. The fourth model is both Extractive and abstractive but it uses:

[CNN/DM BertExt](https://drive.google.com/open?id=1kKWoV0QCbeIuFt85beQgJ4v0lujaXobJ)

[CNN/DM BertExtAbs](https://drive.google.com/open?id=1-IKVCtc4Q-BdZpjXc4s70_fRsWnjtYLr)

[CNN/DM TransformerAbs](https://drive.google.com/open?id=1yLCqT__ilQ3mf5YUUCw9-UToesX5Roxy)

[XSum BertExtAbs](https://drive.google.com/open?id=1H50fClyTkNprWJNh10HWdGEdDdQIkzsI)

##Installation

This project needs Python3.6

Clone this repo:
```
git clone https://github.com/elkd/summrz.git
```

```
pip install -r requirements.txt
```

Copy the downloaded models to the folder ./models/
You should also downlaod the BERT CNN and Daily Mail data then store here ./bert_data_new/cnndm/
[Pre-processed data](https://drive.google.com/open?id=1DN7ClZCCXsk2KegmC6t4ClBwtAf5galI)
unzip the zipfile and put all `.pt` files into folder.

Then run:
```
python manage.py runserver
```

Then open the browser and access http://127.0.0.1:8000

Fill in a sample text and summarize. The models doesn't do well on very long texts like a whole article. In that case it's better to split the text into batches.
You can check my implementation on the default view [here](https://github.com/elkd/summrz/blob/master/client/views.py#L159)
Also you can change the default options of the models [here](https://github.com/elkd/summrz/blob/master/client/views.py#L33)
