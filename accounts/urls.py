from django.urls import path
from . import views


urlpatterns = [
    path('signup/', views.SingUp.as_view(), name='signup'),
]
