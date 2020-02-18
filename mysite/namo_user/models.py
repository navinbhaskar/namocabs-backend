from django.db import models
import datetime

class namo_user(models.Model):
    gender_choices = [('1', 'Male'), ('2', 'Female')]
    login_choices = [('1', 'phone'), ('2', 'gmail'), ('3', 'Facebook')]

    user_id = models.AutoField(primary_key=True)
    firstname = models.CharField(max_length=50, blank=False)
    lastname = models.CharField(max_length=50, blank=False)
    gender = models.CharField(max_length=9, choices=gender_choices, default='1')
    phone_number = models.CharField(max_length=13, blank =False, unique=True)
    email = models.CharField(max_length=60, blank=True, unique=True, null=True,)
    photo =  models.CharField(max_length=300, blank=True)
    rating = models.IntegerField(blank =True, null=True)
    login_type = models.CharField(max_length=10, choices=login_choices, default='1')
    date_joined = models.DateTimeField(default=datetime.datetime.now())

    #class Meta:
    #    db_table = 'namocabs_user_info'
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return u'%s - %s %s' % ( str(self.phone_number), str(self.firstname), str(self.lastname))

class driver(models.Model):
    gender_choices = [('1', 'Male'), ('2', 'Female')]
    AVAILABLE = 'available'
    BUSY = 'busy'
    STATUS = [
        (AVAILABLE, ('available')),
        (BUSY, ('busy')),
    ]

    user_id = models.AutoField(primary_key=True)
    firstname = models.CharField(max_length=50, blank=False)
    lastname = models.CharField(max_length=50, blank=False)
    gender = models.CharField(max_length=9, choices=gender_choices, default='1')
    phone_number = models.CharField(max_length=13, blank =False, unique=True)
    address = models.CharField(max_length=500, blank=True, null=True,)
    licence_number = models.CharField(max_length=50, blank=False)
    photo =  models.CharField(max_length=300, blank=True)
    availability = models.CharField( max_length=32, choices=STATUS, default=AVAILABLE,)
    five_stars = models.IntegerField(blank =True, default=0)
    four_stars = models.IntegerField(blank =True, default=0)
    three_stars = models.IntegerField(blank =True, default=0)
    two_stars = models.IntegerField(blank =True, default=0)
    one_stars = models.IntegerField(blank =True, default=0)
    number_of_trips = models.IntegerField(blank =True, default=0)
    city =  models.CharField(max_length=50, blank=True)
    current_debt_amount = models.IntegerField(default=0)
    pan_card = models.CharField(max_length=50, blank=False)

    #class Meta:
    #    db_table = 'namocabs_driver_info'
    class Meta:
        verbose_name = "Driver"
        verbose_name_plural = "Drivers"

    def __str__(self):
        return u'%s - %s %s' % ( str(self.phone_number), str(self.firstname), str(self.lastname))

    @staticmethod
    def autocomplete_search_fields():
        return 'firstname', 'lastname', 'phone_number'