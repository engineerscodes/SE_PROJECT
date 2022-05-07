import re
import threading

from django.contrib import messages
from django.contrib.auth.models import auth, User, Group
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_text, force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from .Token_Gen import Token_generator


# Email Class
class THREADEMAIL(threading.Thread):
    def __init__(self, message, email, cap):
        self.message = message
        self.email = email
        self.cap = cap
        threading.Thread.__init__(self)

    # send email on a different thread
    def run(self):
        send_mail(
            self.cap,
            self.message,
            'naveennoob95@gmail.com',
            [self.email],
            fail_silently=False,

        )


# login function
def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    if request.method == 'POST':
        username = request.POST['user-name']
        Password = request.POST['passwordcnf']

        User = auth.authenticate(username=username, password=Password)

        if User is not None:
            if User.is_active == False:
                return HttpResponse("<h1> Verify Mail </h1>")
            else:
                auth.login(request, User)
                return redirect('/')

        else:
            messages.info(request, "Invalid Username  or Password ")
            return redirect('/account/login')


# create new account
def reg(request):
    if request.method == 'GET':
        return render(request, 'reg.html')
    if request.method == 'POST':

        userName = request.POST['names']
        password = request.POST['password_cfn']
        email = request.POST['emails'].lower()

        if re.search('^[a-zA-z]+\.[0-9a-zA-Z]+@vitap\.ac\.in$', email) is None:
            messages.info(request, "USE VITAP MAIL ONLY ")
            return redirect('/account/reg/')
        if len(password) < 8:
            messages.info(request, 'Password should be minimum 8 characters')
            return redirect('/account/reg/')

        if User.objects.filter(username=userName).exists():
            messages.info(request, " UserName is not Available")
            return redirect('/account/reg/')
        if User.objects.filter(email=email).exists():
            messages.info(request, " MAIL IS ALREADY REG")
            return redirect('/account/reg/')
        if re.search('^[a-zA-z]+\.[0-9a-zA-Z]+@vitap\.ac\.in$', email) is not None and User.objects.filter(
                username=userName).exists() == False:
            user = User.objects.create_user(username=userName, password=password, email=email)
            user.is_active = False
            user.save()
            group = Group.objects.get(name='members')
            user.groups.add(group)
            # PasswordResetTokenGenerator use it to verfiy and create token also
            Useract_token = Token_generator()
            message = render_to_string('activate.html',
                                       {
                                           'user': user,
                                           'domain': get_current_site(request),
                                           'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                                           'TOKEN': Useract_token.make_token(user)

                                       }
                                       )
            ''' send_mail(
                                   'THANKS FOR REG',
                                   message,
                                   'naveennoob95@gmail.com',
                                   [email],
                                   fail_silently=False,
                )'''

            THREADEMAIL(message, email, 'THANKS FOR REG').start()
            messages.info(request, " plz verify your email ")
            return redirect('/account/reg/')


# check verfication url for new user
def AUTHUSERNAME(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception as identifier:
        user = None
    Useract_token = Token_generator()
    if user is not None and Useract_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.info(request, "VERIFIED USER PLZ LOGIN ")
        return redirect('/account/login')
    # if url is wrong
    return render(request, 'auth_failed.html', status=401)


# logout function
def logout(request):
    auth.logout(request)

    return redirect('/account/login')


# reste password function
def resetPassword(request):
    if request.method == 'GET':
        return render(request, 'resetpass.html', status=200)
    if request.method == 'POST':
        email = request.POST['email'].lower()
        uname = request.POST['uname']

        try:
            user = User.objects.get(username=uname, email=email)
            Useract_token = Token_generator()
            message = render_to_string('resend.html',
                                       {
                                           'user': user,
                                           # 'domain': get_current_site(request),
                                           'domain': "3.108.66.53",
                                           'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                                           'TOKEN': Useract_token.make_token(user)

                                       }
                                       )
            THREADEMAIL(message, email, 'PASSWORD RESET ').start()  # start new thread
            messages.info(request, "Check YOUR MAIL BOX !")
            return render(request, 'success.html', status=200)
        except Exception as e:  # if sending email failed
            messages.info(request, "Try again later !")
            return render(request, 'auth_failed.html', status=401)


# verify reset password link send to user email
def vali_reset_pass(request, uidb64, token):
    if request.method == 'GET':
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            Useract_token = Token_generator()
            check_token = Useract_token.check_token(user, token)
            if user is not None and check_token:

                return render(request, 'changepass.html', status=200)
            else:
                messages.info(request, 'SOMETHING IS WRONG PLZ CHECK YOUR TOKEN !')
                return render(request, 'auth_failed.html', status=401)
        except Exception as identifier:  # user token is not valid and user is not found
            messages.info(request, "User Doesn't EXIST")
            return render(request, 'auth_failed.html', status=401)

    if request.method == 'POST':  # check password and update it

        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            Useract_token = Token_generator()
            check_token = Useract_token.check_token(user, token)
            if request.POST['pass'] != request.POST['pass2'] or len(request.POST['pass']) < 8:
                messages.info(request, 'Invalid Password plz check !')
                return render(request, 'auth_failed.html', status=401)
            if user is not None and check_token and len(request.POST['pass']) > 8:
                user.set_password(request.POST['pass'])
                user.save()
                messages.info(request, 'PassWord Updated ! login next ')
                return render(request, 'success.html', status=200)
            else:
                messages.info(request, 'SOMETHING IS WRONG PLZ CHECK YOUR TOKEN !')
                return render(request, 'auth_failed.html', status=401)
        except Exception as identifier:
            messages.info(request, "User Doesn't EXIST")
            return render(request, 'auth_failed.html', status=401)
