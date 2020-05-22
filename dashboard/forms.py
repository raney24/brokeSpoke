from django import forms
import datetime
from .models import Users, Timelogs, Transactions
from tempus_dominus.widgets import DatePicker, TimePicker, DateTimePicker
from django.contrib.auth.models import User

class RawUserForm(forms.Form):
    firstname           = forms.CharField(label="First name")
    middlename          = forms.CharField(label="Middle name or initial")
    lastname            = forms.CharField(label="Last name")
    waiverAcceptedDate  = forms.DateTimeField(
        widget=DateTimePicker(
            options={
                'useCurrent': True,
                'collapse': False,
            },
            attrs={
                'append': 'fa fa-calendar',
                'icon_toggle': True,
            }
        ),
    )
    membershipExp       = forms.DateTimeField(
        widget=DateTimePicker(
            options={
                'useCurrent': True,
                'collapse': False,
            },
            attrs={
                'append': 'fa fa-calendar',
                'icon_toggle': True,
            }
        ),
    )
    birthdate           = forms.DateTimeField(
        widget=DateTimePicker(
            options={
                'useCurrent': True,
                'collapse': False,
            },
            attrs={
                'append': 'fa fa-calendar',
                'icon_toggle': True,
            }
        ),
    )
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
    date                = forms.DateTimeField(initial=datetime.date.today)
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
    startTime           = forms.DateTimeField(
        widget=DateTimePicker(
            options={
                'useCurrent': True,
                'collapse': False,
            },
            attrs={
                'append': 'fa fa-calendar',
                'icon_toggle': True,
            }
        ),
    )
    endTime             = forms.DateTimeField(initial=datetime.date.today)

class NewSignIn(forms.Form):
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
    startTime           = forms.DateTimeField(label = "Start Time", initial=datetime.datetime.now)

class ChargeEquity(forms.Form):
    TRANSACTION_CHOICES = (
        ('Equity Bike Purchase', 'Equity Bike Purchase'),
        ('Equity Parts Purchase', 'Equity Parts Purchase'),
    )
    person              = forms.CharField(label = "Person" )
    transactionType     = forms.ChoiceField(label = "transaction Type", choices = TRANSACTION_CHOICES )
    amount              = forms.IntegerField(label = "Amount")
    date                = forms.DateTimeField(initial=datetime.date.today)

class CreateNewSystemUser(forms.Form):
    SYSTEM_USER_CHOICES = (
        ('App Admin', 'App Admin'),
        ('Shop Admin', 'Shop Admin'),
        ('Kiosk', 'Kiosk'),
    )
    username              = forms.CharField(label = "Username" )
    role                  = forms.ChoiceField(label = "Role", choices = SYSTEM_USER_CHOICES )
    email                 = forms.EmailField(label = "Email")
    password              = forms.CharField(max_length=32, widget=forms.PasswordInput)    