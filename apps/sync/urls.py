from django.urls import path
from . import views

app_name = "sync"
urlpatterns = [
    path('senaite', views.SyncSenaiteView.as_view(), name='senaite'),
    path('progress', views.SyncProgressView.as_view(), name='progress')
]