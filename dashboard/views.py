from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from .models import Transactions, Users, Timelogs,NewSystemUser
from .forms import RawUserForm,RawTransactionForm,RawTimelogsForm,NewSignIn,ChargeEquity,CreateNewSystemUser
from . import views
from django.urls import path
from django.contrib.auth import logout,login, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.models import User, Permission
import datetime
from datetime import timedelta

## add permission mixins
def dashboard(request):
    obj = Timelogs.objects.filter(endTime__isnull = True)
    recents = Timelogs.objects.all()
    # for recent in recents:
    #     elapsedTime = recent.endTime - recent.startTime
    #     # minutes = divmod(elapsedTime, 60)[0]
    #     print(f" time elapsed for {recent.person}={elapsedTime}")
    my_form = NewSignIn()
    transaction_form = ChargeEquity()
    if request.method == "POST":
        my_form = NewSignIn(request.POST)
        transaction_form = ChargeEquity(request.POST)
        if my_form.is_valid():
            print(my_form.cleaned_data)
            Timelogs.objects.create(**my_form.cleaned_data)
            return HttpResponseRedirect("dashboard")
        if transaction_form.is_valid():
            print(transaction_form.cleaned_data)
            Transactions.objects.create(**my_form.cleaned_data)
            return HttpResponseRedirect("dashboard")
    args = { 'dashboard_page': "active","form": my_form,'obj':obj,"transaction_form": transaction_form}
    return render(request,'dashboard.html',args)

def loginPage(request):
    return render(request,'index.html')

def logout(request):
    logout(request)
    messages.info(request,"logged out successfully!")
    return HttpResponseRedirect("/dashboard")

def people_create_view(request):
    my_form = RawUserForm()
    if request.method == "POST":
        my_form = RawUserForm(request.POST)
        if my_form.is_valid():
            print(my_form.cleaned_data)
            Users.objects.create(**my_form.cleaned_data)
            return HttpResponseRedirect("/people")

    context = {"form":my_form}
    return render(request,'people_create.html',context)

def transaction_create_view(request):
    my_form = RawTransactionForm()
    if request.method == "POST":
        my_form = RawTransactionForm(request.POST)
        if my_form.is_valid():
            print(my_form.cleaned_data)
            Transactions.objects.create(**my_form.cleaned_data)
            return HttpResponseRedirect("new")
    context = {"form":my_form}
    return render(request,'transaction_create.html',context)

def timelogs_create_view(request):
    my_form = RawTimelogsForm()
    if request.method == "POST":
        my_form = RawTimelogsForm(request.POST)
        if my_form.is_valid():
            print(my_form.cleaned_data)
            Timelogs.objects.create(**my_form.cleaned_data)
            my_form = RawTimelogsForm()
            return HttpResponseRedirect("new")
    context = {"form":my_form}
    return render(request,'timelogs_create.html',context)
        
def people(request):
    obj = Users.objects.all()
    args = { 'obj': obj,'people_page': "active"}
    return render(request,'people.html',args)

def timelogs(request):
    obj = Timelogs.objects.all()
    args = { 'obj': obj,'timelogs_page': "active"}
    return render(request,'timelogs.html',args)

def transactions(request):
    obj = Transactions.objects.all()
    args = { 'obj': obj,'transactions_page': "active"}
    return render(request,'transactions.html',args)

def users(request):
    django_users = User.objects.all()
    obj = NewSystemUser.objects.all()
    my_form = CreateNewSystemUser()
    if request.method == "POST":
        my_form = CreateNewSystemUser(request.POST)
        if my_form.is_valid():
            username = my_form.cleaned_data.get('username')
            email = my_form.cleaned_data.get('email')
            password = my_form.cleaned_data.get('password')
            role = my_form.cleaned_data.get('role')
            print(role)
            user = User.objects.create_user(username,email,password)
            user.first_name = role
            user.save()
            # NewSystemUser.objects.create(**my_form.cleaned_data)
            my_form = CreateNewSystemUser()
            return HttpResponseRedirect("users")
    args = { 'obj': django_users,'users_page': "active","form":my_form}
    return render(request,'users.html',args)

def signout(request,id):
    print(f"trying for id {id}")
    obj = Timelogs.objects.get(pk=id)
    if request.method == "POST":
        print(f'current obj endTime {obj.endTime}')
        obj.endTime = datetime.datetime.now()
        obj.save()
        print(f'new obj endTime {obj.endTime}')
        return HttpResponseRedirect('/dashboard')
        print("should be done by now")
    return HttpResponseRedirect('/dashboard')


