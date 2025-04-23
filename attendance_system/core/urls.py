#not included in package

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Authentication
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('redirect/', views.redirect_after_login, name='redirect_after_login'),

    # Common
    path('', views.home, name='home'),

    # Member
    path('member/home/', views.member_home, name='member_home'),
    path('member/qr-code/', views.member_qr_code, name='member_qr_code'),
    path('member/attendance-stats/', views.member_attendance_stats, name='member_attendance_stats'),
    
    # Admin
    path('admin/home/', views.admin_home, name='admin_home'),
    path('admin/create-event/', views.create_event, name='create_event'),
    path('admin/event/<int:event_id>/attendees/', views.event_attendees, name='event_attendees'),
    path('admin/event/<int:event_id>/scan/', views.scan_qr_code, name='scan_qr_code'),
    path('admin/reports/', views.admin_reports, name='admin_reports'),
]