from django.shortcuts import render, redirect, get_object_or_404
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser
from django.contrib.auth.models import Group
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from shop.models import Product
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView, DeleteView


def signupView(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            signup_user = CustomUser.objects.get(username=username)
            customer_group = Group.objects.get(name='Customer')
            customer_group.user_set.add(signup_user)
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html',{'form':form})

def signinView(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username = username, password = password)
            if user is not None:
                login(request, user)
                return redirect('shop:allProdCat')
            else:
                return redirect('accounts:signup')
    else:
        form =AuthenticationForm()
    return render(request, 'signin.html', {'form':form })


def signoutView(request):
    logout(request)
    return redirect('accounts:signin')

# Dashboard Code
def dashboard_view(request):
    return render(request, 'dashboard.html')



# Profile Code
def view_profile(request):
    args = {'user': request.user}
    return render(request, 'profile.html', args)

def edit_profile(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance = request.user)

        if form.is_valid():
            form.save()
            return redirect('accounts:view_profile')

    else:
        form = CustomUserChangeForm(instance = request.user)
        args = {'form': form}
        return render(request, 'edit_profile.html', args)

# Password Change Code

def changePassword(request):
    if request.method == 'POST':
        form = PasswordChangeForm(data = request.POST, user = request.user)

        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            return redirect('accounts:view_profile')
        else:
            return redirect('accounts:change_password')
    else:
        form = PasswordChangeForm(user = request.user)

        args = {'form':form}
        return render(request, 'change_password.html', args)


# Wish-list code:
@login_required(login_url = 'accounts:signin' )
def wishlist(request):
    products = Product.objects.filter(user_wishlist = request.user)
    return render(request, 'user_wishlist.html', {'wishlist':products})

@login_required(login_url = 'accounts:signin' )
def add_to_wishlist(request, product_id):
    product = Product.objects.get(id=product_id)
    if product.user_wishlist.filter(id=request.user.id).exists():
        product.user_wishlist.remove(request.user)
    else:
        product.user_wishlist.add(request.user)
        messages.success(request, "Added " + product.name + " to your WishList")
    return HttpResponseRedirect(request.META['HTTP_REFERER'])