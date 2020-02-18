from django.contrib import admin
from . models import ride_history, booking, coupon, ride_later_booking#, BookingSummary
#from django.conf import settings

class bookingAdmin(admin.ModelAdmin):

	search_fields = ('booking_id', 'driver__phone_number', 'customer__phone_number')
	list_display = ("customer", "driver", "is_verified", "status")
	list_filter = ("verified", "trip_status", "driver__phone_number", "customer__phone_number",)

	def is_verified(self, obj):
		return obj.verified
	def status(self, obj):
		return False if(obj.trip_status == 'ongoing') else True
	def driver(self, obj):
		return obj.driver
	def customer(self, obj):
		return obj.customer

	is_verified.boolean = True
	status.boolean = True




class couponAdmin(admin.ModelAdmin):

	search_fields = ('code', 'title',)
	list_display = ("code", "title", "used_count", "max_limit")

	def used_count(self, obj):
		return obj.used_count
	def max_limit(self, obj):
		return obj.max_limit

	used_count.boolean = True
	max_limit.boolean = True

admin.site.register(booking, bookingAdmin)
admin.site.register(coupon, couponAdmin)
admin.site.register(ride_later_booking)

#@admin.register(BookingSummary)
#class BookingSummaryAdmin(admin.ModelAdmin):
#    change_list_template = 'summary.html'
    #date_hierarchy = 'created'