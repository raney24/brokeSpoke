from getpass import getuser
from json.encoder import py_encode_basestring
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from .models import EquityRates, Transactions, Users, Timelogs, NewSystemUser
from .forms import ShiftsInRangeReport,UserReport,HoursReport, LoginReport,ChangeEquityRates, RawUserForm, RawTransactionForm, RawTimelogsForm, NewSignIn, ChargeEquity, CreateNewSystemUser, ChangeEquityValue
from . import views
import json
from django.urls import path
from django.contrib.auth import logout, login, authenticate 
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.models import User, Permission
import pytz
import datetime
from datetime import timedelta, tzinfo
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.core import serializers
import csv
from django.db.models import F,Q, UniqueConstraint
import xlwt
from django.db.models import Sum
from dateutil import relativedelta
from dateutil.rrule import rrule, MONTHLY
import dateutil.parser
from django.db.models import Count
from collections import Counter
from operator import countOf
from django.core.paginator import Paginator


#Debugger
import pdb




def getUserID(person):
    uniqueID = person.replace(' ','').upper()
    allusers = Users.objects.all().values()
    userMap = {}
    for user in allusers:
        if user['middlename']!= ' ':
            userString = user['firstname'].replace(' ','')+user['middlename'].replace(' ','')+user['lastname'].replace(' ','')
        else:
            userString = user['firstname'].replace(' ','')+user['lastname'].replace(' ','')
        # print(f'prelim {userString}')
        # userString.join([i for i in userString.split() if i != ' '])
        userString = userString.upper()
        # print(f'userString {userString}')
        userMap.setdefault(userString,{'id':user['id'],'equity':user['equity']})
    if userMap[uniqueID]:
        print('found')
        userMapUser = userMap[uniqueID]
        user_id = userMapUser['id']
        print(f'userlist {userMapUser}')
    else:
        user_id = None
    return user_id
   # 
# redirectes to login if not valid
@login_required(login_url='/')
def dashboard(request):
    obj = Timelogs.objects.filter(endTime__isnull=True)
    # recents = Timelogs.objects.filter(endTime__isnull=False)
    dictOfPending = []
    wages = EquityRates.objects.get(pk=1)

    # get all timelogs between now and 3 hours ago
    recents = Timelogs.objects.filter(
        endTime__isnull=False,
        endTime__range=[timezone.now() - timedelta(hours=3), timezone.now()]
    ).order_by('startTime')
    # print(timezone.now() + timedelta(hours=999))
    # print(recents)


    pending_payments = Timelogs.objects.filter(
        paymentStatus='Pending',
        endTime__range=[timezone.now() - timedelta(hours=3), timezone.now()]
    )

    for recent in recents:
        wage = 0
        if recent.activity == 'Volunteering':
            wage=wages.sweatEquity
        elif recent.activity == 'Stand Time':
            wage= wages.standTime
        else:
            wage = 0
        # recent.duration_in_hours = "{:.2f}".format((recent.duration.seconds/60/60)) # convert to hours
        recent.balance = abs(int(wage*recent.duration.seconds/60/60))

        
        
    for pendingPayment in pending_payments:
        wage = 0
        if pendingPayment.activity == 'Volunteering':
            wage=wages.sweatEquity
        elif pendingPayment.activity == 'Stand Time':
            wage= wages.standTime
        else:
            wage = 0
        
        # pendingPayment.duration_in_hours = "{:.2f}".format((pendingPayment.duration.seconds/60/60)) # convert to hours
        pendingPayment.balance = abs(int(wage*pendingPayment.duration.seconds/60/60))

        dictOfPending.append(pendingPayment)
    my_form = NewSignIn()
    change_equity_form = ChangeEquityValue()
    transaction_form = ChargeEquity()
    
    if request.method == "POST":
        my_form = NewSignIn(request.POST)
        transaction_form = ChargeEquity(request.POST)
        change_equity_form = ChangeEquityValue(request.POST)
        if my_form.is_valid():
            print(my_form.cleaned_data)
            person = my_form.cleaned_data['person']
            personList = person.split()
            person_first = personList[0]
            person_middle = personList[1]
            person_last = personList[2]
            # print(f"this is the person signing in={person}")
            targetUser = Users.objects.get(lastname__iexact=person_last, firstname__iexact=person_first,middlename__iexact=person_middle)
            print(f"signing in user with id {targetUser.id}")
            my_form.cleaned_data['users_id'] = targetUser.id
            # print(f"the current foreignkey is {my_form.cleaned_data['users_id']}")
            dateToFormat = my_form.cleaned_data['startTime']
            cleanedDate = datetime.datetime.strftime(dateToFormat, "%m/%d/%Y %I:%M %p")
            unroundedTime = RoundTime(cleanedDate,my_form.cleaned_data['activity'])
            roundedTime = unroundedTime.roundTime()
            # print(f"this is the rounded time = {roundedTime}")
            my_form.cleaned_data['startTime'] = roundedTime
            # print(f"date is seen as {dateToFormat}")
            # print(f"date changed to  {roundedTime}")
            Timelogs.objects.create(**my_form.cleaned_data)
            targetUser.lastVisit = roundedTime
            targetUser.save()
            return HttpResponseRedirect("/dashboard")
        elif transaction_form.is_valid():
            dateToFormat = transaction_form.cleaned_data['date']
            cleanedDate = datetime.datetime.strftime(dateToFormat, "%m/%d/%Y %I:%M %p")
            transaction_form.cleaned_data['date'] = cleanedDate
            print(transaction_form.cleaned_data)
            person = transaction_form.cleaned_data['transactionPerson']
            user_id = getUserID(person)
            transaction_form.cleaned_data['paymentType'] = 'Sweat Equity'
            transaction_form.cleaned_data['paymentStatus'] = 'Complete'
            # print(f"this is the person signing in={person}")
            targetUser = Users.objects.get(id=user_id)
            # print(f"signing in user with id {targetUser.id}")
            if transaction_form.cleaned_data['transactionType'] == 'Volunteer Credit' or transaction_form.cleaned_data['transactionType'] == 'Imported Balance':
                newEquity = targetUser.equity + transaction_form.cleaned_data['amount']
                if newEquity > 250:
                    targetUser.equity = 250
                else:
                    targetUser.equity = newEquity
            elif transaction_form.cleaned_data['transactionType'] == 'Parts Purchase' or transaction_form.cleaned_data['transactionType'] == 'Bike Purchase' or transaction_form.cleaned_data['transactionType'] == 'Stand Time Purchase':
                if transaction_form.cleaned_data['paymentType'] == 'Sweat Equity':
                    targetUser.equity = targetUser.equity - transaction_form.cleaned_data['amount']
                else:
                    pass
            else:
                pass
            
            transaction_form.cleaned_data['users_id'] = targetUser.id
            targetUser.save()
            print(transaction_form.cleaned_data)
            Transactions.objects.create(**transaction_form.cleaned_data)
            return HttpResponseRedirect("/dashboard")
        elif change_equity_form.is_valid():
            print("Equity Form")
            
            print(f"Equity Form Data: {change_equity_form}")
            # person = change_equity_form.cleaned_data['person']
            # user_id = getUserID(person)
            # targetUser = Users.objects.get(id=user_id)
            # targetUser.equity = change_equity_form.cleaned_data['equity']
            # targetUser.save()
            return HttpResponseRedirect("/dashboard")

        else:
            print(my_form.errors)
    args = {'dashboard_page': "active", "form": my_form, 'obj': obj,
            "transaction_form": transaction_form, "change_equity_form": change_equity_form, "recents": recents,'pending':dictOfPending}
    return render(request, 'dashboard.html', args)


def transactions_complete(request,id):
    if request.method == "POST":
        print(f"this is the id{id}")
        timelog = Timelogs.objects.get(id=id)
        timelog.paymentStatus = 'Completed'
        timelog.save()
        return HttpResponseRedirect("/dashboard")
    return HttpResponseRedirect("/dashboard")



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

@login_required(login_url='/')
def people_create_view(request):
    my_form = RawUserForm()
    if request.method == "POST":
        my_form = RawUserForm(request.POST)
        if my_form.is_valid():
            print(my_form.cleaned_data)
            try:

                Users.objects.create(**my_form.cleaned_data)
            except:
                print("found error")
                my_form.add_error('firstname','Please make sure the user does not already exist')
                context = {"form": my_form}
                return render(request, 'people_create.html', context)
            
        return HttpResponseRedirect("/people")

    context = {"form": my_form}
    return render(request, 'people_create.html', context)

def people_create_open(request):
    print("trying people create")
    my_form = RawUserForm()
    if request.method == "POST":
        my_form = RawUserForm(request.POST)
        if my_form.is_valid():
            print(my_form.cleaned_data)
            try:
                print("about to assign waiver")
                my_form.cleaned_data['waiverAcceptedDate'] = datetime.datetime.strftime(timezone.now(),'%m/%d/%y')
                
                print(my_form.cleaned_data)
                Users.objects.create(**my_form.cleaned_data)
                response = JsonResponse({"status": "success",})
                return response
            except:
                print(my_form.errors)
                print("found error")
                my_form.add_error('firstname','Please make sure the user does not already exist')
                context = {"form": my_form}
                response = JsonResponse({'status':'false','message':'Please make sure the user does not already exist'}, status=500)
                return response

    else:
        print(my_form.errors)
            
        context = {"form": my_form}
        return HttpResponseRedirect("/signin")

    context = {"form": my_form}
    return HttpResponseRedirect("/signin")

@login_required(login_url='/')
def transaction_create_view(request):
    my_form = RawTransactionForm()
    if request.method == "POST":
        my_form = RawTransactionForm(request.POST)
        if my_form.is_valid():
            print(my_form.cleaned_data)
            person = my_form.cleaned_data['transactionPerson']
            user_id = getUserID(person)
            amount = my_form.cleaned_data['amount']
            obj = Users.objects.get(id=user_id)
            targetId = obj.id
            targetEquity = obj.equity
            my_form.cleaned_data['users_id'] = targetId
            dateToFormat = my_form.cleaned_data['date']
            cleanedDate = datetime.datetime.strftime(dateToFormat, "%m/%d/%Y %I:%M %p")
            my_form.cleaned_data['date'] = cleanedDate
            dateToFormatEnd = my_form.cleaned_data['date']
            if my_form.cleaned_data['transactionType'] == 'Volunteer Credit' or my_form.cleaned_data['transactionType'] == 'Imported Balance':
                newEquity = obj.equity + amount
                if newEquity > 250:
                    obj.equity = 250
                else:
                    obj.equity = newEquity
            elif my_form.cleaned_data['transactionType'] == 'Parts Purchase' or my_form.cleaned_data['transactionType'] == 'Bike Purchase' or my_form.cleaned_data['transactionType'] == 'Stand Time Purchase'or my_form.cleaned_data['transactionType'] == 'Bike Purchase':
                if my_form.cleaned_data['paymentType'] == 'Sweat Equity':
                    obj.equity = obj.equity - amount
                else:
                    pass
            else:
                pass
            obj.save()
            Transactions.objects.create(**my_form.cleaned_data)
            return HttpResponseRedirect("new")
    context = {"form": my_form}
    return render(request, 'transaction_create.html', context)

@login_required(login_url='/')

def timelogs_create_view(request):
    my_form = RawTimelogsForm()
    if request.method == "POST":
        print("In time logs create view from post request")
        my_form = RawTimelogsForm(request.POST)
        if my_form.is_valid():
            print(my_form.cleaned_data)
            
            person = my_form.cleaned_data['person']
            user_id = getUserID(person)
            obj = Users.objects.get(id=user_id)
            print(f"Expiration = {obj.membershipExp}")
            membershipExp = obj.membershipExp
            targetId = obj.id
            targetEquity = obj.equity
            activity = my_form.cleaned_data['activity']
            my_form.cleaned_data['users_id'] = targetId
            wages = EquityRates.objects.get(pk=1)
            wage = 0
            my_form.cleaned_data['startTime'] = my_form.cleaned_data['startTime']
            my_form.cleaned_data['endTime'] = my_form.cleaned_data['endTime']
            roundedTimeStart = RoundTime(my_form.cleaned_data['startTime'], activity)
            roundedTimeEnd = RoundTime(my_form.cleaned_data['endTime'], activity)
            wageTime = roundedTimeStart.time - roundedTimeEnd.time
            wageTimeHours = abs(wageTime.total_seconds() / 60 / 60)
            print(f"setting wage for activity {activity}")
            print(f"wages = {wages}")
            print(f"wage for volunteerTime = {wages.sweatEquity}")
            print(f"wage for standTime = {wages.standTime}")
            if activity == 'Volunteering':
                print("volunteer check")
                wage=wages.sweatEquity
            elif activity == 'Stand Time':
                todayDate = timezone.now()
                if membershipExp:
                    membershipDateFormatted = datetime.datetime.strptime(membershipExp,'%m/%d/%y')
                    print(f"membershipDateFormatted = {membershipDateFormatted}")
                    print(f"todayDate = {todayDate}")
                    print(f"{membershipDateFormatted} < {todayDate}")
                    if membershipDateFormatted >  todayDate: #if the membership date is greater than today's date, then the membership is valid
                        wage = 0 #if the membership is valid, then the wage is 0
                        print("exp has not passed yet")
                    else:
                        wage = wages.standTime #if the membership is not valid, then the wage is the stand time wage
            else:
                wage = 0
            incrementedEquity = targetEquity + wageTimeHours*wage
            if incrementedEquity > 250:
                obj.equity = 250
            else:
                obj.equity = incrementedEquity
            print(f"this is the recieved equity {wageTimeHours*wage} with wage = {wage}")
            
            obj.save()
            # my_form.cleaned_data['endTime'] = roundedTimeEnd
            Timelogs.objects.create(**my_form.cleaned_data)
            my_form = RawTimelogsForm()
            return HttpResponseRedirect("new")
    context = {"form": my_form}
    return render(request, 'timelogs_create.html', context)

@login_required(login_url='/')
def people(request):
    obj = Users.objects.all()
    args = {'obj': obj, 'people_page': "active"}
    return render(request, 'people.html', args)

def signin_request(request):
    print("hit the correct view")
    obj = Users.objects.all()
    print(f"this it the port request {request.POST}")
    userID = request.POST['userid']
    my_form = NewSignIn(request.POST)
  
    if my_form.is_valid():
        targetUser = Users.objects.get(id=userID)
        my_form.cleaned_data['users_id'] = targetUser.id
        if not my_form.cleaned_data['startTime']:
            my_form.cleaned_data['startTime'] = timezone.now()
        roundedTime = RoundTime(my_form.cleaned_data['startTime'],my_form.cleaned_data['activity'])
        # roundedTime = roundedTime.time.replace(tzinfo=pytz.UTC)
        my_form.cleaned_data['startTime'] = roundedTime.time
        
        Timelogs.objects.create(**my_form.cleaned_data)
        targetUser.lastVisit = roundedTime
        
        targetUser.save()
        
    else:
        print("form not valid")
        print(my_form.errors)

    payload = {'success': True}
    return HttpResponse(json.dumps(payload), content_type='application/json')

@login_required(login_url='/')

def signin(request):
    new_user = RawUserForm()
    currentUsers = Timelogs.objects.filter(endTime__isnull=True)
    print("aight time to try")
    obj = Users.objects.all()
    my_form = NewSignIn()

    args = {'obj': obj,'form':my_form,'currentUsers':currentUsers, 'user_form':new_user}
    

    return render(request, 'signin.html', args)


@login_required(login_url='/')
def timelogs(request):
    
    timelogs = Timelogs.objects.filter(endTime__isnull=False).order_by('-startTime')
    paginator = Paginator(timelogs, 25)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    args = {
         'timelogs_page': "active", 'timelogs': timelogs, 'page_obj': page_obj}
    return render(request, 'timelogs.html', args)

def timelogs_data_request(request):
    print("In timelogs data request")
    start = int(request.GET.get('start', 0))
    end = int(request.GET.get('length', 20))
    print(f"heres start = {start} and end {end}")
    obj = Timelogs.objects.filter(endTime__isnull=False).values()
    finalList = list(obj)
    # finalListSorted = sorted(finalList, key=lambda date:datetime.datetime.strptime(date['startTime'],"%m/%d/%Y %I:%M %p"),reverse=True)
    finalListSorted = sorted(finalList, key=lambda date:date['startTime'],reverse=True)

    

    timelogList =  []
    columns = ['person', 'startTime','endTime','activity','hours','id']
    
    for timelog in finalListSorted[start:start+end]:
        userTimelog = []
        for column in columns:
            if column == "startTime":
                if isinstance(timelog['startTime'], datetime.date):
                    timelog['hours'] = "{:.2f}".format((timelog['endTime'] - timelog['startTime']).seconds/60/60)
                    
                    # timelog['startTime'] = timelog['startTime'].replace(tzinfo='US/Eastern')
                    # timelog['endTime'] = timelog['endTime'].replace(tzinfo='US/Eastern') 
                    
                    timelog['startTime'] = datetime.datetime.strftime(timelog['startTime'],"%b %d, %Y, %I:%M %p")
                    timelog['endTime'] = datetime.datetime.strftime(timelog['endTime'],"%b %d, %Y, %I:%M %p")

            userTimelog.append(str(timelog.get(column)))
           
        timelogList.append(userTimelog)
    
    draw = int(request.GET.get('draw'))
    recordsTotal = obj.count()
    recordsFiltered = obj.count()
    timelogData = {
    "draw": draw,
    "recordsTotal": recordsTotal,
    "recordsFiltered": recordsFiltered,
    "data": timelogList,
   }
    # print(timelogData)
    
    return JsonResponse(timelogData)
def people_transactions_data_request(request,id):
    
    print("people timelogs and transactions")
    start = int(request.GET.get('start', 0))
    end = int(request.GET.get('length', 20))
    print(f"heres start = {start} and end {end}")

    timelogs = Timelogs.objects.filter(Q(endTime__isnull=False)&Q(users_id=id)).values()
    obj = Transactions.objects.filter(users_id=id).values()
    timelogList = list(timelogs)
    wages = EquityRates.objects.get(pk=1)
    transactionList = list(obj)
    for element in timelogList:
        element['type'] = 'Timelog'
        wage = 0
        volunteerDuration = element['endTime'] - element['startTime']
        if element['activity'] == 'Volunteering':
            wage=wages.sweatEquity
        elif element['activity'] == 'Stand Time':
           wage= wages.standTime
        else:
            wage = 0
        element['amount'] = "{:.2f}".format((volunteerDuration.seconds/60/60)*wage)
        element['date'] = element['endTime']
        element['transactionPerson'] = element['person']
        if element['payment'] == 0:
            element['paymentType'] = 'Sweat Equity'
        else:
            element['paymentType'] = 'Cash/Card'
        
        element['transactionType'] = str(element['activity'])
    for element in transactionList:
        if str(element['transactionType']) == 'Bike Purchase' or str(element['transactionType']) == 'Parts Purchase':
            if str(element['amount'])[0] != '-':
                element['amount'] = str("-"+str(element['amount']))
            else:
                element['amount'] = str(element['amount'])
    finalList = timelogList + transactionList

    transactionList =  []
    columns = ['transactionPerson', 'date','transactionType','amount','paymentType','type','id']
    finalList = sorted(obj, key=lambda user:datetime.datetime.strptime(user['date'],"%m/%d/%Y %I:%M %p"),reverse=True)

    for transaction in finalList[start:start+end]:
        userTransaction = []
        
        for column in columns:
            if column == "date":
                formattedDate = datetime.datetime.strptime(transaction.get(column), "%m/%d/%Y %I:%M %p")
                
                userTransaction.append(datetime.datetime.strftime(formattedDate, '%b %d, %Y, %I:%M %p'))
            else:
                userTransaction.append(str(transaction.get(column)))
        transactionList.append(userTransaction)
    
    draw = int(request.GET.get('draw'))
    recordsTotal = len(finalList)
    recordsFiltered = len(finalList)
    transactionData = {
    "draw": draw,
    "recordsTotal": recordsTotal,
    "recordsFiltered": recordsFiltered,
    "data": transactionList,
   }
    print(transactionData)
    
    return JsonResponse(transactionData)
def people_timelogs_data_request(request,id):
    print("ya want me data eh")
    start = int(request.GET.get('start', 0))
    end = int(request.GET.get('length', 20))
    print(f"heres start = {start} and end {end}")
    obj = Timelogs.objects.filter(Q(endTime__isnull=False) & Q(users_id = id)).values()
    sortedObj = sorted(obj, key=lambda user:user['endTime'],reverse=True)

    timelogList =  []
    columns = ['person', 'startTime','endTime','activity','hours','id']
    
    for timelog in sortedObj[start:start+end]:
        userTimelog = []
        
        for column in columns:
            if column == 'startTime':
                # timelog['startTime'] = timelog['startTime']
                formattedTime = datetime.datetime.strftime(timelog['startTime'], '%b %d, %Y, %I:%M %p')
                userTimelog.append(formattedTime)
            elif column == 'endTime':
                # timelog['endTime'] = timelog['endTime']
                formattedTime = datetime.datetime.strftime(timelog['endTime'], '%b %d, %Y, %I:%M %p')
                userTimelog.append(formattedTime)
            elif column == 'hours':
                hours = "{:.2f}".format((timelog['endTime'] - timelog['startTime']).seconds/60/60)
                userTimelog.append(hours)
            else:
                userTimelog.append(str(timelog.get(column)))
        timelogList.append(userTimelog)
    
    draw = int(request.GET.get('draw'))
    recordsTotal = obj.count()
    recordsFiltered = obj.count()
    timelogData = {
    "draw": draw,
    "recordsTotal": recordsTotal,
    "recordsFiltered": recordsFiltered,
    "data": timelogList,
   }
    print(timelogData)
    
    return JsonResponse(timelogData)
def people_data_request(request):
    search = request.GET.get('search[value]')
    print(f"the search query is {search}")    
    start = int(request.GET.get('start', 0))
    end = int(request.GET.get('length', 20))
    print(f"heres start = {start} and end {end}")
    obj = Users.objects.filter(lastname__icontains = search).values()
    sortedObj = sorted(obj, key=lambda user:user['lastname'])
    # print(f"sortedobj = {sortedObj}")

    peopleList =  []
    columns = ['name', 'lastVisit','equity','waiverAcceptedDate','id']
    
    for timelog in sortedObj[start:start+end]:
        userTimelog = []
        
        for column in columns:
            if column == 'name':
                userTimelog.append(str(timelog.get("lastname"))+","+str(timelog.get("firstname")) +" " + str(timelog.get("middlename")))
            else:

                userTimelog.append(str(timelog.get(column)))
        peopleList.append(userTimelog)
    
    draw = int(request.GET.get('draw'))
    recordsTotal = obj.count()
    recordsFiltered = obj.count()
    timelogData = {
    "draw": draw,
    "recordsTotal": recordsTotal,
    "recordsFiltered": recordsFiltered,
    "data": peopleList,
   }

    # print(timelogData)
    return JsonResponse(timelogData)

def transactions_data_request(request):
    start = int(request.GET.get('start', 0))
    end = int(request.GET.get('length', 20))
    print(f"heres start = {start} and end {end}")
    # 
    timelogs = Timelogs.objects.filter(endTime__isnull=False).values().order_by('-endTime')
    obj = Transactions.objects.all().values().order_by('date')
    timelogList = list(timelogs)
    wages = EquityRates.objects.get(pk=1)
    transactionList = list(obj)
    for element in timelogList:
        element['type'] = 'Timelog'
        wage = 0
        volunteerDuration = element['endTime'] - element['startTime']
        if element['activity'] == 'Volunteering':
            wage=wages.sweatEquity
        elif element['activity'] == 'Stand Time':
           wage= wages.standTime
        else:
            wage = 0
        element['amount'] = (volunteerDuration.seconds / 60 / 60)*wage
        element['date'] = element['endTime']
        element['transactionPerson'] = element['person']
        if element['payment'] == 0:
            element['paymentType'] = 'Sweat Equity'
        else:
            element['paymentType'] = 'Cash/Card'
        element['transactionType'] = str(element['activity'])
    for element in transactionList:
        if str(element['transactionType']) == 'Bike Purchase' or str(element['transactionType']) == 'Parts Purchase':
            if str(element['amount'])[0] != '-':
                element['amount'] = str("-"+str(element['amount']))
            else:
                element['amount'] = str(element['amount'])
    finalList = timelogList + transactionList
    finalListSorted = sorted(finalList, key=lambda date:datetime.datetime.strptime(element['date'],"%m/%d/%Y %I:%M %p"),reverse=True)
    # 

    transactionList =  []
    columns = ['transactionPerson', 'date','transactionType','amount','paymentType','type','id']
    
    for transaction in finalListSorted[start:start+end]:
        userTransaction = []
        
        for column in columns:
            if column == "date":
                if isinstance(transaction['date'], datetime.date):
                    transaction['date'] = datetime.datetime.strftime(transaction['date'],"%m/%d/%Y %I:%M %p")

            userTransaction.append(str(transaction.get(column)))
        transactionList.append(userTransaction)
    
    draw = int(request.GET.get('draw'))
    recordsTotal = len(finalList)
    recordsFiltered = len(finalList)
    transactionData = {
    "draw": draw,
    "recordsTotal": recordsTotal,
    "recordsFiltered": recordsFiltered,
    "data": transactionList,
   }
    print(transactionData)
    
    return JsonResponse(transactionData)
@login_required(login_url='/')
def transactions(request):
    args = {
        # 'obj': finalList, 
        'transactions_page': "active"}
    return render(request, 'transactions.html', args)

@login_required(login_url='/')
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

def loadUsers(request):
    print("loading users")
    nullmiddles = Users.objects.filter(middlename = 'NULL')
    for user in nullmiddles:
        user.middlename = ' '
        user.save()

    return HttpResponseRedirect("/charts")

def signout(request, id, payment):
    # Statement.objects.filter(id__in=statements).update(vote=F('vote') + 1)
    # for updating the equity
    currentTime = timezone.now()
    print(f"trying for id {id}")
    obj = Timelogs.objects.get(pk=id)
    targetid = obj.users_id
    equity = Users.objects.get(pk=targetid)
    obj.endTime = currentTime
    if request.method == "POST":
        unroundedTimeEnd = RoundTime(obj.endTime, obj.activity)
        obj.endTime = unroundedTimeEnd.roundTime()
        obj.payment = payment
        if payment == 1:
            obj.paymentStatus = 'Pending'
        else:
            pass
        activity = obj.activity
        wages = EquityRates.objects.get(pk=1)
        wage = 0
        print(f"wages = {wages}")
        print(f"wage for volunteerTime = {wages.volunteerTime}")
        print(f"wage for standTime = {wages.standTime}")
        print(f"wage for sweatEquity = {wages.sweatEquity}")
        membershipDate = equity.membershipExp
        isvalid = 0
    
        todayDate = timezone.now()
        if membershipDate:
            membershipDateFormatted = datetime.datetime.strptime(membershipDate,'%m/%d/%y')
            membershipDateFormatted = membershipDateFormatted.replace(tzinfo=None) #error on signout page
            print(f"membershipDateFormatted = {membershipDateFormatted}")
            print(f"todayDate = {todayDate}")
            print(f"{membershipDateFormatted} < {todayDate}")
            if membershipDateFormatted >  todayDate:
                print(f"{membershipDateFormatted} - {todayDate}")
                membershipExp = datetime.datetime.strftime(datetime.datetime.strptime(membershipDate,'%m/%d/%y'),'%m/%d/%y')
                isvalid = 1
                print("exp has not passed yet")
            else:
                isvalid = 0
                membershipExp = 'null'
        else:
            membershipExp = 'null'
        print(f"isvalid {isvalid} with activity {activity}")

        if activity == 'Volunteering':
            print("confirmed volunteer")
            wage=wages.sweatEquity
        elif activity == 'Stand Time':
            print("confirmed stand time")
            print(f"payment of {payment}")
            if int(payment) != 1:
                if isvalid == 1:
                    wage = 0
                else:
                    wage = wages.standTime
            else:
                wage = 0       
        elif activity == 'Volunteer Stand Time':
            print("confirmed volunteer stand time")
            if int(payment) != 1:
                if isvalid == 1:
                    wage = 0
                else:
                    wage = wages.standTime
            else:
                wage = 0
        else:
            wage = 0
        currentEquity = equity.equity
        print(f"paying the wage = {wage} for the activity {activity}")
        time_in_hours = (obj.endTime - obj.startTime).seconds / 60 / 60
        incrementedEquity = currentEquity + (time_in_hours)*wage
        if incrementedEquity >250:
            equity.equity = 250
        else:
            equity.equity = incrementedEquity
        equity.save()
        obj.save()
        print(f'new obj endTime {obj.endTime}')
        if activity ==  'Stand Time':

            payload = {'success': True}
            return HttpResponse(json.dumps(payload), content_type='application/json')
        else: 
            return HttpResponseRedirect("/dashboard")
        print("should be done by now")
    return HttpResponseRedirect("/dashboard")

def signoutPublic(request, id, payment):
    # for updating the equity
    currentTime = timezone.now()
    print(f"trying for id {id}")
    obj = Timelogs.objects.get(pk=id)
    targetid = obj.users_id
    equity = Users.objects.get(pk=targetid)
    obj.endTime = currentTime
    if request.method == "POST":
        
        roundedTimeStart = RoundTime(obj.startTime, obj.activity).roundTime()
        unroundedTimeEnd = RoundTime(obj.endTime, obj.activity)
        roundedTimeEnd = unroundedTimeEnd.roundTime()
        
        obj.payment = payment
        if payment == 1:
            obj.paymentStatus = 'Pending'
        else:
            pass
        if roundedTimeEnd < roundedTimeStart:
            roundedTimeEnd = roundedTimeStart
            
        else:
            pass
        elapsedTime = roundedTimeEnd - roundedTimeStart


        print(f"elapsed time = {elapsedTime}")
        activity = obj.activity
        wages = EquityRates.objects.get(pk=1)
        wage = 0
        print(f"wages = {wages}")
        print(f"wage for volunteerTime = {wages.volunteerTime}")
        print(f"wage for standTime = {wages.standTime}")
        print(f"wage for sweatEquity = {wages.sweatEquity}")
        membershipDate = equity.membershipExp
        # isvalid = 0
    
        todayDate = timezone.now()
        if membershipDate:
            membershipDateFormatted = datetime.datetime.strptime(membershipDate,'%m/%d/%y')
            membershipDateFormatted = membershipDateFormatted.replace(tzinfo=None) #could cause possible error
            print(f"membershipDateFormatted = {membershipDateFormatted}")
            print(f"todayDate = {todayDate}")
            print(f"{membershipDateFormatted} < {todayDate}")
            if membershipDateFormatted >  todayDate:
                membershipExp = datetime.datetime.strftime(datetime.datetime.strptime(membershipDate,'%m/%d/%y'),'%m/%d/%y')
                isvalid = 1
                print("exp has not passed yet")
            else:
                isvalid = 0
                membershipExp = 'null'
        else:
            membershipExp = 'null'
        # print(f"isvalid {isvalid}")
        if activity == 'Volunteering':
            print("volunteer check")
            wage=wages.sweatEquity
        elif activity == 'Member Stand Time':
            wage= 0
        elif activity == 'Stand Time':
            wage= wages.standTime
        else:
            wage = 0
        currentEquity = equity.equity
        time_in_hours = (roundedTimeEnd - roundedTimeStart).seconds / 60 / 60
        payableTime = time_in_hours
        print(f"payable time = {payableTime}")
        print(f"paying the wage = {wage} for the activity {activity}")
        print(f"this is the payment value {payment}")
        if payment == 0:
            incrementedEquity = currentEquity + payableTime*wage
        else:
            incrementedEquity = currentEquity
        if incrementedEquity > 250:
            equity.equity = 250
            
        else:
            equity.equity = incrementedEquity
        equity.save()
        obj.save()
        print(f'new obj endTime {obj.endTime}')
        summary = {"activity":obj.activity,"name":obj.person,"startTime": roundedTimeStart, "endTime":roundedTimeEnd,"elapsed":round(payableTime,2),"wage":wage,"currentBalance":incrementedEquity, "earned":int(payableTime*wage)}
        new_user = RawUserForm()
        currentUsers = Timelogs.objects.filter(endTime__isnull=True)
        obj = Users.objects.all()
        my_form = NewSignIn()
        print("successful signout achieved")
        if activity == 'Stand Time':
            responseData = {'status':'success',
            'summary':summary}
            response = JsonResponse(responseData)
            return response
        else:
            args = {'obj': obj,'form':my_form,'currentUsers':currentUsers, 'user_form':new_user,'summary':summary}
            return render(request, 'signin.html', args)
    args = {'obj': obj,'form':my_form,'currentUsers':currentUsers, 'user_form':new_user,'summary':summary}
    return render(request, 'signin.html', args)

def delete_request_public(request, id):
    if request.method == "POST":
        print(f"trying for id {id}")
        obj = Timelogs.objects.filter(id=id)
        obj.delete()
        print("object deleted")
        return HttpResponseRedirect('/signin')

    return HttpResponseRedirect('/signin')

def delete_request(request, id):
    if request.method == "POST":
        print(f"trying for id {id}")
        obj = Timelogs.objects.filter(id=id)
        obj.delete()
        print("object deleted")
        return HttpResponseRedirect('/dashboard')

    return HttpResponseRedirect('/dashboard')

def django_delete_request(request, username):
    if request.method == "POST":
        print(f"trying for id {username}")
        obj = User.objects.get(username=username)
        obj.delete()
        print("object deleted")
        return HttpResponseRedirect('/users')
    print("done deleting")

    return HttpResponseRedirect('/users')

@login_required(login_url='/')
def transactions_edit(request, id):
    my_form = RawTransactionForm()
    obj = Transactions.objects.get(id=id)
    fieldsDict = {'transactionPerson':obj.transactionPerson,'transactionType':obj.transactionType,'amount':obj.amount,'paymentType':obj.paymentType,'paymentStatus':obj.paymentStatus,'date':obj.date}
    for field in fieldsDict:
        my_form.fields[field].widget.attrs['placeholder'] = fieldsDict.get(field)
    if request.method == "POST":
        my_form = RawTransactionForm(request.POST)
        if my_form.is_valid():
            print(my_form.cleaned_data)
            obj.date = datetime.datetime.strftime(my_form.cleaned_data.get('date'),"%m/%d/%Y %I:%M %p")
            obj.transactionPerson = my_form.cleaned_data.get('transactionPerson')
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

@login_required(login_url='/')
def timelogs_edit(request, id):
    my_form = RawTimelogsForm()
    obj = Timelogs.objects.get(id=id)
    fieldsDict = {'person':obj.person,'activity':obj.activity,'startTime':obj.startTime,'endTime':obj.endTime, 'payment':obj.payment}
    

    for field in fieldsDict:
        if field == 'startTime' or field == 'endTime':
            my_form.fields[field].widget.attrs['placeholder'] = datetime.datetime.strftime(fieldsDict.get(field), '%m/%d/%Y %I:%M %p')
        else: 
            my_form.fields[field].widget.attrs['placeholder'] = fieldsDict.get(field)
    if request.method == "POST":
        my_form = RawTimelogsForm(request.POST)
        if my_form.is_valid():
            print(my_form.cleaned_data)
            obj.person = my_form.cleaned_data.get('person')
            obj.activity = my_form.cleaned_data.get('activity')
            obj.payment = my_form.cleaned_data.get('payment')
            obj.startTime = my_form.cleaned_data.get('startTime')
            obj.endTime = my_form.cleaned_data.get('endTime')
            if obj.endTime < obj.startTime:
                obj.endTime = obj.startTime
            else:
                pass
            elapsedTime = obj.startTime - obj.endTime
            print(f"changing starttime and endtime {my_form.cleaned_data.get('startTime')} and {my_form.cleaned_data.get('endTime')}")
            obj.save()
            print("updated forms")

            return HttpResponseRedirect("/timelogs")
        else:
            print("failed")
    context = {"form": my_form}
    return render(request, 'timelogs_edit.html', context)

@login_required(login_url='/')
def people_edit(request, id):
    my_form = RawUserForm()
    obj = Users.objects.get(id=id)
    
    fieldsDict = {'firstname':obj.firstname,'middlename':obj.middlename,'lastname':obj.lastname,'waiverAcceptedDate':obj.waiverAcceptedDate,'membershipExp':obj.membershipExp,'birthdate':obj.birthdate,'email':obj.email,'phone':obj.phone,'emergencyName':obj.emergencyName,'relation':obj.relation,'emergencyPhone':obj.emergencyPhone}
    for field in fieldsDict:
        my_form.fields[field].widget.attrs['placeholder'] = fieldsDict.get(field)
    targetid = obj.id
    timelogs = Timelogs.objects.filter(Q(users_id=targetid) & Q(endTime__isnull = False))
    # for timelog in timelogs:
    #     if timelog['endTime']:
    #         volunteerDuration = datetime.datetime.strptime(timelog['endTime'], "%m/%d/%Y %I:%M %p") - datetime.datetime.strptime(timelog['startTime'], "%m/%d/%Y %I:%M %p")
    #         timelog['hours'] = float(volunteerDuration.seconds/60/60)
    bikePurchases = Transactions.objects.filter(Q(transactionType = 'Bike Purchase') & Q(users_id = targetid) & Q(paymentType = 'Sweat Equity')).values('date')
    shifts = Timelogs.objects.filter(Q(users_id = targetid) & Q(activity='Volunteering')).count()
    numBikes = 0
    
    # isvalid = 1 #this one fixes the error, but there is no check if the experation date is valid
    endTime = timezone.now()
    utc = pytz.UTC
    
    


    for bike in bikePurchases:
        print(bike['date'])
        # if (timezone.make_aware(datetime.datetime.strptime(bike['date'],'%m/%d/%Y %I:%M %p'))) > (timezone.make_aware(timezone.now()-datetime.timedelta(days=365))):
        if (datetime.datetime.strptime(bike['date'],'%m/%d/%Y %I:%M %p')) > (timezone.now()-datetime.timedelta(days=365)):
            numBikes+=1

    
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
    transactions = Transactions.objects.filter(Q(users_id=targetid) & Q(paymentType = 'Sweat Equity')).values()
    timelogList = list(Timelogs.objects.filter(Q(users_id = targetid) & Q(endTime__isnull = False)).values())
    
    transactionList = list(transactions)
    wages = EquityRates.objects.get(pk=1)
    finalTimelogList = []
    for element in timelogList:
        element['type'] = 'Timelog'
        wage = 0
        # volunteerDuration = datetime.datetime.strptime(element['endTime'], "%m/%d/%Y %I:%M %p") - datetime.datetime.strptime(element['startTime'], "%m/%d/%Y %I:%M %p")
        if element['activity'] == 'Volunteering':
            wage=wages.sweatEquity
        elif element['activity'] == 'Stand Time':
            wage=wages.standTime
        else:
            wage = 0
        # element['startTime'] = element['startTime'] + timedelta(hours=-4) # convert to est
        # element['endTime'] = element['endTime'] + timedelta(hours=-4) # convert to est

        element['duration'] = element['endTime'] - element['startTime']
        element['amount'] = (element['duration'].seconds/60/60)*wage
        element['hours'] = element['duration'].seconds/60/60
        element['date'] = datetime.datetime.strftime(element['endTime'], '%m/%d/%y %I:%M %p')
        element['transactionPerson'] = element['person']
        element['paymentType'] = 'Sweat Equity'
        element['transactionType'] = element['activity']
        # finalTimelogList.append(element)
    for element in transactionList:
        if str(element['transactionType']) == 'Bike Purchase' or str(element['transactionType']) == 'Parts Purchase':

            element['amount'] = str("-"+str(element['amount']))
    finalList = timelogList + transactionList
    finalList = timelogList + transactionList
    volunteerAlert = wages.volunteerAlert

    #--------------------- (START) Check if membership is valid ---------------------
    membershipDate = obj.membershipExp

    # print(f"------{membershipDate}------")
    isvalid = 0 #default to not valid
    todayDate = timezone.now()
    if membershipDate:
        membershipDateFormatted = datetime.datetime.strptime(membershipDate,'%m/%d/%y')
        print(f"membershipDateFormatted = {membershipDateFormatted}")
        print(f"todayDate = {todayDate}")
        print(f"{membershipDateFormatted} < {todayDate}")
        if membershipDateFormatted >  todayDate: #if the membership date is greater than today's date, then the membership is valid
            isvalid = 1
            print("exp has not passed yet")
        else:
            isvalid = 0
            
    print(f"isvalid {isvalid}")

    #--------------------- (END) Check if membership is valid ---------------------

    context = {"form": my_form, 'person':obj, 'transactions':transactions,'timelogs':finalTimelogList,'numBikes':numBikes,'numShifts':shifts,'membershipExp':obj.membershipExp,'isvalid':isvalid,'obj':finalList,'volunteerAlert':volunteerAlert}
    return render(request, 'people_edit.html', context)

def transaction_delete_request(request, id):
    if request.method == "POST":
        print(f"trying for id {id}")
        obj = Transactions.objects.get(id=id)
        obj.delete()
        usr = obj.users
        usr.equity += obj.amount
        usr.save()
        print(obj.users.equity)
        print("object deleted")
        return HttpResponseRedirect('/transactions')

def timelogs_delete_request(request, id):
    print(f"this is the request{request.get_full_path()}")
    if request.method == "POST":
        print(f"trying for id {id}")
        obj = Timelogs.objects.get(id=id) 
        timelog_time_rounded_start = RoundTime(obj.startTime, obj.activity)
        timelog_time_rounded_end = RoundTime(obj.endTime, obj.activity)
        timelog_time = timelog_time_rounded_start.time - timelog_time_rounded_end.time
        wage = getEquityAmount(abs(timelog_time.total_seconds()/60/60), obj.activity)
        usr = obj.users
        usr.equity -= wage
        usr.save()
        
        obj.delete()
        print("object deleted")
        return HttpResponseRedirect('/timelogs')

    return HttpResponseRedirect('/timelogs')

def user_delete_request(request, id):
    if request.method == "POST":
        print("made it to user delete request")
        print(f"trying for id {id}")
        obj = Users.objects.get(id=id)
        timelogs = Timelogs.objects.filter(users_id = id)
        timelogs.delete()
        transactions = Transactions.objects.filter(users_id = id)
        transactions.delete()
        obj.delete()
        print("object deleted")
        return HttpResponseRedirect('/people')

    return HttpResponseRedirect('/people')

def search_request(request):
    print("in function")
    if request.method == 'GET':
        search_request = request.GET.get('search_query')
        if search_request != '':
            # print(f"searchtext in if = {search_request}")
            users = Users.objects.filter(lastname__icontains=search_request).values()
            if not users:
                userList = ['no persons found']
            else:
                userList = list(users)
        else:
            userList = ['Enter Last name']
        # print(userList)
        userList = sorted(userList, key = lambda i: i['firstname'])

        return JsonResponse(userList[0:50], safe=False)

def get_equity_values():
    print("in get_equity_values")
    equity = EquityRates.objects.get(id=1)

    return equity.sweatEquity

def update_equity(request):
    print("Update Equity Request made")

    responseEquity = EquityRates.objects.get(id=1)

    print("Current sweatEquity: " + str(responseEquity.sweatEquity))
    print("Current standTime: " + str(responseEquity.standTime))

    if request.method == 'GET':
        print("GET request made")
        # responseEquity = EquityRates.objects.get(id=1)
        return JsonResponse({"sweatEquity": responseEquity.sweatEquity, "standTime": responseEquity.standTime}, safe=False, json_dumps_params={'indent': 4, "default": str, "ensure_ascii": False, "sort_keys": True, "separators": (",", ":")})

    if request.method == 'POST':
        
        requestSweatEquity = int(request.POST.get('sweatEquity'))
        requestStandTime = int(request.POST.get('standTime'))

        print("Updated sweatEquity: " + str(requestSweatEquity))
        print("Updated standTime: " + str(requestStandTime))
        responseEquity = EquityRates.objects.filter(id=1).update(sweatEquity=requestSweatEquity, standTime=-requestStandTime)

        return JsonResponse(responseEquity, safe=False)


def validate_request(request):
    print("validating")
    if request.method == 'GET':
        validation_query = request.GET.get('validation_query')
        print(validation_query)
        uniqueID = validation_query.replace(' ','').upper()
        allusers = Users.objects.all().values()
        userMap = {}
        for user in allusers:
            if user['middlename']!= ' ':
                userID = user['firstname'].replace(' ','')+user['middlename'].replace(' ','')+user['lastname'].replace(' ','')
            else:
                userID = user['firstname'].replace(' ','')+user['lastname'].replace(' ','')

            # print(f"prelim {userID} and post {userID.join(userID.split()).upper()}")
            # userID.join(userID.split())
            userID = userID.upper()
            
            userMap.setdefault(userID,{'id':user['id'],'equity':user['equity']})
        if userMap[uniqueID]:
            print('found')
            userList = userMap[uniqueID]
            print(f'userlist {userList}')
            return JsonResponse(userList, safe=False)
        else:
            return JsonResponse(['not enough characters'], safe=False)


@login_required(login_url='/')
def charts(request):
    rates = EquityRates.objects.get(pk=1)
    my_form = ChangeEquityRates()
    fieldsDict = {'sweatEquity':rates.sweatEquity,'standTime':rates.standTime,'volunteerTime':rates.volunteerTime,'volunteerAlert':rates.volunteerAlert}
    for field in fieldsDict:
        my_form.fields[field].widget.attrs['placeholder'] = fieldsDict.get(field)
    
    hours_form = HoursReport()
    login_form = LoginReport()
    user_form = UserReport()
    range_form = ShiftsInRangeReport()
    if request.method == 'POST':
        print(f"this is the post request for charts: {request.POST}")
        my_form = ChangeEquityRates(request.POST)
        if my_form.is_valid():
            print(my_form.cleaned_data)
            rates.sweatEquity = my_form.cleaned_data['sweatEquity']
            rates.volunteerTime = my_form.cleaned_data['volunteerTime']
            rates.standTime = my_form.cleaned_data['standTime']
            rates.save()

    args = {
        'charts_page': "active", 'form':my_form, 'hoursForm':hours_form, 'loginForm':login_form, 'userForm':user_form,'range_form':range_form
    }
    return render(request, 'charts.html',args)

def generate_report(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="large-report.xls"'
    book = xlwt.Workbook(encoding='utf-8', style_compression = 0)
    rows = ['January', 'February', 'March', 'April', 'May','June','July','August','September','October','November','December']
    columns = ['Month','Volunteering','Stand Time','Shopping','Other','Total']
    userSet = Timelogs.objects.filter(endTime__isnull = False)
    volunteering = []
    memberSheet = book.add_sheet('Members', cell_overwrite_ok = True)
    sweatEquityNeg = book.add_sheet('sweat equity negative balance', cell_overwrite_ok = True)
    sweatEquityNeg.write(0,0, "Broke Spoke")
    sweatEquityNeg.write(1,0, "Sweat Equity Negative Balance ($)")
    currTime = timezone.now()
    sweatEquityNeg.write(2,0, f"As of {currTime}")
    negUsers = Users.objects.filter(equity__lt = 0)
    negUserRow = 3
    negUserColumn = 0

    for user in negUsers:
        sweatEquityNeg.write(negUserRow, 0, user.firstname + ", " + user.lastname)
        sweatEquityNeg.write(negUserRow, 2, user.equity)
        negUserRow+=1
    sweatEquityNeg.write(negUserRow,0,"Total")
    sweatEquityNeg.write(negUserRow,2,xlwt.Formula(f'SUM(C3:C{negUserRow})'))
    sweatEquityBikeP = book.add_sheet('sweat equity bike purchases', cell_overwrite_ok = True)
    sweatEquityBikeP.write(0,0, "Broke Spoke")
    sweatEquityBikeP.write(1,0, "Volunteer Sweat Equity Bike Purchases")
    sweatEquityBikeP.write(2,0, f"As of {currTime}")
    bikePurchasers = Transactions.objects.filter(transactionType = 'Bike Purchase')
    bikePRow = 5
    bikePHeaders = ['Person', 'Date','# of Bikes','$SE Used']
    bikePColumn = 0
    dictOfBikePurchases = {}
    for header in bikePHeaders:
        sweatEquityBikeP.write(4,bikePColumn,bikePHeaders[bikePColumn])
        bikePColumn+=1
    for people in bikePurchasers:
        if people.transactionPerson in dictOfBikePurchases:
            dictOfBikePurchases[people.transactionPerson] = dictOfBikePurchases[people.transactionPerson] + 1
        else:
            dictOfBikePurchases[people.transactionPerson] = 1
        sweatEquityBikeP.write(bikePRow,0,people.transactionPerson)
        sweatEquityBikeP.write(bikePRow,1,people.date)
        sweatEquityBikeP.write(bikePRow,2,1)
        sweatEquityBikeP.write(bikePRow,3,people.amount)
        bikePRow +=1
    sweatEquityBikeP.write(bikePRow,0,"Total")
    sweatEquityBikeP.write(bikePRow,2,xlwt.Formula(f'SUM(C6:C{bikePRow})'))
    sweatEquityBikeP.write(bikePRow,3,xlwt.Formula(f'SUM(D6:D{bikePRow})'))

    bikePurchasePerCustomer = book.add_sheet('Bike Purchases over 1', cell_overwrite_ok = True)
    bikePurchasePerCustomer.write(0,0, "Broke Spoke")
    bikePurchasePerCustomer.write(1,0, "Volunteer Sweat Equity Bike Purchases > 1")
    bikePurchasePerCustomer.write(2,0, f"As of {currTime}")
    bikePPerCustomerRow = 5
    bikePPerCustomerColumn = 0
    bikePPerCustomerColumnHeaders = ["person","YTD # of Bikes"]
    for header in bikePPerCustomerColumnHeaders:
        bikePurchasePerCustomer.write(4,bikePPerCustomerColumn,header)
        bikePPerCustomerColumn+=1
    for person in dictOfBikePurchases:
         if dictOfBikePurchases[person] > 1:
            bikePurchasePerCustomer.write(bikePPerCustomerRow,0,person)
            bikePurchasePerCustomer.write(bikePPerCustomerRow,1,dictOfBikePurchases[person])
            bikePPerCustomerRow+=1
    bikePurchasePerCustomer.write(bikePPerCustomerRow,0,"Total")
    bikePurchasePerCustomer.write(bikePPerCustomerRow,1,xlwt.Formula(f'SUM(B5:B{bikePPerCustomerRow})'))

    keyMetrics = book.add_sheet('key metrics', cell_overwrite_ok = True)
    keyMetrics.write(0,0, "Broke Spoke")
    keyMetrics.write(1,0, "Key metrics")
    keyMetrics.write(2,0, f"As of {currTime}")
    keyMetricsHeaders = ['Total Volunteer hours', 'Total SE$', 'Total Shop Logins','#SE bikes sold','SE $ for bike parts','Stand Time']
    keyMetricColumn = 0
    for header in keyMetricsHeaders:
        keyMetrics.write(3,keyMetricColumn,header)
        keyMetricColumn+=1
    totalVolunteerSet = Timelogs.objects.all()
    totalVolunteerDuration = datetime.timedelta
    totalStandTimeDuration = 0
    for volunteer in totalVolunteerSet:
        if volunteer.activity == 'Volunteering' and volunteer.endTime != None:
            # volunteerDuration = datetime.datetime.strptime(volunteer.endTime, "%m/%d/%Y %I:%M %p") - datetime.datetime.strptime(volunteer.startTime, "%m/%d/%Y %I:%M %p")
            
            # volunteerDuration = (volunteerDuration.seconds//60//60)%60
            totalVolunteerDuration = timedelta(seconds=volunteer.duration.seconds)
            print(f"total volunteer duration {totalVolunteerDuration}")
        if volunteer.activity == 'Member Stand Time' or volunteer.activity == 'Stand Time' and volunteer.endTime != None:
            # standTimeDuration= datetime.datetime.strptime(volunteer.endTime, "%m/%d/%Y %I:%M %p") - datetime.datetime.strptime(volunteer.startTime, "%m/%d/%Y %I:%M %p")
            # standTimeDuration = (standTimeDuration.seconds//60//60)%60
            # totalStandTimeDuration += standTimeDuration
            totalStandTimeDuration = timedelta(seconds=volunteer.duration.seconds)
            print(f"total stand time duration {totalStandTimeDuration}")
    totalSE = Transactions.objects.aggregate(Sum('amount'))['amount__sum']
    print(f"this is totalSE={totalSE}")
    totalShopLogins = Timelogs.objects.count()
    bikesSold = len(Transactions.objects.filter(transactionType = 'Bike Purchase'))
    bikeParts = len(Transactions.objects.filter(transactionType = 'Parts Purchase'))
    keyMetrics.write(4,0, totalVolunteerDuration.seconds)
    keyMetrics.write(4,1,totalSE)
    keyMetrics.write(4,2,totalShopLogins)
    keyMetrics.write(4,3,bikesSold)
    keyMetrics.write(4,4,bikeParts)
    keyMetrics.write(4,5,totalStandTimeDuration.seconds)
    members = Users.objects.exclude(membershipExp = '').values('firstname', 'middlename','lastname','membershipExp','email')
    memberSheet.write(0,0,"List of members both active and inactive")
    memberSheet.write(1,0,"Name")
    memberSheet.write(1,1,"Active/Inactive")
    memberSheet.write(1,2,"Date of Expiration")
    memberSheet.write(1,3,"Email")
    memberRow = 2
    for member in members:
        membershipDate = member['membershipExp']
        print(f"------{membershipDate}------")
        isvalid = 0
        todayDate = timezone.now()
        if membershipDate:
            membershipDateFormatted = datetime.datetime.strptime(membershipDate,'%m/%d/%y')
            print(f"membershipDateFormatted = {membershipDateFormatted}")
            print(f"todayDate = {todayDate}")
            print(f"{membershipDateFormatted} < {todayDate}")
            if membershipDateFormatted >  todayDate: #error for generate-report page
                membershipExp = datetime.datetime.strftime(datetime.datetime.strptime(membershipDate,'%m/%d/%y'),'%m/%d/%y')
                isvalid = 1
                memberSheet.write(memberRow,0,f"{member['firstname']} {member['lastname']}")
                memberSheet.write(memberRow,1,"Active")
                memberSheet.write(memberRow,2,membershipExp)
                memberSheet.write(memberRow,3,member['email'])
                memberRow+=1
                print("exp has not passed yet")
            else:
                isvalid = 0
                membershipExp = 'null'
                memberSheet.write(memberRow,0,f"{member['firstname']} {member['lastname']}")
                memberSheet.write(memberRow,1,"Inactive")
                memberSheet.write(memberRow,2,"------")
                memberSheet.write(memberRow,3,member['email'])
                memberRow+=1
        else:
            membershipExp = 'null'
        # print(f"isvalid {isvalid}")

    book.save(response)
    return response
class LogEntry:
    def __init__(self, startTime, endTime):
        self.startTime = startTime
        self.endTime = endTime
    def duration(self):
        duration = self.endTime-self.startTime
        return duration
class RoundTime:
    def __init__(self, time, activity):
        self.time = time
        self.activity = activity
        self.roundTo=15 # round to 15 minutes
    def roundTime(self):
        newTime = self.time
        discard = datetime.timedelta(minutes=self.time.minute % self.roundTo,
                                    seconds=self.time.second,
                                    microseconds=self.time.microsecond)
        newTime -= discard
        if discard >= datetime.timedelta(minutes=8):
            newTime += datetime.timedelta(minutes=15)
        return newTime


def generateQuery(activity):
    print(f"the activity is {activity}")
    if activity == 'Volunteering':
        columnDataSet = Timelogs.objects.filter(activity = activity)
        # print(f"this is the internal for {activity} dataset {columnDataSet}")
    elif activity == 'Stand Time':
        columnDataSet = Timelogs.objects.filter(Q(activity = activity) | Q(activity='Member Stand Time'))
        # print(f"this is the internal for {activity} dataset {columnDataSet}")
    elif activity == 'Shopping':
        columnDataSet = Timelogs.objects.filter(activity = activity)
        # print(f"this is the internal for {activity} dataset {columnDataSet}")
    elif activity == 'Other':
        columnDataSet = Timelogs.objects.filter(Q(activity = activity) | Q(activity='Imported Login'))
        # print(f"this is the internal for {activity} dataset {columnDataSet}")
    # print(f"this is the returned set {columnDataSet}")
    else:
        columnDataSet = Timelogs.objects.filter(activity=activity)
    return columnDataSet

def generateQueryUnique(activity):
    print(f"the activity is {activity}")
    if activity == 'Volunteering':
        columnDataSet = Timelogs.objects.filter(activity = activity).order_by().values('person','startTime','endTime').distinct('person','activity')
    elif activity == 'Stand Time':
        columnDataSet = Timelogs.objects.filter(Q(activity = activity) | Q(activity='Member Stand Time')).order_by().values('person','startTime','endTime').distinct('person','activity')
    elif activity == 'Shopping':
        columnDataSet = Timelogs.objects.filter(activity = activity).order_by().values('person','startTime','endTime').distinct('person','activity')
    elif activity == 'Other':
        columnDataSet = Timelogs.objects.filter(Q(activity = activity) | Q(activity='imported login')).order_by().values('person','startTime','endTime').distinct('person','activity')
    else:
        columnDataSet = Timelogs.objects.filter(activity=activity)
    # print(f"this is the returned unique set {columnDataSet}")
    return columnDataSet
def hours_report(request):
    monthDict = {'1':'January',
    '2':'February',
    '3':'March',
    '4':'April',
    '5':'May',
    '6':'June',
    '7': 'July',
    '8':'August',
    '9':'September',
    '10':'October',
    '11': 'November',
    '12': 'December'}
    columns = {'Volunteering':'Volunteering','Stand Time':'Stand Time','Shopping':'Shopping','Other':'Other'}
    my_form = LoginReport()
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="hours-report.xls"'
    if request.method == 'POST':
        my_form = LoginReport(request.POST)
        if my_form.is_valid():
            book = xlwt.Workbook(encoding='utf-8', style_compression = 0)
            startDate = my_form.cleaned_data['startDate']
            endDate = my_form.cleaned_data['endDate']
            print(f"startDate = {startDate} and  endDate= {endDate}")
            formattedStartDate = datetime.datetime.strptime(startDate,'%m/%d/%y')
            formattedEndDate = datetime.datetime.strptime(endDate,'%m/%d/%y')
            userDuration = formattedEndDate - formattedStartDate
            dates = [dt for dt in rrule(MONTHLY, dtstart=formattedStartDate, until=formattedEndDate)]
            customerLogin = book.add_sheet('customer logins', cell_overwrite_ok = True)
            row_count = 5
            header_column_count = 1
            customerLogin.write(0,0,"BrokeSpoke")
            customerLogin.write(1,0,"Shop Hours By user defined date range")
            customerLogin.write(2,0,f"Date range {startDate} - {endDate}")
            customerLogin.write(4,0,'Month')
            
            for column in columns:
                customerLogin.write(4,header_column_count,column)
                header_column_count+=1
            customerLogin.write(4,5,'Total')

            print(f"Start Date: {formattedStartDate}")
            print(f"End Date: {formattedEndDate}")
            
            dataset = Timelogs.objects.filter(startTime__range=[formattedStartDate, formattedEndDate])
            

            # for date in dates: 
            #     volunteer_time_set = dataset.filter(startTime__month=date.month, activity__icontains="volunteer")
            #     stand_time_set = dataset.filter(startTime__month=date.month, activity__icontains="stand")
            #     shopping_time_set = dataset.filter(startTime__month=date.month, activity__icontains="shopping")
            #     other_time_set = dataset.filter(startTime__month=date.month, activity__icontains="other")
            #     for i in 
            for date in dates:
                volunteer_time_duration = 0
                stand_time_duration = 0
                shopping_time_duration = 0
                other_time_duration = 0
                customerLogin.write(row_count,0,monthDict[str(date.month)])

                
                
                volunteer_time_set = dataset.filter(startTime__month=date.month, activity__icontains="volunteer")
                for i in volunteer_time_set:
                    volunteer_time_duration += i.duration.seconds
                customerLogin.write(row_count,1,round(volunteer_time_duration/60/60,2)) # convert from seconds to hours
                
                stand_time_set = dataset.filter(startTime__month=date.month, activity__icontains="stand")
                for i in stand_time_set:
                    stand_time_duration += i.duration.seconds
                customerLogin.write(row_count,2,round(stand_time_duration/60/60,2))
                
                shopping_time_set = dataset.filter(startTime__month=date.month, activity__icontains="shopping")
                for i in shopping_time_set:
                    shopping_time_duration += i.duration.seconds
                customerLogin.write(row_count,3,round(shopping_time_duration/60/60,2))
                
                other_time_set = dataset.filter(startTime__month=date.month, activity__icontains="other")
                for i in other_time_set:
                    other_time_duration += i.duration.seconds
                customerLogin.write(row_count,4,round(other_time_duration/60/60,2))
                
                customerLogin.write(row_count,5,xlwt.Formula(f'SUM(B{row_count+1}:E{row_count+1})'))
                row_count+=1

                

            customerLogin.write(row_count,5,xlwt.Formula(f'SUM(F5:F{row_count})'))
                
                
            book.save(response)
    return response
    
def login_report(request):
    monthDict = {'1':'January',
    '2':'February',
    '3':'March',
    '4':'April',
    '5':'May',
    '6':'June',
    '7': 'July',
    '8':'August',
    '9':'September',
    '10':'October',
    '11': 'November',
    '12': 'December'}
    columns = {'Volunteering':'Volunteering','Stand Time':'Stand Time','Shopping':'Shopping','Other':'Other'}
    my_form = HoursReport()
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="login-report.xls"'
    if request.method == 'POST':
        my_form = HoursReport(request.POST)
        if my_form.is_valid():
            book = xlwt.Workbook(encoding='utf-8', style_compression = 0)
            startDate = my_form.cleaned_data['startDate']
            endDate = my_form.cleaned_data['endDate']
            print(f"startDate = {startDate} and  endDate= {endDate}")
            formattedStartDate = datetime.datetime.strptime(startDate,'%m/%d/%y')
            formattedEndDate = datetime.datetime.strptime(endDate,'%m/%d/%y')
            userDuration = formattedEndDate - formattedStartDate
            dates = [dt for dt in rrule(MONTHLY, dtstart=formattedStartDate, until=formattedEndDate)]
            customerLogin = book.add_sheet('customer logins', cell_overwrite_ok = True)
            uniqueCustomerLogin = book.add_sheet('unique customer logins', cell_overwrite_ok = True)
            row_count = 5
            header_column_count = 1
            customerLogin.write(0,0,"BrokeSpoke")
            customerLogin.write(1,0,"Customer Logins, By user defined date range")
            customerLogin.write(2,0,f"Date range {startDate} - {endDate}")
            customerLogin.write(4,0,'Month')
            uniqueCustomerLogin.write(0,0,"BrokeSpoke")
            uniqueCustomerLogin.write(1,0,"Unique Customer Logins, By user defined date range")
            uniqueCustomerLogin.write(2,0,f"Date range {startDate} - {endDate}")
            uniqueCustomerLogin.write(4,0,'Month')
            
            for column in columns:
                customerLogin.write(4,header_column_count,column)
                uniqueCustomerLogin.write(4,header_column_count,column)
                header_column_count+=1
            customerLogin.write(4,5,'Total')
            uniqueCustomerLogin.write(4,5,'Total')

            dataset = Timelogs.objects.filter(startTime__range=[formattedStartDate, formattedEndDate])
            for date in dates:
                customerLogin.write(row_count,0,monthDict[str(date.month)])
                uniqueCustomerLogin.write(row_count,0,monthDict[str(date.month)])

                volunteer_logs = dataset.filter(startTime__month=date.month, activity__icontains="volunteer")\
                    .aggregate(count=Count('startTime'))
                customerLogin.write(row_count,1,volunteer_logs['count'])
                stand_logs = dataset.filter(startTime__month=date.month, activity__icontains="stand")\
                    .aggregate(count=Count('startTime'))
                customerLogin.write(row_count,2,stand_logs['count'])
                shopping_time_logs = dataset.filter(startTime__month=date.month, activity__icontains="shopping")\
                    .aggregate(count=Count('startTime'))
                customerLogin.write(row_count,3,shopping_time_logs['count'])
                other_time_logs = dataset.filter(startTime__month=date.month, activity__icontains="other")\
                    .aggregate(count=Count('startTime'))
                customerLogin.write(row_count,4,other_time_logs['count'])

                customerLogin.write(row_count,5,xlwt.Formula(f'SUM(B{row_count+1}:E{row_count+1})'))

                # Unique customer logins
                unique_volunteer_logs = dataset.filter(startTime__month=date.month, activity__icontains="volunteer")\
                    .distinct('person')\
                    .count()
                uniqueCustomerLogin.write(row_count,1,unique_volunteer_logs)
                unique_stand_logs = dataset.filter(startTime__month=date.month, activity__icontains="stand")\
                    .distinct('person')\
                    .count()
                uniqueCustomerLogin.write(row_count,2,unique_stand_logs)
                unique_shopping_time_logs = dataset.filter(startTime__month=date.month, activity__icontains="shopping_time")\
                    .distinct('person')\
                    .count()
                uniqueCustomerLogin.write(row_count,3,unique_shopping_time_logs)
                unique_other_time_logs = dataset.filter(startTime__month=date.month, activity__icontains="other_time")\
                    .distinct('person')\
                    .count()
                uniqueCustomerLogin.write(row_count,4,unique_other_time_logs)

                uniqueCustomerLogin.write(row_count,5,xlwt.Formula(f'SUM(B{row_count+1}:E{row_count+1})'))

                row_count+=1

            customerLogin.write(row_count,5,xlwt.Formula(f'SUM(F5:F{row_count})'))

            uniqueCustomerLogin.write(row_count,5,xlwt.Formula(f'SUM(F5:F{row_count})'))
            book.save(response)
                
            
    return response

def user_report(request):
    my_form = UserReport()
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="user-report.xls"'
    book = xlwt.Workbook(encoding='utf-8', style_compression = 0)
    customerLogs = book.add_sheet('customer logs', cell_overwrite_ok = True)
    if request.method == 'POST':
        my_form = UserReport(request.POST)
        if my_form.is_valid():
            formStartDate = datetime.datetime.strptime(my_form.cleaned_data['startDate'],'%m/%d/%y')
            formEndDate = datetime.datetime.strptime(my_form.cleaned_data['endDate'],'%m/%d/%y')
            
            row_count = 4
            column_count = 0
            usr_id = getUserID(my_form.cleaned_data['person'])
            usr = Users.objects.get(id=usr_id)
            userLogs = Timelogs.objects.filter(users=usr)\
                .filter(startTime__range=[formStartDate, formEndDate])\
                .order_by('startTime').values()
            
            customerLogs.write(0,0,"Broke Spoke")
            customerLogs.write(1,0,"Volunteer shifts")
            customerLogs.write(2,0,my_form.cleaned_data['person'])
            customerLogs.write(3,0,f"date range: {my_form.cleaned_data['startDate']} - {my_form.cleaned_data['endDate']}")
            customerLogs.write(3,3,"Activity")
            
            for userLog in userLogs:
                if userLog['endTime'] != None:
                    userLogFormattedDate = datetime.datetime.strftime(userLog['startTime'], '%m/%d/%y')
                    customerLogs.write(row_count,0,userLogFormattedDate)
                    customerLogs.write(row_count,2,round(Timelogs.objects.get(id=userLog['id']).duration.seconds/60/60,2))
                    customerLogs.write(row_count,3,userLog['activity'])
                    row_count+=1
            customerLogs.write(row_count,0,"Total")
            customerLogs.write(row_count,2,xlwt.Formula(f'SUM(C5:C{row_count})'))

            startDate = my_form.cleaned_data['startDate']
            endDate = my_form.cleaned_data['endDate']
            print(f"startDate = {startDate} and  endDate= {endDate}")
            
    book.save(response)
    return response

def shiftsInRange(request):
    my_form = ShiftsInRangeReport()
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="shift-report.xls"'
    book = xlwt.Workbook(encoding='utf-8', style_compression = 0)
    customerLogs = book.add_sheet('shifts in range', cell_overwrite_ok = True)
    usermap = {}
    if request.method == 'POST':
        my_form = ShiftsInRangeReport(request.POST)
        if my_form.is_valid():
            minimum_logs = my_form.cleaned_data['numShifts']
            formattedStartDate = datetime.datetime.strptime(my_form.cleaned_data['startDate'],'%m/%d/%y')
            formattedEndDate = datetime.datetime.strptime(my_form.cleaned_data['endDate'],'%m/%d/%y')
            timeLogs = Timelogs.objects.exclude(activity="Shopping")\
                .filter(
                    startTime__range=[formattedStartDate, formattedEndDate], 
                    activity__icontains="volunteer"
                )\

            usersLogs = timeLogs.values('person').annotate(num_logs=Count('person'))
            
            row_count = 5
            column_count = 0
            customerLogs.write(0,0,"Broke Spoke")
            customerLogs.write(1,0,"Volunteer shifts")
            customerLogs.write(3,0,f"date range: {my_form.cleaned_data['startDate']} - {my_form.cleaned_data['endDate']}")
            customerLogs.write(4,0,"Person")
            customerLogs.write(4,2,"# of logins")
            for userLog in usersLogs:   
                # logins = timeLogs.annotate(num_logs=Count('endTime'))
                if userLog['num_logs'] >= my_form.cleaned_data['numShifts']:
                    customerLogs.write(row_count,0,userLog['person'])
                    customerLogs.write(row_count,2,userLog['num_logs'])

                row_count+=1
                    
            customerLogs.write(row_count,0,"Total")
            customerLogs.write(row_count,2,xlwt.Formula(f'SUM(C6:C{row_count})'))


    book.save(response)
    return response
def dumpData(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="shift-report.xls"'
    book = xlwt.Workbook(encoding='utf-8', style_compression = 0)
    timelogDump = book.add_sheet('timelog-dump', cell_overwrite_ok = True)
    transactionDump = book.add_sheet('transaction-dump', cell_overwrite_ok = True)
    usersDump = book.add_sheet('user-dump', cell_overwrite_ok = True)
    timelogs = Timelogs.objects.all()
    transactions = Transactions.objects.all()
    users = Users.objects.all()
    row = 1
    timelogHeaders = ['id','activity','startTime','endTime','payment','hours','paymentStatus','users_id','importedTimelogId','importedTransactionId','importedUserId']
    for key,value in enumerate(timelogHeaders):
        timelogDump.write(0,key,value)
    for timelog in timelogs:
        rowObj = [timelog.id,timelog.activity,timelog.startTime,timelog.endTime,timelog.payment,timelog.hours,timelog.paymentStatus,timelog.users_id,timelog.importedTimelogId,timelog.importedTransactionId,timelog.importedUserId]
        for counter,value in enumerate(rowObj):
            timelogDump.write(row,counter,value)
        row+=1
    row = 1
    userHeaders = ['id','firstname','middlename','lastname','waiverAcceptedDate','membershipExp','birthdate','email','phone','emergencyName','relation','emergencyPhone','lastVisit','equity','waiver','permissions','importedID']
    for key,value in enumerate(userHeaders):
        usersDump.write(0,key,value)
    for user in users:
        rowObj = [user.id,user.firstname,user.middlename,user.lastname,user.waiverAcceptedDate,user.membershipExp,user.birthdate,user.email,user.phone,user.emergencyName,user.relation,user.emergencyPhone,user.lastVisit,user.equity,user.waiver,user.permissions,user.importedID]
        for counter,value in enumerate(rowObj):
            usersDump.write(row,counter,value)
        row+=1
    row = 1

    transactionHeaders = ['id','transactionPerson','transactionType','amount','paymentType','paymentStatus','date','users_id','importedTransactionId','importedUserId']
    for key,value in enumerate(transactionHeaders):
        transactionDump.write(0,key,value)
    for transaction in transactions:
        rowObj = [transaction.id,transaction.transactionPerson,transaction.transactionType,transaction.amount,transaction.paymentType,transaction.paymentStatus,transaction.date,transaction.users_id,transaction.importedTransactionId,transaction.importedUserId]
        for counter,value in enumerate(rowObj):
            transactionDump.write(row,counter,value)
        row+=1
    
    book.save(response)
    return response


def getEquityAmount(time_in_hours, activity):
    wages = EquityRates.objects.get(pk=1)
    wage = 0
    if activity == 'Volunteering':
        wage = wages.volunteerTime
    elif activity == 'Stand Time':
        wage = wages.standTime
    else:
        wage = 0

    return (wage*time_in_hours)

    
