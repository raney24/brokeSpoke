from django import forms
from .models import Users, Timelogs, Transactions
from tempus_dominus.widgets import DatePicker, TimePicker, DateTimePicker
from django.contrib.auth.models import User
from .widgets import XDSoftDateTimePickerInput
import pytz
import datetime
from datetime import timezone, timedelta
import floppyforms as forms



class RawUserForm(forms.Form):
    firstname           = forms.CharField(label="First name")
    middlename          = forms.CharField(label="Middle name or initial")
    lastname            = forms.CharField(label="Last name")
    waiverAcceptedDate  = forms.DateTimeField(input_formats=['%d/%m/%Y %H:%M'],widget=XDSoftDateTimePickerInput())
    membershipExp       = forms.DateTimeField(input_formats=['%d/%m/%Y %H:%M'],widget=XDSoftDateTimePickerInput())
    birthdate           = forms.DateTimeField(input_formats=['%d/%m/%Y %H:%M'],widget=XDSoftDateTimePickerInput())
    email               = forms.CharField(label="E-mail",required=False)
    phone               = forms.CharField(label="phone",required=False)
    emergencyName       = forms.CharField(label = "Emergency Contact Name", required=False)
    relation            = forms.CharField(label = "relation", required=False)
    emergencyPhone      = forms.CharField(label = " Emergency Contact Phone",required=False)

class RawTransactionForm(forms.Form):
    TRANSACTION_CHOICES = (
        ('Equity Bike Purchase', 'Equity Bike Purchase'),
        ('Equity Parts Purchase', 'Equity Parts Purchase'),
    )
    PAYMENT_CHOICES = (
        ('Cash/Credit', 'Cash/Credit'),
        ('Sweat Equity', 'Sweat Equity'),
    )
    STATUS_CHOICES = (
        ('Complete', 'Complete'),
        ('Pending', 'Pending'),
    )
    person              = forms.CharField(label = "Person" )
    transactionType     = forms.ChoiceField(label = "transaction Type", choices = TRANSACTION_CHOICES )
    amount              = forms.IntegerField(label = "Amount")
    date                = forms.DateTimeField(input_formats=['%d/%m/%Y %H:%M'],widget=XDSoftDateTimePickerInput())
    paymentType         = forms.ChoiceField(label = "payment Type", choices = PAYMENT_CHOICES )
    paymentStatus       = forms.ChoiceField(label = "Payment Status", choices = STATUS_CHOICES )    
class RawTimelogsForm(forms.Form):
    SIGN_IN_CHOICES = (
        ('volunteering', 'volunteering'),
        ('member stand time', 'member stand time'),
        ('stand time', 'stand time'),
        ('shopping', 'shopping'),
        ('other', 'other'),
        ('imported login', 'imported login'),
    )
    person              = forms.CharField(label = "Person" )
    activity            = forms.ChoiceField(label = "Activity", choices = SIGN_IN_CHOICES )
    startTime           = forms.DateTimeField(input_formats=['%d/%m/%Y %H:%M'],widget=XDSoftDateTimePickerInput())
    endTime             = forms.DateTimeField(input_formats=['%d/%m/%Y %H:%M'],widget=XDSoftDateTimePickerInput())

class NewSignIn(forms.Form):
    SIGN_IN_CHOICES = (
        ('volunteering', 'volunteering'),
        ('member stand time', 'member stand time'),
        ('stand time', 'stand time'),
        ('shopping', 'shopping'),
        ('other', 'other'),
        ('imported login', 'imported login'),
    )
    local = pytz.timezone ("US/Eastern")
    currentTime = datetime.datetime.now()
    # naive = datetime.datetime.strftime(currentTime, "%d/%m/%Y %H:%M")
    local_dt = local.localize(currentTime, is_dst=None)
    currentTime = local_dt.strftime('%d/%m/%Y %H:%M')
    person              = forms.CharField(label = "Person" )
    activity            = forms.ChoiceField(label = "Activity", choices = SIGN_IN_CHOICES )
    startTime           = forms.CharField(initial=str(currentTime), label = "Start Time",widget=XDSoftDateTimePickerInput())
    


class ChargeEquity(forms.Form):
    TRANSACTION_CHOICES = (
        ('Equity Bike Purchase', 'Equity Bike Purchase'),
        ('Equity Parts Purchase', 'Equity Parts Purchase'),
    )
    person              = forms.CharField(label = "Person" )
    transactionType     = forms.ChoiceField(label = "transaction Type", choices = TRANSACTION_CHOICES )
    amount              = forms.IntegerField(label = "Amount")
    date                = forms.DateTimeField(input_formats=['%d/%m/%Y %H:%M'],widget=XDSoftDateTimePickerInput())

class CreateNewSystemUser(forms.Form):
    SYSTEM_USER_CHOICES = (
        ('App Admin', 'App Admin'),
        ('Shop Admin', 'Shop Admin'),
        ('Kiosk', 'Kiosk'),
    )
    username              = forms.CharField(label = "Username" )
    role                  = forms.ChoiceField(label = "Role", choices = SYSTEM_USER_CHOICES )
    email                 = forms.EmailField(label = "Email")
    password              = forms.CharField( widget=forms.PasswordInput)    

class ChangeEquityRates(forms.Form):
    sweatEquity = forms.IntegerField(label = 'sweat equity')
    standTime = forms.IntegerField(label = 'stand time')
    volunteerTime = forms.IntegerField(label = 'volunteer time')