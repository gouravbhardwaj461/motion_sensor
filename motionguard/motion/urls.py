from django.urls import path
from . import views
from django.shortcuts import redirect


urlpatterns = [
    path('', lambda request:  redirect('dashboard'), name='home_redirect'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('start-camera/', views.start_camera, name='start_camera'),
    path('stop-camera/', views.stop_camera, name='stop_camera'),
    path('camera-status/', views.camera_status, name='camera_status'),
    path('video_feed/', views.video_feed, name='video_feed'),
    path('remote-camera-qr/', views.remote_camera_qr, name='remote_camera_qr'),
    path('cam/', views.phone_camera, name='phone_camera'),
    path('receive_frame/', views.receive_frame, name='receive_frame'),

]
