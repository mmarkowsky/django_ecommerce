from itertools import product
from operator import index
from django.shortcuts import redirect, render
from accounts.forms import RegistrationForm
from accounts.models import Account
from django.contrib import messages,auth
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.core.mail import EmailMessage
from carts.views import _cart_id
from carts.models import Cart, CartItem

def register(request):
    form = RegistrationForm()
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            phone_number = form.cleaned_data["phone_number"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            username = email.split("@")[0]
            user = Account.objects.create_user(first_name=first_name, last_name=last_name,email=email,username=username,password=password)
            user.phone_number = phone_number
            user.save()

            current_site = get_current_site(request)
            mail_subject = "Por favor ative a sua conta"
            body = render_to_string("accounts/account_verification_email.html",{
                "user": user,
                "domain": current_site,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": default_token_generator.make_token(user),
            })

            to_email = email
            send_email = EmailMessage(mail_subject,body,to=[to_email])
            send_email.send()

            #messages.success(request, "Usuario salvo com sucesso")
            return redirect("/accounts/login/?command=verification&email="+email)

    context = {
        "form": form
    }
    return render(request, "accounts/register.html", context)


def login(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)

        if user is not None:

            try:
                cart_id = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_items_exists = CartItem.objects.filter(cart=cart_id).exists()
                if is_cart_items_exists:
                    cart_item = CartItem.objects.filter(cart=cart_id)

                    product_variation = []
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation))

                    cart_item = CartItem.objects.filter(user=user)
                    ex_var_list = []
                    id = []
                    for item in cart_item:
                        existing_variation = item.variations.all()
                        ex_var_list.append(list(existing_variation))
                        id.append(item.id)

                    for pr in product_variation:
                        if pr in ex_var_list:
                            index = ex_var_list.index(pr)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity +=1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart_id)
                            for item in cart_item:
                                item.user = user
                                item.save()
            except:
                pass

            auth.login(request,user)
            messages.success(request,"Login feito com sucesso")
            return redirect("dashboard")

        else:
            messages.error(request,"Usuario não existente")
            return redirect("login")

    return render(request, "accounts/login.html")


@login_required(login_url="login")
def logout(request):
    auth.logout(request)
    messages.success(request, "Saiu da sua sessão!")
    return redirect("login")


def activate(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError,OverflowError,Account.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user,token):
        user.is_active = True
        user.save()
        messages.success(request, "A conta foi ativada")
        return redirect('login')
    else:
        messages.error(request, "Ocorreu um problema na ativação da conta")
        return redirect('register')

@login_required(login_url='login')
def dashboard(request):
    return render(request, "accounts/dashboard.html")

def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            current_site = get_current_site(request)
            mail_subject = 'Reset da senha'
            body = render_to_string('accounts/reset_password_email.html',{
                "user":user,
                "domain": current_site,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": default_token_generator.make_token(user),
            })

            to_email = email
            send_email = EmailMessage(mail_subject, body, to=[to_email])
            send_email.send()

            messages.success(request, "Email enviado para o reset da sua senha")
            return redirect("login")
        else:
            messages.error(request, "Não foi possivel enviar o correio para reset da sua senha. Tente de novo por favor!")
            return redirect("forgotPassword")

    return render(request, "accounts/forgotPassword.html")


def reset_password_validate(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user =None
    
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request,"Por favor faça o reset da sua senha")
        return redirect("reset_password")
    else:
        messages.error(request, "O link está expirado")
        return redirect("login")


def reset_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session['uid']
            user = Account.objects.get(pk= uid)
            user.set_password(password)
            user.save()
            messages.success(request,"A senha foi trocada")
            return redirect("login")
        else:
            messages.error(request, "A senha e a confirmação tem que ser iguais")
            return redirect("resetPassword")
    else:
        return render(request, "accounts/reset_password.html")

