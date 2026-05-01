from django import urls
from django.urls import path
from .views import camera_phones_view, gaming_phones_view, performance_view

urlpatterns = [
    path('camera-phones/', camera_phones_view, name='camera_phones'),
    path('gaming-phones/', gaming_phones_view, name='gaming_phones'),
    path('performance/', performance_view, name='performance'),

]

