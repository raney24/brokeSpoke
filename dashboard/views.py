from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from .models import EquityRates, Transactions, Users, Timelogs, NewSystemUser
from .forms import ShiftsInRangeReport,UserReport,HoursReport, LoginReport,ChangeEquityRates, RawUserForm, RawTransactionForm, RawTimelogsForm, NewSignIn, ChargeEquity, CreateNewSystemUser
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
from django.db.models import F,Q
import xlwt
from django.db.models import Sum
from dateutil import relativedelta
from dateutil.rrule import rrule, MONTHLY





# redirectes to login if not valid
@login_required(login_url='/')

def dashboard(request):
    local = pytz.timezone ("US/Eastern")
    obj = Timelogs.objects.filter(endTime__isnull=True)
    recents = Timelogs.objects.filter(endTime__isnull=False)
    maxObject = timedelta(days=0, hours=3, minutes=0)
    dictOfRecents = []
    for recent in recents:
        naive = datetime.datetime.strptime(recent.endTime, "%m/%d/%Y %I:%M %p")
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
            personList = person.split()
            person_first = personList[0]
            person_last = personList[1]
            person_phone = personList[2]
            print(f"this is the person signing in={person}")
            targetUser = Users.objects.get(lastname=person_last, firstname=person_first,phone__contains=person_phone)
            print(f"signing in user with id {targetUser.id}")
            my_form.cleaned_data['users_id'] = targetUser.id
            print(f"the current foreignkey is {my_form.cleaned_data['users_id']}")
            dateToFormat = my_form.cleaned_data['startTime']
            cleanedDate = datetime.datetime.strftime(dateToFormat, "%m/%d/%Y %I:%M %p")
            unroundedTime = RoundTime(cleanedDate,my_form.cleaned_data['activity'])
            roundedTime = unroundedTime.roundTime()
            print(f"this is the rounded time = {roundedTime}")
            my_form.cleaned_data['startTime'] = roundedTime
            print(f"date is seen as {dateToFormat}")
            print(f"date changed to  {roundedTime}")
            Timelogs.objects.create(**my_form.cleaned_data)
            targetUser.lastVisit = roundedTime
            targetUser.save()
            return HttpResponseRedirect("dashboard")
        if transaction_form.is_valid():
            dateToFormat = transaction_form.cleaned_data['date']
            cleanedDate = datetime.datetime.strftime(dateToFormat, "%m/%d/%Y %I:%M %p")
            transaction_form.cleaned_data['date'] = cleanedDate
            #TODO: add in the correct customer id to apply credit
            print(transaction_form.cleaned_data)
            person = transaction_form.cleaned_data['transactionPerson']
            personList = person.split()
            person_first = personList[0]
            person_last = personList[1]
            person_phone = personList[2]
            print(f"this is the person signing in={person}")
            targetUser = Users.objects.get(lastname=person_last, firstname=person_first,phone__contains=person_phone)
            print(f"signing in user with id {targetUser.id}")
            targetUser.equity = targetUser.equity + transaction_form.cleaned_data['amount']
            transaction_form.cleaned_data['users_id'] = targetUser.id
            targetUser.save()
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
            person = my_form.cleaned_data['transactionPerson'].split()
            amount = my_form.cleaned_data['amount']
            obj = Users.objects.get(firstname=person[0], lastname = person[1], phone__contains = person[2])
            targetId = obj.id
            targetEquity = obj.equity
            my_form.cleaned_data['users_id'] = targetId
            obj.equity = obj.equity+amount
            obj.save()
            dateToFormat = my_form.cleaned_data['date']
            cleanedDate = datetime.datetime.strftime(dateToFormat, "%m/%d/%Y %I:%M %p")
            my_form.cleaned_data['date'] = cleanedDate
            dateToFormatEnd = my_form.cleaned_data['date']
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
            dateToFormat = my_form.cleaned_data['startTime']
            cleanedDate = datetime.datetime.strftime(dateToFormat, "%m/%d/%Y %I:%M %p")
            unroundedTime = RoundTime(cleanedDate,my_form.cleaned_data['activity'])
            roundedTime = unroundedTime.roundTime()
            my_form.cleaned_data['startTime'] = roundedTime
            person = my_form.cleaned_data['person'].split()
            dateToFormatEnd = my_form.cleaned_data['endTime']
            cleanedDateEnd = datetime.datetime.strftime(dateToFormatEnd, "%m/%d/%Y %I:%M %p")
            unroundedTimeEnd = RoundTimeSignout(cleanedDateEnd,my_form.cleaned_data['activity'])
            roundedTimeEnd = unroundedTimeEnd.roundTime()
            wageTime = datetime.datetime.strptime(roundedTimeEnd,"%m/%d/%Y %I:%M %p") - datetime.datetime.strptime(roundedTime,"%m/%d/%Y %I:%M %p")
            wageTimeHours = wageTime.seconds/60/60
            obj = Users.objects.get(firstname=person[0], lastname = person[1], phone__contains = person[2])
            targetId = obj.id
            targetEquity = obj.equity
            activity = my_form.cleaned_data['activity']
            my_form.cleaned_data['users_id'] = targetId
            wages = EquityRates.objects.get(pk=1)
            wage = 0
            print(f"wages = {wages}")
            print(f"wage for volunteerTime = {wages.volunteerTime}")
            print(f"wage for standTime = {wages.standTime}")
            print(f"this is the unformatted time = {wageTime}")
            print(f"there are these many hours = {wageTimeHours}")
            if activity == 'volunteering' or 'volunteer stand time':
                wage=wages.volunteerTime
            elif activity == 'member stand time':
                wage= wages.standTime
            else:
                wage = 0
            
            incrementedEquity = targetEquity + wageTimeHours*wage
            obj.equity = incrementedEquity
            obj.save()
            my_form.cleaned_data['endTime'] = roundedTimeEnd
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
        naiveStart = datetime.datetime.strptime(obj.startTime, "%m/%d/%Y %I:%M %p")
        print(f"naive starttime {naiveStart}")
        naiveEnd = datetime.datetime.now()
        print(f"naive end {naiveEnd}")
        naiveEnd = naiveEnd.astimezone(local)
        # endLocal_dt = local.localize(naiveEnd, is_dst=None)
        print(f"localized end {naiveEnd}")
        current_time = naiveEnd.strftime("%m/%d/%Y %I:%M %p")
        endTime = datetime.datetime.strptime(current_time, "%m/%d/%Y %I:%M %p")
        elapsedTime = endTime - naiveStart
        print(f"endTime = {str(endTime)}")
        formattedEnd = endTime.strftime("%m/%d/%Y %I:%M %p")
        print(f"this is the formatted end {formattedEnd}")
        print(f"elapsed time = {elapsedTime}")
        unroundedTimeEnd = RoundTimeSignout(formattedEnd,obj.activity)
        roundedTimeEnd = unroundedTimeEnd.roundTime()
        obj.endTime = str(roundedTimeEnd)
        activity = obj.activity
        wages = EquityRates.objects.get(pk=1)
        wage = 0
        print(f"wages = {wages}")
        print(f"wage for volunteerTime = {wages.volunteerTime}")
        print(f"wage for standTime = {wages.standTime}")
        print(f"wage for sweatEquity = {wages.sweatEquity}")
        if activity == 'volunteering' or 'volunteer stand time':
            wage=wages.volunteerTime
        elif activity == 'member stand time':
           wage= wages.standTime
        else:
            wage = 0
        currentEquity = equity.equity
        payableTime = elapsedTime.seconds/60/60
        print(f"payable time = {payableTime}")
        print(f"paying the wage = {wage} for the activity {activity}")
        incrementedEquity = currentEquity + payableTime*wage
        equity.equity = incrementedEquity
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

def django_delete_request(request, username):
    if request.method == "POST":
        print(f"trying for id {username}")
        obj = User.objects.get(username=username)
        obj.delete()
        print("object deleted")
        return HttpResponseRedirect('/users')
    print("done deleting")

    return HttpResponseRedirect('/users')

def transactions_edit(request, id):
    my_form = RawTransactionForm()
    if request.method == "POST":
        my_form = RawTransactionForm(request.POST)
        obj = Transactions.objects.get(id=id)
        if my_form.is_valid():
            print(my_form.cleaned_data)
            obj.date = my_form.cleaned_data.get('date')
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
    bikePurchases = Transactions.objects.filter(Q(transactionType = 'Equity Bike Purchase') & Q(users_id = targetid)).values('date')
    shifts = Timelogs.objects.filter(users_id = targetid).count()
    numBikes = 0
    membershipDate = obj.membershipExp
    isvalid = 0
    print(f"{datetime.datetime.strftime(datetime.datetime.strptime(membershipDate,'%m/%d/%y'),'%m/%d/%y')} + {datetime.datetime.strftime(datetime.datetime.now(),'%m/%d/%y')}")
    if datetime.datetime.strftime(datetime.datetime.strptime(membershipDate,'%m/%d/%y'),'%m/%d/%y') < datetime.datetime.strftime(datetime.datetime.now(),'%m/%d/%y'):
        membershipExp = datetime.datetime.strftime(datetime.datetime.strptime(membershipDate,'%m/%d/%y'),'%m/%d/%y')
        isvalid = 1
    else:
        isvalid = 0
        membershipExp = 'null'
    print(f"isvalid {isvalid}")
    


    for bike in bikePurchases:
        print(bike['date'])
        if datetime.datetime.strptime(bike['date'],'%m/%d/%Y %I:%M %p') > (datetime.datetime.now()-datetime.timedelta(days=365)):
            numBikes+=1

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
    context = {"form": my_form, 'person':obj, 'transactions':transactions,'timelogs':timelogs,'numBikes':numBikes,'numShifts':shifts,'membershipExp':membershipExp,'isvalid':isvalid}
    return render(request, 'people_edit.html', context)

def transaction_delete_request(request, id):
    if request.method == "POST":
        print(f"trying for id {id}")
        obj = Transactions.objects.get(id=id)
        amount = obj.amount
        user = Users.objects.get(pk=obj.users_id)
        userEquity = user.equity
        newEquity = userEquity - amount
        user.equity = newEquity
        user.save()
        obj.delete()
        print("object deleted")
        return HttpResponseRedirect('/transactions')

def timelogs_delete_request(request, id):
    if request.method == "POST":
        print(f"trying for id {id}")
        obj = Timelogs.objects.get(id=id)
        startTime = obj.startTime
        endTime = obj.endTime
        activity = obj.activity
        wageTime = datetime.datetime.strptime(endTime,"%m/%d/%Y %I:%M %p") - datetime.datetime.strptime(startTime,"%m/%d/%Y %I:%M %p")
        wageTimeHours = wageTime.seconds/60/60
        wages = EquityRates.objects.get(pk=1)
        wage = 0
        if activity == 'volunteering' or 'volunteer stand time':
            wage=wages.volunteerTime
        elif activity == 'member stand time':
            wage= wages.standTime
        else:
            wage = 0
        user = Users.objects.get(pk=obj.users_id)
        userEquity = user.equity
        newEquity = userEquity - wage*wageTimeHours
        user.equity = newEquity
        user.save()
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
            users = Users.objects.filter(lastname__contains=search_request).values('firstname','lastname', 'middlename', 'id','phone')
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
        validation_query = request.GET.get('validation_query')
        listInput = validation_query.split()
        if len(listInput) < 2:
            return JsonResponse(['not enough characters'], safe=False)
        validation_first = listInput[0]
        validation_last = listInput[1]
        validation_phone = listInput[2]
        print(f"first name = {validation_first} and lastname = {validation_last}")
        if validation_first != '' and validation_phone != '' and validation_last != '':
            users = Users.objects.filter(lastname=validation_last, firstname=validation_first, phone__contains = validation_phone).values('id', 'equity')
            if not users:
                userList = ['no persons found']
            else:
                userList = list(users)
        else:
            userList = ['Enter Last name']
        print("returning userlist" + str(userList))
        return JsonResponse(userList, safe=False)

def charts(request):
    rates = EquityRates.objects.get(pk=1)
    my_form = ChangeEquityRates()
    hours_form = HoursReport()
    login_form = LoginReport()
    user_form = UserReport()
    range_form = ShiftsInRangeReport()
    if request.method == 'POST':
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
    # context = {"form": my_form}
    return render(request, 'charts.html',args)

def generate_report(request):
    response = HttpResponse(content_type='application/ms-excel')
    book = xlwt.Workbook(encoding='utf-8', style_compression = 0)
    rows = ['January', 'February', 'March', 'April', 'May','June','July','August','September','October','November','December']
    columns = ['Month','Volunteering','Stand Time','Shopping','Other','Total']
    userSet = Timelogs.objects.filter(endTime__isnull = False)
    volunteering = []
    sweatEquityNeg = book.add_sheet('sweat equity negative balance', cell_overwrite_ok = True)
    sweatEquityNeg.write(0,0, "Broke Spoke")
    sweatEquityNeg.write(1,0, "Sweat Equity Negative Balance ($)")
    currTimeNaive = datetime.datetime.now(timezone.utc)
    currTime = datetime.datetime.strftime(currTimeNaive, "%d/%m/%Y")
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
    bikePurchasers = Transactions.objects.filter(transactionType = 'Equity Bike Purchase')
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
    totalVolunteerDuration = 0
    totalStandTimeDuration = 0
    for volunteer in totalVolunteerSet:
        if volunteer.activity == 'volunteering':
            volunteerDuration = datetime.datetime.strptime(volunteer.endTime, "%m/%d/%Y %I:%M %p") - datetime.datetime.strptime(volunteer.startTime, "%m/%d/%Y %I:%M %p")
            volunteerDuration = (volunteerDuration.seconds//60//60)%60
            totalVolunteerDuration += volunteerDuration
            print(f"total volunteer duration {totalVolunteerDuration}")
        if volunteer.activity == 'member stand time' or volunteer.activity == 'stand time':
            standTimeDuration= datetime.datetime.strptime(volunteer.endTime, "%m/%d/%Y %I:%M %p") - datetime.datetime.strptime(volunteer.startTime, "%m/%d/%Y %I:%M %p")
            standTimeDuration = (standTimeDuration.seconds//60//60)%60
            totalStandTimeDuration += standTimeDuration
            print(f"total stand time duration {totalStandTimeDuration}")
    totalSE = Transactions.objects.aggregate(Sum('amount'))['amount__sum']
    print(f"this is totalSE={totalSE}")
    totalShopLogins = Timelogs.objects.count()
    bikesSold = len(Transactions.objects.filter(transactionType = 'Equity Bike Purchase'))
    bikeParts = len(Transactions.objects.filter(transactionType = 'Equity Parts Purchase'))
    keyMetrics.write(4,0, totalVolunteerDuration)
    keyMetrics.write(4,1,totalSE)
    keyMetrics.write(4,2,totalShopLogins)
    keyMetrics.write(4,3,bikesSold)
    keyMetrics.write(4,4,bikeParts)
    keyMetrics.write(4,5,totalStandTimeDuration)
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
    def roundTime(self):
        print("made it into roundtime")
        if self.activity == 'volunteering':
            newTime = datetime.datetime.strptime(self.time,'%m/%d/%Y %I:%M %p') - datetime.timedelta(minutes=datetime.datetime.strptime(self.time,'%m/%d/%Y %I:%M %p').minute % 15)
        else:
            m = self.time.split()
            p = m[-1:][0]
            hours, mints = m[1].split(':')
            if 15 <= int(mints) <= 45:
                mints = ':30'
            elif int(mints) < 15:
                mints = ':00'
            elif int(mints) > 45:
                mints = ':00'
                h = int(hours) + 1
                hours = str(h)
            newTime = datetime.datetime.strptime(str(m[0] + " " + str(hours) + str(mints) + " " + str(p)),'%m/%d/%Y %I:%M %p')

            
        return datetime.datetime.strftime(newTime,'%m/%d/%Y %I:%M %p')

class RoundTimeSignout:
    def __init__(self, time, activity):
        self.time = time
        self.activity = activity
    def roundTime(self):
        print(f"made it into roundtime signout for activity {self.activity}")
        if self.activity != 'volunteering':
            newTime = datetime.datetime.strptime(self.time,'%m/%d/%Y %I:%M %p') - datetime.timedelta(minutes=datetime.datetime.strptime(self.time,'%m/%d/%Y %I:%M %p').minute % 15)
        else:
            m = self.time.split()
            p = m[-1:][0]
            hours, mints = m[1].split(':')
            if 15 <= int(mints) <= 30:
                mints = ':30'
            elif 30 < int(mints) <= 45:
                mints = ':45'
            elif int(mints) < 15:
                mints = ':00'
            elif int(mints) > 45:
                mints = ':00'
                h = int(hours) + 1
                hours = str(h)
            newTime = datetime.datetime.strptime(str(m[0] + " " + str(hours) + str(mints) + " " + str(p)),'%m/%d/%Y %I:%M %p')
            print(f"this is the newTimeEnd= {newTime}")
            
        return datetime.datetime.strftime(newTime,'%m/%d/%Y %I:%M %p')
def generateQuery(activity):
    print(f"the activity is {activity}")
    if activity == 'volunteering':
        columnDataSet = Timelogs.objects.filter(activity = activity)
        # print(f"this is the internal for {activity} dataset {columnDataSet}")
    elif activity == 'stand time':
        columnDataSet = Timelogs.objects.filter(Q(activity = activity) | Q(activity='member stand time'))
        # print(f"this is the internal for {activity} dataset {columnDataSet}")
    elif activity == 'shopping':
        columnDataSet = Timelogs.objects.filter(activity = activity)
        # print(f"this is the internal for {activity} dataset {columnDataSet}")
    elif activity == 'other':
        columnDataSet = Timelogs.objects.filter(Q(activity = activity) | Q(activity='imported login'))
        # print(f"this is the internal for {activity} dataset {columnDataSet}")
    # print(f"this is the returned set {columnDataSet}")
    return columnDataSet

def generateQueryUnique(activity):
    print(f"the activity is {activity}")
    if activity == 'volunteering':
        columnDataSet = Timelogs.objects.filter(activity = activity).order_by().values('person','startTime','endTime').distinct('person','activity')
    elif activity == 'stand time':
        columnDataSet = Timelogs.objects.filter(Q(activity = activity) | Q(activity='member stand time')).order_by().values('person','startTime','endTime').distinct('person','activity')
    elif activity == 'shopping':
        columnDataSet = Timelogs.objects.filter(activity = activity).order_by().values('person','startTime','endTime').distinct('person','activity')
    elif activity == 'other':
        columnDataSet = Timelogs.objects.filter(Q(activity = activity) | Q(activity='imported login')).order_by().values('person','startTime','endTime').distinct('person','activity')
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
    columns = {'Volunteering':'volunteering','Stand Time':'stand time','Shopping':'shopping','Other':'other'}
    my_form = LoginReport()
    response = HttpResponse(content_type='application/ms-excel')
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

            for date in dates:
                customerLogin.write(row_count,0,monthDict[str(date.month)])
                
                column_count = 1
                for column in columns:
                    monthlyTotal = {}
                    columnDataSet= generateQuery(columns[column])
                    print(f"this is the dataset {columnDataSet}")
                    dateString = str(date)
                    monthToMatch = int(dateString[5:7])
                    yearToMatch = int(dateString[2:4])
                    print(monthToMatch)
                    print(yearToMatch)
                    for databaseDate in columnDataSet:
                        if monthToMatch == int(databaseDate.startTime[0:2]) and yearToMatch == int(databaseDate.endTime[6:8]):
                            print(f"within range of dateString {dateString}")
                            cellData = LogEntry(datetime.datetime.strptime(databaseDate.startTime,'%m/%d/%Y %I:%M %p'), datetime.datetime.strptime(databaseDate.endTime,'%m/%d/%Y %I:%M %p' ))
                            print(f"this is the duration {(cellData.duration().seconds//60//60)%60}")
                            monthlyTotal[monthToMatch] = monthlyTotal.get(monthToMatch,0)+int((cellData.duration().seconds//60//60)%60)
                    print(f"this is the current tally {monthlyTotal}")
                    customerLogin.write(row_count,column_count,monthlyTotal.get(int(date.month),0))
                    print(f"this is date.month {str(date.month)}")
                    column_count+=1
                row_count+=1
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
    columns = {'Volunteering':'volunteering','Stand Time':'stand time','Shopping':'shopping','Other':'other'}
    my_form = HoursReport()
    response = HttpResponse(content_type='application/ms-excel')
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

            for date in dates:
                customerLogin.write(row_count,0,monthDict[str(date.month)])
                uniqueCustomerLogin.write(row_count,0,monthDict[str(date.month)])
                
                column_count = 1
                for column in columns:
                    monthlyTotal = {}
                    uniqueMonthlyTotal = {}
                    columnDataSet= generateQuery(columns[column])
                    uniqueColumnDataSet= generateQueryUnique(columns[column])
                    print(f"this is the dataset for {columns[column]} = {columnDataSet}")
                    print(f"this is the unique dataset for {columns[column]} = {uniqueColumnDataSet}")
                    dateString = str(date)
                    monthToMatch = int(dateString[5:7])
                    yearToMatch = int(dateString[2:4])
                    print(monthToMatch)
                    print(yearToMatch)
                    for databaseDate in columnDataSet:
                        if monthToMatch == int(databaseDate.startTime[0:2]) and yearToMatch == int(databaseDate.endTime[6:8]):
                            print(f" {databaseDate} passes the month to match {monthToMatch}")
                            monthlyTotal[monthToMatch] = monthlyTotal.get(monthToMatch,0)+1
                    for databaseDate in uniqueColumnDataSet:
                        print(f"this is the date to check {databaseDate} ")
                        if monthToMatch == int(databaseDate['startTime'][0:2]) and yearToMatch == int(databaseDate['endTime'][6:8]):
                            print(f" {int(databaseDate['startTime'][0:2])} passes the month to match in unique set {monthToMatch}")
                            uniqueMonthlyTotal[monthToMatch] = uniqueMonthlyTotal.get(monthToMatch,0)+1
                    print(f"this is the current tally {monthlyTotal}")
                    customerLogin.write(row_count,column_count,monthlyTotal.get(int(date.month),0))
                    uniqueCustomerLogin.write(row_count,column_count,uniqueMonthlyTotal.get(int(date.month),0))
                    print(f"this is date.month {str(date.month)}")
                    column_count+=1
                row_count+=1
            book.save(response)
    return response

def user_report(request):
    my_form = UserReport()
    response = HttpResponse(content_type='application/ms-excel')
    book = xlwt.Workbook(encoding='utf-8', style_compression = 0)
    customerLogs = book.add_sheet('customer logs', cell_overwrite_ok = True)
    if request.method == 'POST':
        my_form = UserReport(request.POST)
        if my_form.is_valid():
            userLogs = Timelogs.objects.filter(person = my_form.cleaned_data['person']).order_by('startTime').values('startTime', 'endTime','person')
            row_count = 4
            column_count = 0
            customerLogs.write(0,0,"Broke Spoke")
            customerLogs.write(1,0,"Volunteer shifts")
            customerLogs.write(2,0,my_form.cleaned_data['person'])
            customerLogs.write(3,0,f"date range: {my_form.cleaned_data['startDate']} - {my_form.cleaned_data['endDate']}")
            for user in userLogs:
                cellData = LogEntry(datetime.datetime.strptime(user['startTime'],'%m/%d/%Y %I:%M %p'), datetime.datetime.strptime(user['endTime'],'%m/%d/%Y %I:%M %p' ))
                userDuration = (cellData.duration().seconds//60//60)%60
                print(f"this is the duration {userDuration}")
                print(f"date = {user['startTime'] } duration = {userDuration}  ")
                if datetime.datetime.strptime(user['startTime'][0:8],'%m/%d/%y') >= datetime.datetime.strptime(my_form.cleaned_data['startDate'],'%m/%d/%y') and datetime.datetime.strptime(user['startTime'][0:8],'%m/%d/%y') <= datetime.datetime.strptime(my_form.cleaned_data['endDate'],'%m/%d/%y'):
                    customerLogs.write(row_count,0,user['startTime'][0:8])
                    customerLogs.write(row_count,2,userDuration)
                    row_count+=1
                else:
                    print(f"there is no match within range {datetime.datetime.strptime(user['startTime'][0:8],'%m/%d/%y')}")

            startDate = my_form.cleaned_data['startDate']
            endDate = my_form.cleaned_data['endDate']
            print(f"startDate = {startDate} and  endDate= {endDate}")
            formattedStartDate = datetime.datetime.strptime(startDate,'%m/%d/%y')
            formattedEndDate = datetime.datetime.strptime(endDate,'%m/%d/%y')
            userDuration = formattedEndDate - formattedStartDate
    book.save(response)
    return response
def shiftsInRange(request):
    my_form = ShiftsInRangeReport()
    response = HttpResponse(content_type='application/ms-excel')
    book = xlwt.Workbook(encoding='utf-8', style_compression = 0)
    customerLogs = book.add_sheet('shifts in range', cell_overwrite_ok = True)
    usermap = {}
    if request.method == 'POST':
        my_form = ShiftsInRangeReport(request.POST)
        if my_form.is_valid():
            userLogs = Timelogs.objects.all()
            row_count = 5
            column_count = 0
            customerLogs.write(0,0,"Broke Spoke")
            customerLogs.write(1,0,"Volunteer shifts")
            customerLogs.write(3,0,f"date range: {my_form.cleaned_data['startDate']} - {my_form.cleaned_data['endDate']}")
            customerLogs.write(4,0,"Person")
            customerLogs.write(4,2,"# of logins")
            for user in userLogs:
                formattedStart = user.startTime.split(" ")
                if datetime.datetime.strptime(formattedStart[0],'%m/%d/%Y') >= datetime.datetime.strptime(my_form.cleaned_data['startDate'],'%m/%d/%y') and datetime.datetime.strptime(formattedStart[0],'%m/%d/%Y') <= datetime.datetime.strptime(my_form.cleaned_data['endDate'],'%m/%d/%y'):
                    usermap[user.person]= usermap.get(user.person,0)+1
            for person in usermap:
                if usermap[person] >= my_form.cleaned_data['numShifts']:
                    customerLogs.write(row_count,0,person)
                    customerLogs.write(row_count,2,usermap[person])
                    row_count+=1


    book.save(response)
    return response