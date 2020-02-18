from django.db import models
import sys
sys.path.append("..")
from mysite.namo_user.models import namo_user, driver
from mysite.namo_services.models import services, vehicle
from datetime import datetime
import random
import string

class ride_history(models.Model):

    ride_id = models.AutoField(primary_key=True)
    total_fare = models.CharField(max_length=50, blank=False)
    driver = models.ForeignKey(driver, on_delete=models.CASCADE)
    customer = models.ForeignKey(namo_user, on_delete=models.CASCADE)
    pickup_location_longitude = models.FloatField(null=True, blank=True, default=None)
    pickup_location_latitude = models.FloatField(null=True, blank=True, default=None)
    drop_location_longitude = models.FloatField(null=True, blank=True, default=None)
    drop_location_latitude = models.FloatField(null=True, blank=True, default=None)

    def __str__(self):
        return u'%s %s  -  %s %s' % ( str(self.driver.firstname), str(self.driver.lastname),str(self.customer.firstname), str(self.customer.lastname))

class booking(models.Model):

    ONGOING = 'ongoing'
    CANCLED = 'cancelled'
    COMPLETED = 'completed'
    STATUS = [
        (ONGOING, ('Ongoing Trip')),
        (CANCLED, ('Trip is cancelled')),
        (COMPLETED, ('Trip is Completed')),
    ]

    booking_id = models.CharField(max_length=50, primary_key=True)
    driver = models.ForeignKey(driver, on_delete=models.CASCADE)
    customer = models.ForeignKey(namo_user, on_delete=models.CASCADE)
    service_type = models.ForeignKey(services, null = True, on_delete=models.SET_NULL)
    vehicle = models.ForeignKey(vehicle, null=True, on_delete=models.SET_NULL)
    pickup_location_longitude = models.FloatField(null=True, blank=True, default=None)
    pickup_location_latitude = models.FloatField(null=True, blank=True, default=None)
    drop_location_longitude = models.FloatField(null=True, blank=True, default=None)
    drop_location_latitude = models.FloatField(null=True, blank=True, default=None)
    otp = models.CharField(max_length=10, blank=False)
    verified = models.BooleanField(default=False)
    base_fare = models.FloatField(null=True, blank=True, default=None)
    final_amount = models.FloatField(null=True, blank=True, default=None)
    trip_status = models.CharField( max_length=32, choices=STATUS, default=ONGOING,)
    payment_mode = models.CharField(max_length=40, blank=False, default='Cash')
    payment_id = models.CharField(max_length=100, blank=True)
    total_distance_travelled = models.IntegerField(default=0)
    timestamp = models.DateTimeField(default=datetime.now, blank=True)
    rating = models.IntegerField(blank =True, null=True, default=0)
    review = models.CharField(max_length=500, blank=True)

    #class Meta:
    #    verbose_name_plural = "Bookings"

    def __str__(self):
        return u'%s %s - %s %s' % (str(self.customer.firstname), str(self.customer.lastname), str(self.driver.firstname), str(self.driver.lastname))


class coupon(models.Model):

    code = models.CharField(max_length=20, primary_key=True, blank=False)
    title = models.CharField(max_length=50, blank=False)
    details = models.CharField(max_length=500, blank=True)
    discount_percent = models.IntegerField(default=0)
    maximum_discount = models.IntegerField(default=0)
    used_count = models.IntegerField(default=0)
    max_limit = models.IntegerField(default=0)

    def __str__(self):
        return u'%s %s  -  %s/%s' % ( str(self.code), str(self.title),str(self.used_count), str(self.max_limit))


class ride_later_booking(models.Model):

    PENDING = 'pending'
    PROCESSED = 'Processed'
    STATUS = [
        (PENDING, ('Pending')),
        (PROCESSED, ('Processed'))
    ]

    booking_id = models.CharField(max_length=50, primary_key=True, default=''.join(random.choices(string.ascii_uppercase + string.digits, k=8)))
    customer = models.ForeignKey(namo_user, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=datetime.now, blank=False)
    pickup_location_longitude = models.FloatField(default=None)
    pickup_location_latitude = models.FloatField(default=None)
    drop_location_longitude = models.FloatField(default=None)
    drop_location_latitude = models.FloatField(default=None)
    service_type = models.ForeignKey(services, null = True, on_delete=models.SET_NULL)
    payment_mode = models.CharField(max_length=50, blank=False)
    status = models.CharField( max_length=32, choices=STATUS, default=PENDING,)

    def __str__(self):
        return u'%s %s  -  %s' % ( str(self.customer.firstname), str(self.customer.lastname),str(self.timestamp),)


#class BookingSummary(booking):
#    class Meta:
#        proxy = True
#        verbose_name = 'Booking Summary'
#        verbose_name_plural = 'Bookings Summary'