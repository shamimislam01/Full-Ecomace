from django.urls import path
from . import views


# app_name = 'account'
urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.profile_view, name='dashboard'),
    path('my_orders/', views.my_orders_view, name='my_orders'),
    path('order/<int:order_id>/', views.order_detail_view, name='order_detail'),
    # path('update_profile/', views.update_profile_view, name='update_profile'),
    # path('update_password/', views.update_password_view, name='update_password'),
    path('verify/', views.verify_view, name='verify'),
    # path('resend_verification/', views.resend_verification_view, name='resend_verification'),
    path('reset/', views.password_reset_request, name='password_reset_request'),
    path('reset/verify/', views.password_reset_verify, name='password_reset_verify'),
    path('reset/confirm/', views.password_reset_confirm, name='password_reset_confirm'),
    path('account-settings/', views.account_settings_view, name='account_settings'),
    path('update_profile/', views.update_profile_view, name='update_profile'),
    path('update_password/', views.update_password_view, name='update_password'),
    path('update_address/', views.update_address_view, name='update_address'),
    path('track_order/', views.track_order_view, name='track_order'),

    # path('password_reset_confirm/<str:token>/', views.password_reset_confirm_view, name='password_reset_confirm'),
]