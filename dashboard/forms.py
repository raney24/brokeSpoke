from django import forms
from .models import Users, Timelogs, Transactions
from tempus_dominus.widgets import DatePicker, TimePicker, DateTimePicker
from django.contrib.auth.models import User
from .widgets import XDSoftDateTimePickerInput, XDSoftDatePickerInput
import pytz
import datetime
from datetime import timezone, timedelta
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout,Field



class RawUserForm(forms.Form):
    # username = forms.CharField()
    firstname = forms.CharField(label="First name")
    middlename = forms.CharField(label="Middle Name, Initial, or Nickname ")
    lastname = forms.CharField(label="Last name")
    waiverAcceptedDate = forms.CharField(
        label="Waiver acceptance date", widget=XDSoftDatePickerInput(), required=False)
    membershipExp = forms.CharField(
        label="Membership Exipration", widget=XDSoftDatePickerInput(), required=False)
    birthdate = forms.CharField(widget=XDSoftDatePickerInput(),required=False)
    email = forms.CharField(label="E-mail", required=False)
    phone = forms.CharField(label="Phone", required=False)
    emergencyName = forms.CharField(
        label="Emergency Contact Name", required=False)
    relation = forms.CharField(label="relation", required=False)
    emergencyPhone = forms.CharField(
        label=" Emergency Contact Phone", required=False)
    importedID = forms.CharField(
        label=" importedID", required=False)


class RawTransactionForm(forms.Form):
    TRANSACTION_CHOICES = (
        ('Bike Purchase', 'Bike Purchase'),
        ('Parts Purchase', 'Parts Purchase'),
        ('Volunteer Credit', 'Volunteer Credit'),
        ('Stand Time Purchase', 'Stand Time Purchase'),
        ('Imported Balance', 'Imported Balance'),
    )
    PAYMENT_CHOICES = (
        
        ('Sweat Equity', 'Sweat Equity'),
        ('Cash/Credit', 'Cash/Credit'),
    )
    STATUS_CHOICES = (
        ('Complete', 'Complete'),
        ('Pending', 'Pending'),
    )
    transactionPerson = forms.CharField(label="Person", widget=forms.TextInput(
        attrs={'placeholder': 'Search by last name'}))
    transactionType = forms.ChoiceField(
        label="Transaction Type", choices=TRANSACTION_CHOICES)
    amount = forms.IntegerField(label="Amount")
    date = forms.DateTimeField(label="Date/Time", input_formats=[
                               '%m/%d/%Y %I:%M %p'], widget=XDSoftDateTimePickerInput())
    paymentType = forms.ChoiceField(
        label="Payment Type", choices=PAYMENT_CHOICES)
    paymentStatus = forms.ChoiceField(
        label="Payment Status", choices=STATUS_CHOICES)
    importedTransactionId = forms.CharField(required=False)
    importedUserId = forms.CharField(required=False)
    


class RawTimelogsForm(forms.Form):
    SIGN_IN_CHOICES = (
        ('Volunteering', 'Volunteering'),
        ('Member Stand Time', 'Member Stand Time'),
        ('Stand Time', 'Stand Time'),
        ('Shopping', 'Shopping'),
        ('Other', 'Other'),
        ('Imported Login', 'Imported Login'),
    )
    PAYMENT_CHOICES = ((0,'Sweat Equity'),(1,'Cash/Card'))
    person = forms.CharField(label="Person", widget=forms.TextInput(
        attrs={'placeholder': 'Search by last name'}))
    activity = forms.ChoiceField(label="Activity", choices=SIGN_IN_CHOICES)
    startTime = forms.DateTimeField(label="Start Time", input_formats=[
                                   '%m/%d/%Y %I:%M %p'], widget=XDSoftDateTimePickerInput())
    endTime = forms.DateTimeField(label="End Time", input_formats=[
                                  '%m/%d/%Y %I:%M %p'], widget=XDSoftDateTimePickerInput())
    payment = forms.ChoiceField(label = "Payment Type",required=False, choices = PAYMENT_CHOICES)
    importedTimelogId = forms.CharField(
        label=" importedID", required=False)
    importedTransactionId = forms.CharField(
        label=" importedID", required=False)
    importedUserId = forms.CharField(
        label=" importedID", required=False)


class NewSignIn(forms.Form):
    SIGN_IN_CHOICES = (
        ('Volunteering', 'Volunteering'),
        ('Member Stand time', 'Member Stand Time'),
        ('Stand Time', 'Stand Time'),
        ('Shopping', 'Shopping'),
        ('Other', 'Other'),
        ('Imported Login', 'Imported Login'),
    )
    local = pytz.timezone("US/Eastern")
    person = forms.CharField(label="Person", widget=forms.TextInput(
        attrs={'placeholder': 'Search by last name'}))
    activity = forms.ChoiceField(label="Activity", choices=SIGN_IN_CHOICES)
    startTime = forms.DateTimeField(input_formats=[
                                    '%m/%d/%Y %I:%M %p'], label="Start time", widget=XDSoftDateTimePickerInput())


class ChargeEquity(forms.Form):
    TRANSACTION_CHOICES = (
        ('Bike Purchase', 'Bike Purchase'),
        ('Parts Purchase', 'Parts Purchase'),
        ('Volunteer Credit', 'Volunteer Credit'),
        ('Stand Time Purchase', 'Stand Time Purchase'),
        ('Imported Balance', 'Imported Balance'),
    )
    transactionPerson = forms.CharField(label="Person", widget=forms.TextInput(
        attrs={'placeholder': 'Search by last name'}))
    transactionType = forms.ChoiceField(
        label="Transaction Type", choices=TRANSACTION_CHOICES)
    amount = forms.IntegerField(label="Amount")
    date = forms.DateTimeField(label="Date", input_formats=[
                               '%m/%d/%Y %I:%M %p'], widget=XDSoftDateTimePickerInput())


class CreateNewSystemUser(forms.Form):
    SYSTEM_USER_CHOICES = (
        ('App Admin', 'App Admin'),
        ('Shop Admin', 'Shop Admin'),
        ('Kiosk', 'Kiosk'),
    )
    username = forms.CharField(label="Username")
    role = forms.ChoiceField(label="Role", choices=SYSTEM_USER_CHOICES)
    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput)


class ChangeEquityRates(forms.Form):
    sweatEquity = forms.IntegerField(label='Sweat Equity')
    standTime = forms.IntegerField(label='Stand Time')
    volunteerTime = forms.IntegerField(label='Volunteer Time')
    volunteerAlert = forms.IntegerField(label='Volunteer Alert')


class LoginReport(forms.Form):
    startDate = forms.CharField(
        label="Start Date", widget=XDSoftDatePickerInput())
    endDate = forms.CharField(label="End Date", widget=XDSoftDatePickerInput())


class HoursReport(forms.Form):
    startDate = forms.CharField(
        label="Start Date", widget=XDSoftDatePickerInput())
    endDate = forms.CharField(label="End Date", widget=XDSoftDatePickerInput())


class UserReport(forms.Form):
    startDate = forms.CharField(
        label="Start Date", widget=XDSoftDatePickerInput())
    endDate = forms.CharField(label="End Date", widget=XDSoftDatePickerInput())
    person = forms.CharField(label="Person", widget=forms.TextInput(
        attrs={'placeholder': 'Search by last name'}))


class ShiftsInRangeReport(forms.Form):
    startDate = forms.CharField(
        label="Start Date", widget=XDSoftDatePickerInput())
    endDate = forms.CharField(label="End Date", widget=XDSoftDatePickerInput())
    numShifts = forms.IntegerField(label="Number of Shifts")
