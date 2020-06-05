from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from .models import EquityRates, Transactions, Users, Timelogs, NewSystemUser
from .forms import ChangeEquityRates, RawUserForm, RawTransactionForm, RawTimelogsForm, NewSignIn, ChargeEquity, CreateNewSystemUser
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
from django.core import serializers
import csv
from django.db.models import F





# add permission mixins
@login_required(login_url='/')
def dashboard(request):
    local = pytz.timezone ("US/Eastern")
    obj = Timelogs.objects.filter(endTime__isnull=True)
    recents = Timelogs.objects.filter(endTime__isnull=False)
    maxObject = timedelta(days=0, hours=3, minutes=0)
    dictOfRecents = []
    for recent in recents:
        naive = datetime.datetime.strptime(recent.endTime, "%d/%m/%Y %I:%M %p")
        local_dt = local.localize(naive, is_dst=None)
        elapsedTime = datetime.datetime.now(timezone.utc) - local_dt
        if maxObject > elapsedTime:
            dictOfRecents.append(recent)
    my_form = NewSignIn()
    transaction_form = ChargeEquity()
    if request.method == "POST":
        my_form = NewSignIn(request.POST)
        transaction_form = ChargeEquity(request.POST)
        if my_form.is_valid():
            print(my_form.cleaned_data)
            person = my_form.cleaned_data['person']
            # lastname = my_form.cleaned_data['lastname']
            print(f"user is named {person}")
            Timelogs.objects.create(**my_form.cleaned_data)
            return HttpResponseRedirect("dashboard")
        if transaction_form.is_valid():
            print(transaction_form.cleaned_data)
            Transactions.objects.create(**transaction_form.cleaned_data)
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

def generate_email_request(request):
    print("gonna export to csv")

    output = []
    response = HttpResponse (content_type='text/csv')
    writer = csv.writer(response)
    query_set = Users.objects.all()
#Header
    writer.writerow(['First Name', 'Last Name', 'email'])
    for user in query_set:
        output.append([user.firstname, user.lastname, user.email])
#CSV Data
    writer.writerows(output)
    return response

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
    # Statement.objects.filter(id__in=statements).update(vote=F('vote') + 1)
# for updating the equity
    local = pytz.timezone ("US/Eastern")
    currentTime = datetime.datetime.now()
    print(f"trying for id {id}")
    obj = Timelogs.objects.get(pk=id)
    targetid = obj.users_id
    equity = Users.objects.get(pk=targetid)
    if request.method == "POST":
        print(f'current obj endTime {obj.endTime}')
        print(f'current obj startTime {obj.startTime}')
        # naiveStart = datetime.datetime.strptime(obj.startTime, "%d/%m/%Y %H:%M")
        # local_dt = local.localize(naiveStart, is_dst=None)
        naiveEnd = datetime.datetime.now()
        current_time = naiveEnd.strftime("%d/%m/%Y %I:%M %p")
        # endTime = datetime.datetime.strftime(naiveEnd, "%d/%m/%Y %H:%M")
        # local_dt = local.localize(naiveEnd, is_dst=None)
        # local_dt.
        # elapsedTime = naiveEnd - local_dt
        print(f"endTime = {str(current_time)}")
        obj.endTime = str(current_time)
        # print(f"elapsed time = {elapsedTime}")
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
            print("changing starttime")
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
def timelogs_delete_request(request, id):
    if request.method == "POST":
        print(f"trying for id {id}")
        obj = Timelogs.objects.filter(id=id)
        obj.delete()
        print("object deleted")
        return HttpResponseRedirect('/timelogs')

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
    print("in function")
    if request.method == 'GET':
        search_request = request.GET.get('search_query')
        if search_request != '':
            print(f"searchtext in if = {search_request}")
            users = Users.objects.filter(lastname__contains=search_request).values('firstname','lastname')
            if not users:
                userList = ['no persons found']
            else:
                userList = list(users)
        else:
            userList = ['Enter Last name']
        print(userList)
        return JsonResponse(userList, safe=False)

def validate_request(request):
    print("validating")
    if request.method == 'GET':
        validation_first = request.GET.get('first_name')
        validation_last = request.GET.get('last_name')
        if validation_first != '' and validation_last != '':
            users = Users.objects.filter(lastname__contains=validation_last, firstname__contains=validation_first).values('id')
            if not users:
                userList = ['no persons found']
            else:
                userList = list(users)
        else:
            userList = ['Enter Last name']
        print("returning userlist" + str(userList))
        return JsonResponse(userList, safe=False)

def charts(request):
    rates = EquityRates.objects.all()
    my_form = ChangeEquityRates()
    if request.method == 'POST':
        my_form = ChangeEquityRates(request.POST)
        if my_form.is_valid():
            rates.sweatEquity = my_form.cleaned_data.get('username')
            rates.volunteerTime = my_form.cleaned_data.get()

    args = {
        'charts_page': "active"
    }
    # context = {"form": my_form}
    return render(request, 'charts.html',args)