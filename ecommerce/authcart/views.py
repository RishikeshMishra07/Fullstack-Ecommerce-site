from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from .utils import TokenGenerator, generate_token
from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError
from django.core.mail import EmailMessage
from django.conf import settings
from django.views.generic import View
from django.contrib.auth.tokens import PasswordResetTokenGenerator


# Create your views here.
def signup(request):
    if request.method=="POST":
        username=request.POST['username']
        email=request.POST['email']
        password=request.POST['pass1']
        confirm_password=request.POST['pass2']
        if password!=confirm_password:
            messages.warning(request,"Password in Not Matching")
            # return HttpResponse("password is not matching")
            return render (request,"signup.html")
        
        if User.objects.filter(email=email).exists():
            messages.info(request, "Email is already in use")
            return render(request, 'signup.html')
        
        if User.objects.filter(username=username).exists():
            messages.info(request, "Username is already in use")
            return render(request, 'signup.html')

        try:
            if User.objects.get(email=email):
                 messages.info (request,"Email is Already exists")
                # return HttpResponse("email already exits")
                # return render (request,'auth/signup.html')
        
        except Exception as identifier:
            pass

        user=User.objects.create_user(username=username,email=email,password=password)
        user.is_active=False
        user.save()
        email_subject="Activation Your Account"
        message=render_to_string('activate.html',{
            'user':user,
            'domain':'127.0.0.1:8000',
            'uid':urlsafe_base64_encode(force_bytes(user.pk)),
            'token':generate_token.make_token(user)
        })

        # email_message = EmailMessage(email_subject, message, settings.EMAIL_HOST_USER, [email],)
        # email_message.send()
        messages.success(request,f"Activate your account ny clicking the link in your gmail {message}")
        return redirect('/auth/login/')

        # return HttpResponse("User created",email)
    return render(request,"signup.html")      

class AactivateAccountView(View):
    def get(self,request,uidb64,token):
        try:
            uid=force_str(urlsafe_base64_decode(uidb64))
            user=User.objects.get(pk=uid)
        except Exception as identifier:
            user=None
        if user is not None and generate_token.check_token(user,token):
            user.is_active=True
            user.save()
            messages.info(request,"Account Activated Succeccfully")
            return redirect('/auth/login')
        return render(request,'activatefail.html')
        




def handlelogin(request):
    if  request.method=="POST":
        # email=request.POST['email']
        username=request.POST['username']
        userpassword=request.POST['pass1']
        myuser=authenticate(username=username,password=userpassword)

        if myuser is not None:
            login(request,myuser)
            messages.success(request,"Login Success")
            return redirect('/')
        else:
            messages.error(request,"Invalid Credentials")
            return redirect('/auth/login')
        
    return render (request,"login.html")


def handlelogout(request):
    logout(request)
    messages.info(request,"Logout Success")
    return redirect('/auth/login')


class RequestResetEmailView(View):
    def get(self,request):
        return render(request,'request-reset-email.html')
    
    def post(self,request):
        email=request.POST['email']
        user=User.objects.filter(email=email)

        if user.exists():
            # current_site=get_current_site(request)
            email_subject='[Reset Your Password]'
            message=render_to_string('reset-user-password.html',{
                'domain':'127.0.0.1:8000',
                'uid':urlsafe_base64_encode(force_bytes(user[0].pk)),
                'token':PasswordResetTokenGenerator().make_token(user[0])

            })
            # email_message=EmailMessage(email_subject,message,settings.EMAIL_HOST_USER,[email])
            # email_message.send()
            messages.info(request, f"WE HAVE SENT YOU AN EMAIL WITH INSTRUCTIONS ON HOW TO RESET PASSWORD {message}")

            return render(request,'request-reset-email.html')
        
class SetNewPasswordView(View):
    def get(self,request,uidb64,token):
        context={
            'uidb64':uidb64,
            'token':token,
        }
        try:
            user_id=force_str(urlsafe_base64_decode(uidb64))
            user=User.objects.get(pk=user_id)

            if not PasswordResetTokenGenerator().check_token(user,token):
                messages.warning(request,"Password Reset Link is Invalid")
                return render(request,'request-reset-email.html')
        except DjangoUnicodeDecodeError as identifier:
            pass
        return render(request,'set-password.html',context)
    
    def post(self,request,uidb64,token):
        context={
            'uidb64':uidb64,
            'token':token,
        }
        password=request.POST['pass1']
        confirm_password=request.POST['pass2']
        if password != confirm_password:
            messages.warning(request,"Password is not Matched")
            return render(request,'set-password.html',context)
        
        try:
            user_id=force_str(urlsafe_base64_decode(uidb64))
            user=User.objects.get(pk=user_id)
            user.set_password(password)
            user.save()
            messages.success(request,"Password Reset Successfull")
            return redirect('/auth/login')
        

        except DjangoUnicodeDecodeError as identifier:
            messages.error(request,"something Went Wrong")
            return render(request,'set-password.html',context)
        return render(request,'set-password.html',context)
        