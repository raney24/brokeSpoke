from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from .models import Transactions, Users, Timelogs, NewSystemUser
from .forms import RawUserForm, RawTransactionForm, RawTimelogsForm, NewSignIn, ChargeEquity, CreateNewSystemUser
from . import views
from django.urls import path
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.models import User, Permission
import pytz
import datetime
from datetime import timezone, timedelta
from django.contrib.auth.decorators import login_required



# add permission mixins
@login_required(login_url='/')
def dashboard(request):
    obj = Timelogs.objects.filter(endTime__isnull=True)
    recents = Timelogs.objects.filter(endTime__isnull=False)
    maxObject = timedelta(days=0, hours=3, minutes=0)
    dictOfRecents = []
    for recent in recents:
        elapsedTime = datetime.datetime.now(timezone.utc) - recent.endTime
        if maxObject > elapsedTime:
            dictOfRecents.append(recent)
            # print("printing")
            # print(f" time elapsed for {recent.person}={elapsedTime}")
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
    args = {'dashboard_page': "active", "form": my_form, 'obj': obj,
            "transaction_form": transaction_form, "recents": dictOfRecents}
    return render(request, 'dashboard.html', args)


def loginPage(request):
    return render(request, 'index.html')


def logout_request(request):
    print("gonna log out now")
    logout(request)
    return HttpResponseRedirect("/")


def people_create_view(request):
    my_form = RawUserForm()
    if request.method == "POST":
        my_form = RawUserForm(request.POST)
        if my_form.is_valid():
            print(my_form.cleaned_data)
            Users.objects.create(**my_form.cleaned_data)
            return HttpResponseRedirect("/people")

    context = {"form": my_form}
    return render(request, 'people_create.html', context)


def transaction_create_view(request):
    my_form = RawTransactionForm()
    if request.method == "POST":
        my_form = RawTransactionForm(request.POST)
        if my_form.is_valid():
            print(my_form.cleaned_data)
            Transactions.objects.create(**my_form.cleaned_data)
            return HttpResponseRedirect("new")
    context = {"form": my_form}
    return render(request, 'transaction_create.html', context)


def timelogs_create_view(request):
    my_form = RawTimelogsForm()
    if request.method == "POST":
        my_form = RawTimelogsForm(request.POST)
        if my_form.is_valid():
            print(my_form.cleaned_data)
            Timelogs.objects.create(**my_form.cleaned_data)
            my_form = RawTimelogsForm()
            return HttpResponseRedirect("new")
    context = {"form": my_form}
    return render(request, 'timelogs_create.html', context)


def people(request):
    obj = Users.objects.all()
    args = {'obj': obj, 'people_page': "active"}
    return render(request, 'people.html', args)


def timelogs(request):
    obj = Timelogs.objects.all()
    args = {'obj': obj, 'timelogs_page': "active"}
    return render(request, 'timelogs.html', args)


def transactions(request):
    obj = Transactions.objects.all()
    args = {'obj': obj, 'transactions_page': "active"}
    return render(request, 'transactions.html', args)


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
            user = User.objects.create_user(username, email, password)
            user.first_name = role
            user.save()
            # NewSystemUser.objects.create(**my_form.cleaned_data)
            my_form = CreateNewSystemUser()
            return HttpResponseRedirect("users")
    args = {'obj': django_users, 'users_page': "active", "form": my_form}
    return render(request, 'users.html', args)


def signout(request, id):
    print(f"trying for id {id}")
    obj = Timelogs.objects.get(pk=id)
    targetid = obj.users_id
    equity = Users.objects.get(pk=targetid)
    if request.method == "POST":
        print(f'current obj endTime {obj.endTime}')
        obj.endTime = datetime.datetime.now()
        equity.equity = 4
        equity.save()
        obj.save()
        print(f'new obj endTime {obj.endTime}')
        return HttpResponseRedirect('/dashboard')
        print("should be done by now")
    return HttpResponseRedirect('/dashboard')


def delete_request(request, id):
    if request.method == "POST":
        print(f"trying for id {id}")
        obj = Timelogs.objects.filter(id=id)
        obj.delete()
        print("object deleted")
        return HttpResponseRedirect('/dashboard')

    return HttpResponseRedirect('/dashboard')


def transactions_edit(request, id):
    my_form = RawTransactionForm()
    if request.method == "POST":
        my_form = RawTransactionForm(request.POST)
        obj = Transactions.objects.get(id=id)
        if my_form.is_valid():
            print(my_form.cleaned_data)
            obj.date = my_form.cleaned_data.get('date')
            obj.person = my_form.cleaned_data.get('person')
            obj.transactionType = my_form.cleaned_data.get('transactionType')
            obj.amount = my_form.cleaned_data.get('amount')
            obj.paymentType = my_form.cleaned_data.get('paymentType')
            obj.paymentStatus = my_form.cleaned_data.get('paymentStatus')
            obj.save()
            print("updated forms")
            # Transactions.objects.create(**my_form.cleaned_data)
            return HttpResponseRedirect("/transactions")
        else:
            print("failed")
    context = {"form": my_form}
    return render(request, 'transactions_edit.html', context)


def timelogs_edit(request, id):
    my_form = RawTimelogsForm()
    if request.method == "POST":
        my_form = RawTimelogsForm(request.POST)
        obj = Timelogs.objects.get(id=id)
        if my_form.is_valid():
            print(my_form.cleaned_data)
            obj.person = my_form.cleaned_data.get('person')
            obj.activity = my_form.cleaned_data.get('activity')
            obj.startTime = my_form.cleaned_data.get('startTime')
            obj.endTime = my_form.cleaned_data.get('endTime')
            obj.save()
            print("updated forms")
            # Transactions.objects.create(**my_form.cleaned_data)
            return HttpResponseRedirect("/timelogs")
        else:
            print("failed")
    context = {"form": my_form}
    return render(request, 'timelogs_edit.html', context)

def people_edit(request, id):
    my_form = RawUserForm()
    obj = Users.objects.get(id=id)
    targetid = obj.id
    timelogs = Timelogs.objects.filter(users_id=targetid)
    transactions = Transactions.objects.filter(users_id=targetid)
    if request.method == "POST":
        my_form = RawUserForm(request.POST)
        
        if my_form.is_valid():
            print(my_form.cleaned_data)
            obj.lastname  = my_form.cleaned_data.get('lastname')
            obj.firstname = my_form.cleaned_data.get('firstname')
            obj.middlename = my_form.cleaned_data.get('middlename')
            obj.waiverAcceptedDate = my_form.cleaned_data.get('waiverAcceptedDate')
            obj.birthdate = my_form.cleaned_data.get('birthdate')
            obj.membershipExp = my_form.cleaned_data.get('membershipExp')
            obj.email = my_form.cleaned_data.get('email')
            obj.phone = my_form.cleaned_data.get('phone')
            obj.emergencyName = my_form.cleaned_data.get('emergencyName')
            obj.relation = my_form.cleaned_data.get('relation')
            obj.emergencyPhone = my_form.cleaned_data.get('emergencyPhone')
            obj.save()
            print("updated forms")
            return HttpResponseRedirect("/people")
        else:
            print("failed")
    context = {"form": my_form, 'person':obj, 'transactions':transactions,'timelogs':timelogs}
    return render(request, 'people_edit.html', context)

def transaction_delete_request(request, id):
    if request.method == "POST":
        print(f"trying for id {id}")
        obj = Transactions.objects.filter(id=id)
        obj.delete()
        print("object deleted")
        return HttpResponseRedirect('/transactions')

    return HttpResponseRedirect('/transactions')
def user_delete_request(request, id):
    if request.method == "POST":
        print(f"trying for id {id}")
        obj = Users.objects.filter(id=id)
        obj.delete()
        print("object deleted")
        return HttpResponseRedirect('/people')

    return HttpResponseRedirect('/people')

def search_request(request):
    if request.method == 'POST':
        search_text == request.POST['search_text']
    else:
        search_text = ''
    users = User.object.filter(lastname__contains=search_text)

    return render(request,'ajax_search.html', {'users':users})
