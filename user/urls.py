from django.urls import path

from user import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('forgot_password/', views.forgot_password, name="forgot_password"),
    path('reset_password/', views.reset_password, name="reset_password"),
    path('send_reset_email/', views.send_reset_email, name="send_reset_email"),
    path('profile/', views.user_profile, name="user_profile"),
]
