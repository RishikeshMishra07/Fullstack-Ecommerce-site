from django.urls import path
from authcart import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.handlelogin, name='handlelogin'),
    path('logout/', views.handlelogout, name='handlelogout'),
    path('activate/<uidb64>/<token>', views.AactivateAccountView.as_view(), name='activate'),
    path('request-reset-email/', views.RequestResetEmailView.as_view(), name='request-reset-email'),
    path('set-password/<uidb64>/<token>', views.SetNewPasswordView.as_view(), name='set-password'),
    

]