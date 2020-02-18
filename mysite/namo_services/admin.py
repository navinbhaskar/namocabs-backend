from django.contrib import admin
from . models import services, vehicle, city_availability, promo_code, saved_location, promotions#, bookings

class servicesAdmin(admin.ModelAdmin):

	search_fields = ('name', 'tagline',)
	list_display = ("name",)

class vehicleAdmin(admin.ModelAdmin):

	search_fields = ('driver__firstname', 'driver__lastname', 'name', 'company', 'vehicle_number')
	list_display = ('driver', 'name', 'company', 'vehicle_number')

admin.site.register(services, servicesAdmin)
admin.site.register(vehicle, vehicleAdmin)
admin.site.register(city_availability)
admin.site.register(promo_code)
admin.site.register(saved_location)
admin.site.register(promotions)
