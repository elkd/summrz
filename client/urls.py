from django.urls import path
from django.views.generic import TemplateView
from client import views


urlpatterns = [
    path('', views.index, name='index'),
    path('summarize_page', views.summarize_page, name='summarize_page'),
    path('save_summary', views.save_summary, name='save_summary'),
    path('about', views.history, name='about'),
    path('history', views.history, name='history'),
    path('history_topic', views.history_topic, name='history_topic'),
]
