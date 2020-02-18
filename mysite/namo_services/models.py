from django.db import models
import sys
sys.path.append("..")
from mysite.namo_user.models import namo_user, driver
from datetime import datetime

class services(models.Model):
    #service_choices = [('1', 'bike'), ('2', 'Scooty'), ('3', 'Mini'), ('4', 'Luxury'), ('5', 'Truck')]

    uid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20, blank=False, unique=True)
    icon =  models.CharField(max_length=300, blank=True)
    card_image =  models.CharField(max_length=300, blank=True)
    tagline =  models.CharField(max_length=300, blank=True)
    fixed_amount = models.IntegerField(default= 20)
    rate = models.IntegerField(default = 8)

    #class Meta:
    #    db_table = 'namocabs_services_info'

    def __str__(self):
        return u'%s' % ( str(self.name))

class vehicle(models.Model):

    uid = models.AutoField(primary_key=True)
    driver = models.ForeignKey(driver, null = True, on_delete=models.SET_NULL, unique=True)
    name = models.CharField(max_length=40, blank=False)
    service_type = models.ForeignKey(services, on_delete=models.CASCADE)
    vehicle_number = models.CharField(max_length=20, blank=False, unique=True)
    company = models.CharField(max_length=20, blank=False)
    color = models.CharField(max_length=20, blank=False)

    #class Meta:
    #    db_table = 'namocabs_vehicles_info'
        

    def __str__(self):
        return u'%s - %s - %s %s' % ( str(self.name), str(self.service_type.name), str(self.driver.firstname), str(self.driver.lastname))


class city_availability(models.Model):
    service_type = models.ForeignKey(services, on_delete=models.CASCADE)
    city= models.CharField(max_length=100, blank=True)
    state= models.CharField(max_length=100, blank=True)

    class Meta:
        #db_table = 'city_availability'
        verbose_name_plural = "City Availabilities"
        unique_together = ('service_type', 'city', 'state')

    def __str__(self):
        return u'%s - %s, %s' % ( str(self.service_type.name), str(self.city), str(self.state))

class promo_code(models.Model):

    promo_code_id = models.AutoField(primary_key=True)
    promo_code = models.CharField(max_length=50, blank=False)
    title = models.CharField(max_length=50, blank=True)
    subtitle = models.CharField(max_length=50, blank=True)
    terms = models.CharField(max_length=200, blank=True)
    image =  models.CharField(max_length=300, blank=True)

    #class Meta:
    #    db_table = 'namocabs_promo_code'

    def __str__(self):
        return u'%s - %s' % ( str(self.promo_code), str(self.title))

class saved_location(models.Model):

    location_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(namo_user, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, blank=False)
    longitude = models.FloatField(null=True, blank=True, default=None)
    latitude = models.FloatField(null=True, blank=True, default=None)
    location = models.CharField(max_length=1000, blank=False)
    complete_address = models.CharField(max_length=1000, blank=False)


    def __str__(self):
        return u'%s - %s' % ( str(self.name), str(self.complete_address))

class promotions(models.Model):

    promotion_code_id = models.AutoField(primary_key=True)
    promotion_code = models.CharField(max_length=50, blank=False)
    title = models.CharField(max_length=50, blank=True)
    subtitle = models.CharField(max_length=50, blank=True)
    terms = models.CharField(max_length=200, blank=True)
    image =  models.CharField(max_length=300, blank=True)

    class Meta:
        #db_table = 'namocabs_promotions'
        verbose_name_plural = "Promotions"

    def __str__(self):
        return u'%s - %s' % ( str(self.promotion_code), str(self.title))


        