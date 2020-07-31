from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from .models import EquityRates, Transactions, Users, Timelogs, NewSystemUser
from .forms import ShiftsInRangeReport,UserReport,HoursReport, LoginReport,ChangeEquityRates, RawUserForm, RawTransactionForm, RawTimelogsForm, NewSignIn, ChargeEquity, CreateNewSystemUser
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
from datetime import timezone, timedelta
from django.contrib.auth.decorators import login_required
from django.core import serializers
import csv
from django.db.models import F,Q, UniqueConstraint
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
        if maxObject > abs(elapsedTime):
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
            person_middle = personList[1]
            person_last = personList[2]
            print(f"this is the person signing in={person}")
            targetUser = Users.objects.get(lastname__iexact=person_last, firstname__iexact=person_first,middlename__iexact=person_middle)
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
        elif transaction_form.is_valid():
            dateToFormat = transaction_form.cleaned_data['date']
            cleanedDate = datetime.datetime.strftime(dateToFormat, "%m/%d/%Y %I:%M %p")
            transaction_form.cleaned_data['date'] = cleanedDate
            print(transaction_form.cleaned_data)
            person = transaction_form.cleaned_data['transactionPerson']
            personList = person.split()
            person_first = personList[0]
            person_middle = personList[1]
            person_last = personList[2]
            transaction_form.cleaned_data['paymentType'] = 'Sweat Equity'
            transaction_form.cleaned_data['paymentStatus'] = 'Complete'
            print(f"this is the person signing in={person}")
            targetUser = Users.objects.get(lastname__iexact=person_last, firstname__iexact=person_first,middlename__iexact=person_middle)
            print(f"signing in user with id {targetUser.id}")
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
            return HttpResponseRedirect("dashboard")
        else:
            print(my_form.errors)
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
                my_form.cleaned_data['waiverAcceptedDate'] = datetime.datetime.strftime(datetime.datetime.now(),'%m/%d/%y')
                
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
            person = my_form.cleaned_data['transactionPerson'].split()
            amount = my_form.cleaned_data['amount']
            obj = Users.objects.get(firstname__iexact=person[0], middlename__iexact = person[1], lastname__iexact = person[2])
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
            obj = Users.objects.get(firstname__iexact=person[0], middlename__iexact = person[1], lastname__iexact = person[2])
            targetId = obj.id
            targetEquity = obj.equity
            activity = my_form.cleaned_data['activity']
            my_form.cleaned_data['users_id'] = targetId
            wages = EquityRates.objects.get(pk=1)
            wage = 0
            print(f"setting wage for activity {activity}")
            print(f"wages = {wages}")
            print(f"wage for volunteerTime = {wages.volunteerTime}")
            print(f"wage for standTime = {wages.standTime}")
            print(f"this is the unformatted time = {wageTime}")
            print(f"there are these many hours = {wageTimeHours}")
            if activity == 'Volunteering' or activity == 'Volunteer Stand Time':
                print("volunteer check")
                wage=wages.volunteerTime
            elif activity == 'Member Stand Time':
                wage= wages.standTime
            else:
                wage = 0
            incrementedEquity = targetEquity + wageTimeHours*wage
            if incrementedEquity > 250:
                obj.equity = 250
            else:
                obj.equity = incrementedEquity
            print(f"this is the recieved equity {wageTimeHours*wage} with wage = {wage}")
            
            obj.save()
            my_form.cleaned_data['endTime'] = roundedTimeEnd
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
    # print(f"name = {person}, activity = {activity}, startTime = {startTime}")
    # data = {'csrfmiddlewaretoken':[f"{request.POST['csrfmiddlewaretoken']}",f"{request.POST['csrfmiddlewaretoken']}"],'person':[name],'activity':[activity],'startTime':[startTime.replace('_','/')]}
    # print(f"trying to send this data {data}")
    print(f"this it the port request {request.POST}")
    my_form = NewSignIn(request.POST)
    if my_form.is_valid():
        print("valid form")
        print(my_form.cleaned_data)
        person = my_form.cleaned_data['person']
        personList = person.split()
        person_first = personList[0]
        person_middle = personList[1]
        person_last = personList[2]
        targetUser = Users.objects.get(lastname__iexact=person_last, firstname__iexact=person_first,middlename__contains=person_middle)
        my_form.cleaned_data['users_id'] = targetUser.id
        local = pytz.timezone ("US/Eastern")
        naiveTime = datetime.datetime.now()
        awareTime = naiveTime.astimezone(local)
        cleanedDate = datetime.datetime.strftime(awareTime, "%m/%d/%Y %I:%M %p")
        unroundedTime = RoundTime(cleanedDate,my_form.cleaned_data['activity'])
        roundedTime = unroundedTime.roundTime()
        my_form.cleaned_data['startTime'] = roundedTime
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
    obj = Timelogs.objects.filter(endTime__isnull=False).values('id','person','startTime','endTime','activity')
    for object in obj:
        volunteerDuration = datetime.datetime.strptime(object['endTime'], "%m/%d/%Y %I:%M %p") - datetime.datetime.strptime(object['startTime'], "%m/%d/%Y %I:%M %p")
        object['hours'] = (float(volunteerDuration.seconds/60/60))
        
    args = {'obj': obj, 'timelogs_page': "active"}
    return render(request, 'timelogs.html', args)

@login_required(login_url='/')
def transactions(request):
    timelogs = Timelogs.objects.filter(endTime__isnull=False).values('id','startTime','person','activity','endTime','users_id')
    obj = Transactions.objects.all().values('id','transactionPerson','transactionType','date','amount','paymentType','users_id')
    timelogList = list(timelogs)
    wages = EquityRates.objects.get(pk=1)
    transactionList = list(obj)
    for element in timelogList:
        element['type'] = 'Timelog'
        wage = 0
        volunteerDuration = datetime.datetime.strptime(element['endTime'], "%m/%d/%Y %I:%M %p") - datetime.datetime.strptime(element['startTime'], "%m/%d/%Y %I:%M %p")
        if element['activity'] == 'Volunteering':
            wage=wages.volunteerTime
        elif element['activity'] == 'Member Stand Time' or 'Volunteer Stand Time':
           wage= wages.standTime
        else:
            wage = 0
        element['amount'] = float(volunteerDuration.seconds/60/60)*wage
        element['date'] = element['endTime']
        element['transactionPerson'] = element['person']
        element['paymentType'] = 'Equity'
        element['transactionType'] = element['activity']
    finalList = timelogList + transactionList
    
    print(finalList)
    args = {'obj': finalList, 'transactions_page': "active"}
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


def signout(request, id, payment):
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
        
        print(f"endTime = {str(endTime)}")
        formattedEnd = endTime.strftime("%m/%d/%Y %I:%M %p")
        print(f"this is the formatted end {formattedEnd}")
        
        unroundedTimeEnd = RoundTimeSignout(formattedEnd,obj.activity)
        roundedTimeEnd = unroundedTimeEnd.roundTime()
        elapsedTime = datetime.datetime.strptime(roundedTimeEnd,"%m/%d/%Y %I:%M %p") - naiveStart
        print(f"elapsed time = {elapsedTime}")
        obj.endTime = str(roundedTimeEnd)
        activity = obj.activity
        wages = EquityRates.objects.get(pk=1)
        wage = 0
        print(f"wages = {wages}")
        print(f"wage for volunteerTime = {wages.volunteerTime}")
        print(f"wage for standTime = {wages.standTime}")
        print(f"wage for sweatEquity = {wages.sweatEquity}")
        membershipDate = equity.membershipExp
        isvalid = 0
    
        todayDate = datetime.datetime.now()
        if membershipDate:
            membershipDateFormatted = datetime.datetime.strptime(membershipDate,'%m/%d/%y')
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
        print(f"isvalid {isvalid} with activity {activity}")

        if activity == 'Volunteering':
            print("confirmed volunteer")
            wage=wages.volunteerTime
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
        payableTime = elapsedTime.seconds/60/60
        print(f"payable time = {payableTime}")
        print(f"paying the wage = {wage} for the activity {activity}")
        incrementedEquity = currentEquity + payableTime*wage
        if incrementedEquity >250:
            equity.equity = 250
        else:
            equity.equity = incrementedEquity
        equity.save()
        obj.save()
        print(f'new obj endTime {obj.endTime}')
        return HttpResponseRedirect('/dashboard')
        print("should be done by now")
    return HttpResponseRedirect('/dashboard')

def signoutPublic(request, id, payment):
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
        
        print(f"endTime = {str(endTime)}")
        formattedEnd = endTime.strftime("%m/%d/%Y %I:%M %p")
        print(f"this is the formatted end {formattedEnd}")
        
        unroundedTimeEnd = RoundTimeSignout(formattedEnd,obj.activity)
        roundedTimeEnd = unroundedTimeEnd.roundTime()
        obj.endTime = str(roundedTimeEnd)
        elapsedTime = datetime.datetime.strptime(roundedTimeEnd,"%m/%d/%Y %I:%M %p") - naiveStart
        print(f"elapsed time = {elapsedTime}")
        activity = obj.activity
        wages = EquityRates.objects.get(pk=1)
        wage = 0
        print(f"wages = {wages}")
        print(f"wage for volunteerTime = {wages.volunteerTime}")
        print(f"wage for standTime = {wages.standTime}")
        print(f"wage for sweatEquity = {wages.sweatEquity}")
        membershipDate = equity.membershipExp
        isvalid = 0
    
        todayDate = datetime.datetime.now()
        if membershipDate:
            membershipDateFormatted = datetime.datetime.strptime(membershipDate,'%m/%d/%y')
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
        print(f"isvalid {isvalid}")
        if activity == 'Volunteering':
            wage=wages.volunteerTime
        elif activity == 'Shopping' or "Other":
            wage = 0
        elif activity == 'Member Stand Time' or 'Stand Time' or 'Volunteer Stand Time':
            if isvalid == 1 or int(payment) == 1:
                wage = 0
            else:
                wage= wages.standTime
        else:
            wage = 0
        currentEquity = equity.equity
        payableTime = elapsedTime.seconds/60/60
        print(f"payable time = {payableTime}")
        print(f"paying the wage = {wage} for the activity {activity}")
        incrementedEquity = currentEquity + payableTime*wage
        if incrementedEquity > 250:
            equity.equity = 250
            
        else:
            equity.equity = incrementedEquity
        equity.save()
        obj.save()
        print(f'new obj endTime {obj.endTime}')
        summary = {"activity":obj.activity,"name":obj.person,"startTime": str(obj.startTime).split(" ")[1], "endTime":str(obj.endTime).split(" ")[1],"elapsed":round(payableTime,2),"wage":wage,"currentBalance":incrementedEquity, "earned":int(payableTime*wage)}
        new_user = RawUserForm()
        currentUsers = Timelogs.objects.filter(endTime__isnull=True)
        obj = Users.objects.all()
        my_form = NewSignIn()
        print("successful signout achieved")
        args = {'obj': obj,'form':my_form,'currentUsers':currentUsers, 'user_form':new_user,'summary':summary}
        return render(request, 'signin.html', args)
        print("should be done by now")
    return HttpResponseRedirect('/signin')

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
    fieldsDict = {'person':obj.person,'activity':obj.activity,'startTime':obj.startTime,'endTime':obj.endTime}
    

    for field in fieldsDict:
        my_form.fields[field].widget.attrs['placeholder'] = fieldsDict.get(field)
        print(fieldsDict.get(field))
    if request.method == "POST":
        my_form = RawTimelogsForm(request.POST)
        if my_form.is_valid():
            print(my_form.cleaned_data)
            obj.person = my_form.cleaned_data.get('person')
            obj.activity = my_form.cleaned_data.get('activity')
            obj.startTime = datetime.datetime.strftime(my_form.cleaned_data.get('startTime'),"%m/%d/%Y %I:%M %p")
            obj.endTime = datetime.datetime.strftime(my_form.cleaned_data.get('endTime'),"%m/%d/%Y %I:%M %p")
            print(f"changing starttime and endtime {my_form.cleaned_data.get('startTime')} and {my_form.cleaned_data.get('endTime')}")
            obj.save()
            print("updated forms")
            # Transactions.objects.create(**my_form.cleaned_data)
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
    timelogs = Timelogs.objects.filter(users_id=targetid).values()
    for timelog in timelogs:
        if timelog['endTime']:
            volunteerDuration = datetime.datetime.strptime(timelog['endTime'], "%m/%d/%Y %I:%M %p") - datetime.datetime.strptime(timelog['startTime'], "%m/%d/%Y %I:%M %p")
            timelog['hours'] = float(volunteerDuration.seconds/60/60)
    bikePurchases = Transactions.objects.filter(Q(transactionType = 'Bike Purchase') & Q(users_id = targetid)).values('date')
    shifts = Timelogs.objects.filter(Q(users_id = targetid) & Q(activity='Volunteering')).count()
    numBikes = 0
    membershipDate = obj.membershipExp
    isvalid = 0
    naiveEnd = datetime.datetime.now()
    local = pytz.timezone ("US/Eastern")
    endTime = naiveEnd.astimezone(local)
    
    if membershipDate:
        membershipDateFormatted = datetime.datetime.strptime(membershipDate,'%m/%d/%y')
        membershipDateFormatted = membershipDateFormatted.astimezone(local)
        print(f"membershipDateFormatted = {membershipDateFormatted}")
        print(f"todayDate = {endTime}")
        print(f"{membershipDateFormatted} < {endTime}")
        if membershipDateFormatted >  endTime:
            membershipExp = datetime.datetime.strftime(datetime.datetime.strptime(membershipDate,'%m/%d/%y'),'%m/%d/%y')
            isvalid = 1
            print("exp has not passed yet")
        else:
            isvalid = 0
            membershipExp = 'null'
    else:
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

    timelogList = list(Timelogs.objects.filter(Q(users_id = targetid) & Q(endTime__isnull = False)).values())
    transactionList = list(transactions)
    wages = EquityRates.objects.get(pk=1)
    for element in timelogList:
        element['type'] = 'Timelog'
        wage = 0
        volunteerDuration = datetime.datetime.strptime(element['endTime'], "%m/%d/%Y %I:%M %p") - datetime.datetime.strptime(element['startTime'], "%m/%d/%Y %I:%M %p")
        if element['activity'] == 'Volunteering':
            wage=wages.volunteerTime
        elif element['activity'] == 'Member Stand Time' or 'Volunteer Stand Time':
            wage= wages.standTime
        else:
            wage = 0
        element['amount'] = float(volunteerDuration.seconds/60/60)*wage
        element['date'] = element['endTime']
        element['transactionPerson'] = element['person']
        element['paymentType'] = 'Equity'
        element['transactionType'] = element['activity']
    finalList = timelogList + transactionList
    context = {"form": my_form, 'person':obj, 'transactions':transactions,'timelogs':timelogs,'numBikes':numBikes,'numShifts':shifts,'membershipExp':membershipExp,'isvalid':isvalid,'obj':finalList}
    return render(request, 'people_edit.html', context)

def transaction_delete_request(request, id):
    if request.method == "POST":
        print(f"trying for id {id}")
        obj = Transactions.objects.get(id=id)
        obj.delete()
        print("object deleted")
        return HttpResponseRedirect('/transactions')

def timelogs_delete_request(request, id):
    print(f"this is the request{request.get_full_path()}")
    if request.method == "POST":
        print(f"trying for id {id}")
        obj = Timelogs.objects.get(id=id) 
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
            print(f"searchtext in if = {search_request}")
            users = Users.objects.filter(lastname__icontains=search_request).values('firstname','lastname', 'middlename', 'id','phone')
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
        validation_middle = listInput[1]
        validation_last = listInput[2]
        print(f"first name = {validation_first} and lastname = {validation_last}")
        if validation_first != '' and validation_middle != '' and validation_last != '':
            users = Users.objects.filter(lastname__iexact=validation_last, firstname__iexact=validation_first, middlename__iexact = validation_middle).values('id', 'equity')
            if not users:
                userList = ['no persons found']
            else:
                userList = list(users)
        else:
            userList = ['Enter Last name']
        print("returning userlist" + str(userList))
        return JsonResponse(userList, safe=False)

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
        print(f"this is the post request for charts{request.POST}")
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
    totalVolunteerDuration = 0
    totalStandTimeDuration = 0
    for volunteer in totalVolunteerSet:
        if volunteer.activity == 'Volunteering' and volunteer.endTime != None:
            volunteerDuration = datetime.datetime.strptime(volunteer.endTime, "%m/%d/%Y %I:%M %p") - datetime.datetime.strptime(volunteer.startTime, "%m/%d/%Y %I:%M %p")
            volunteerDuration = (volunteerDuration.seconds//60//60)%60
            totalVolunteerDuration += volunteerDuration
            print(f"total volunteer duration {totalVolunteerDuration}")
        if volunteer.activity == 'Member Stand Time' or volunteer.activity == 'Stand Time' and volunteer.endTime != None:
            standTimeDuration= datetime.datetime.strptime(volunteer.endTime, "%m/%d/%Y %I:%M %p") - datetime.datetime.strptime(volunteer.startTime, "%m/%d/%Y %I:%M %p")
            standTimeDuration = (standTimeDuration.seconds//60//60)%60
            totalStandTimeDuration += standTimeDuration
            print(f"total stand time duration {totalStandTimeDuration}")
    totalSE = Transactions.objects.aggregate(Sum('amount'))['amount__sum']
    print(f"this is totalSE={totalSE}")
    totalShopLogins = Timelogs.objects.count()
    bikesSold = len(Transactions.objects.filter(transactionType = 'Bike Purchase'))
    bikeParts = len(Transactions.objects.filter(transactionType = 'Parts Purchase'))
    keyMetrics.write(4,0, totalVolunteerDuration)
    keyMetrics.write(4,1,totalSE)
    keyMetrics.write(4,2,totalShopLogins)
    keyMetrics.write(4,3,bikesSold)
    keyMetrics.write(4,4,bikeParts)
    keyMetrics.write(4,5,totalStandTimeDuration)
    members = Users.objects.exclude(membershipExp = '').values('firstname', 'middlename','lastname','membershipExp','email')
    memberSheet.write(0,0,"List of members both active and inactive")
    memberSheet.write(1,0,"Name")
    memberSheet.write(1,1,"Active/Inactive")
    memberSheet.write(1,2,"Date of Expiration")
    memberSheet.write(1,3,"Email")
    memberRow = 2
    for member in members:
        membershipDate = member['membershipExp']
        isvalid = 0
        todayDate = datetime.datetime.now()
        if membershipDate:
            membershipDateFormatted = datetime.datetime.strptime(membershipDate,'%m/%d/%y')
            print(f"membershipDateFormatted = {membershipDateFormatted}")
            print(f"todayDate = {todayDate}")
            print(f"{membershipDateFormatted} < {todayDate}")
            if membershipDateFormatted >  todayDate:
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
        print(f"isvalid {isvalid}")

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
        if self.activity == 'Volunteering':
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
                if int(hours) == 12:
                    h = 1
                else:
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
        if self.activity != 'Volunteering':
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
                if int(hours) == 12:
                    h = 1
                else:
                    h = int(hours) + 1
                hours = str(h)
            newTime = datetime.datetime.strptime(str(m[0] + " " + str(hours) + str(mints) + " " + str(p)),'%m/%d/%Y %I:%M %p')
            print(f"this is the newTimeEnd= {newTime}")
            
        return datetime.datetime.strftime(newTime,'%m/%d/%Y %I:%M %p')
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
    columns = {'Volunteering':'Volunteering','Stand Time':'Stand time','Shopping':'Shopping','Other':'Other'}
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
                        if databaseDate.endTime != None:
                            if monthToMatch == int(databaseDate.startTime[0:2]) and yearToMatch == int(databaseDate.endTime[6:8]):
                                print(f"within range of dateString {dateString}")
                                cellData = LogEntry(datetime.datetime.strptime(databaseDate.startTime,'%m/%d/%Y %I:%M %p'), datetime.datetime.strptime(databaseDate.endTime,'%m/%d/%Y %I:%M %p' ))
                                print(f"this is the duration {(cellData.duration().seconds//60//60)%60}")
                                monthlyTotal[monthToMatch] = monthlyTotal.get(monthToMatch,0)+int((cellData.duration().seconds//60//60)%60)
                    print(f"this is the current tally {monthlyTotal}")
                    customerLogin.write(row_count,column_count,monthlyTotal.get(int(date.month),0))
                    print(f"this is date.month {str(date.month)}")
                    column_count+=1
                customerLogin.write(row_count,5,xlwt.Formula(f'SUM(B{row_count+1}:E{row_count+1})'))
                
                row_count+=1
            customerLogin.write(row_count+1,5,xlwt.Formula(f'SUM(F5:F{row_count+1})'))
                
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
                        if databaseDate.endTime != None:
                            if monthToMatch == int(databaseDate.startTime[0:2]) and yearToMatch == int(databaseDate.endTime[6:8]):
                                print(f" {databaseDate} passes the month to match {monthToMatch}")
                                monthlyTotal[monthToMatch] = monthlyTotal.get(monthToMatch,0)+1
                    for databaseDate in uniqueColumnDataSet:
                        print(f"this is the date to check {databaseDate} ")
                        if databaseDate['endTime'] != None:
                            if monthToMatch == int(databaseDate['startTime'][0:2]) and yearToMatch == int(databaseDate['endTime'][6:8]):
                                print(f" {int(databaseDate['startTime'][0:2])} passes the month to match in unique set {monthToMatch}")
                                uniqueMonthlyTotal[monthToMatch] = uniqueMonthlyTotal.get(monthToMatch,0)+1
                    print(f"this is the current tally {monthlyTotal}")
                    customerLogin.write(row_count,column_count,monthlyTotal.get(int(date.month),0))
                    uniqueCustomerLogin.write(row_count,column_count,uniqueMonthlyTotal.get(int(date.month),0))
                    print(f"this is date.month {str(date.month)}")
                    column_count+=1
                    customerLogin.write(row_count,5,xlwt.Formula(f'SUM(B{row_count+1}:E{row_count+1})'))
                    uniqueCustomerLogin.write(row_count,5,xlwt.Formula(f'SUM(B{row_count+1}:E{row_count+1})'))
                row_count+=1
            customerLogin.write(row_count+2,5,xlwt.Formula(f'SUM(F5:F{row_count+1})'))
            uniqueCustomerLogin.write(row_count+2,5,xlwt.Formula(f'SUM(F5:F{row_count+1})'))
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
            userLogs = Timelogs.objects.filter(person = my_form.cleaned_data['person']).order_by('startTime').values('startTime', 'endTime','person')
            row_count = 4
            column_count = 0
            customerLogs.write(0,0,"Broke Spoke")
            customerLogs.write(1,0,"Volunteer shifts")
            customerLogs.write(2,0,my_form.cleaned_data['person'])
            customerLogs.write(3,0,f"date range: {my_form.cleaned_data['startDate']} - {my_form.cleaned_data['endDate']}")
            for user in userLogs:
                if user['endTime'] != None:
                    cellData = LogEntry(datetime.datetime.strptime(user['startTime'],'%m/%d/%Y %I:%M %p'), datetime.datetime.strptime(user['endTime'],'%m/%d/%Y %I:%M %p' ))
                    userDuration = (cellData.duration().seconds//60//60)%60
                    print(f"this is the duration {userDuration}")
                    print(f"date = {user['startTime'] } duration = {userDuration}  ")
                    if user['endTime'] != None:
                        if datetime.datetime.strptime(user['startTime'][0:8],'%m/%d/%y') >= datetime.datetime.strptime(my_form.cleaned_data['startDate'],'%m/%d/%y') and datetime.datetime.strptime(user['startTime'][0:8],'%m/%d/%y') <= datetime.datetime.strptime(my_form.cleaned_data['endDate'],'%m/%d/%y'):
                            customerLogs.write(row_count,0,user['startTime'][0:8])
                            customerLogs.write(row_count,2,userDuration)
                            row_count+=1
                        else:
                            print(f"there is no match within range {datetime.datetime.strptime(user['startTime'][0:8],'%m/%d/%y')}")
            customerLogs.write(row_count,0,"Total")
            customerLogs.write(row_count,2,xlwt.Formula(f'SUM(C5:C{row_count})'))

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
    response['Content-Disposition'] = 'attachment; filename="shift-report.xls"'
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
            customerLogs.write(row_count,0,"Total")
            customerLogs.write(row_count,2,xlwt.Formula(f'SUM(C6:C{row_count})'))


    book.save(response)
    return response
