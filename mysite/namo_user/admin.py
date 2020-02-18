from django.contrib import admin
from . models import namo_user, driver
from django.contrib.auth.models import User, Group

class namo_userAdmin(admin.ModelAdmin):

	search_fields = ('firstname', 'lastname', 'phone_number')
	list_display = ("firstname", "lastname", "phone_number", "email")

class driverAdmin(admin.ModelAdmin):

	search_fields = ('firstname', 'lastname', 'phone_number', 'city')
	list_display = ("firstname", "lastname", "phone_number", "city", "rating")

	def rating(self, obj):
		total_ratings = obj.five_stars + obj.four_stars + obj.three_stars + obj.two_stars + obj.one_stars
		return round((5 * obj.five_stars + 4 * obj.four_stars + 3 * obj.three_stars + 2 * obj.two_stars + obj.one_stars) / total_ratings, 2) if total_ratings != 0 else 'Null'

admin.site.unregister(User)
admin.site.unregister(Group)
admin.site.register(namo_user, namo_userAdmin)
admin.site.register(driver, driverAdmin)
