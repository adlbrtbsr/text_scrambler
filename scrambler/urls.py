from django.urls import path
from . import views


urlpatterns = [
    path('', views.upload_view, name='upload'),
    path('result/', views.result_view, name='result'),
]


