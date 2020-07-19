from django.db import models
import datetime
# Create your models here.

class Users(models.Model):
    firstname           = models.CharField(max_length=20,default = 'NULL')
    middlename          = models.CharField(max_length=20,default = 'NULL')
    lastname            = models.CharField(max_length=20,default = 'NULL')
    waiverAcceptedDate  = models.CharField(max_length = 40,null=True,blank = True,default = 'NULL')
    membershipExp       = models.CharField(max_length = 40,null=True,blank = True,default = 'NULL')
    birthdate           = models.CharField(max_length = 40,null=True)
    email               = models.CharField(max_length=40,blank = True,default = 'NULL')
    phone               = models.CharField(max_length=40,default = 'NULL',null=True,blank = True)
    emergencyName       = models.CharField(max_length=20,blank = True,default = 'NULL')
    relation            = models.CharField(max_length=20,blank = True,default = 'NULL')
    emergencyPhone      = models.CharField(max_length=40,blank = True,default = 'NULL')
    lastVisit           = models.CharField(max_length=40,blank = True,default = 'NULL')
    equity              = models.IntegerField(blank = True,default = 0)
    waiver              = models.CharField(max_length=20,blank = True,default = 'NULL')
    permissions         = models.CharField(max_length=20,blank = True,default = 'NULL')

    class Meta:
        constraints = [models.UniqueConstraint(fields=['firstname', 'middlename','lastname','birthdate'], name='unique user check')]
    def __str__(self):
        return self.firstname

class Transactions(models.Model):
    TRANSACTION_CHOICES = (
        ('Bike Purchase', 'Bike Purchase'),
        ('Parts Purchase', 'Parts Purchase'),
        ('Volunteer Credit', 'Volunteer Credit'),
        ('Stand Time Purchase', 'Stand Time Purchase'),
        ('Imported Balance', 'Imported Balance'),
    )
    PAYMENT_CHOICES = (
        ('Cash/Credit', 'Cash/Credit'),
        ('Sweat Equity', 'Sweat Equity'),
    )
    STATUS_CHOICES = (
        ('Complete', 'Complete'),
        ('Pending', 'Pending'),
    )
    transactionPerson   = models.CharField(max_length=20)
    transactionType     = models.CharField(max_length=40, choices = TRANSACTION_CHOICES)
    amount              = models.IntegerField(null=True,blank = True,default = 0)
    paymentType         = models.CharField(max_length=20,null=True,blank = True,default = 0,choices = PAYMENT_CHOICES )
    paymentStatus       = models.CharField(max_length=20,null=True,blank = True,default = 0,choices = STATUS_CHOICES )   
    date                = models.CharField(max_length = 40,null=True)
    users               = models.ForeignKey(Users, on_delete = models.SET_DEFAULT, default = 1)
    
    def __str__(self):
        return self.transactionPerson

class Timelogs(models.Model):
    SIGN_IN_CHOICES = (
        ('volunteering', 'volunteering'),
        ('member stand time', 'member stand time'),
        ('stand time', 'stand time'),
        ('shopping', 'shopping'),
        ('other', 'other'),
        ('imported login', 'imported login'),
    )

    person              = models.CharField(max_length=20)
    activity            = models.CharField(max_length=100, choices = SIGN_IN_CHOICES)
    startTime           = models.CharField(max_length = 40,null=True)
    endTime             = models.CharField(max_length = 40,null=True)
    users               = models.ForeignKey(Users,on_delete = models.SET_DEFAULT, default = 1)

    def __str__(self):
        return self.person
    

class NewSystemUser(models.Model):
    SYSTEM_USER_CHOICES = (
        ('App Admin', 'App Admin'),
        ('Shop Admin', 'Shop Admin'),
        ('Kiosk', 'Kiosk'),
    )
    username              = models.CharField(max_length = 40)
    role                  = models.CharField(max_length = 20, choices = SYSTEM_USER_CHOICES )
    email                 = models.EmailField(max_length = 254)
    password              = models.CharField(max_length=32)   

    def __str__(self):
        return self.username 

class EquityRates(models.Model):
    sweatEquity = models.IntegerField(null=True,blank = True,default = 8)
    standTime = models.IntegerField(null=True,blank = True,default = 4)
    volunteerTime = models.IntegerField(null=True,blank = True,default = 8)
    volunteerAlert = models.IntegerField(null=True,blank = True,default = 4)