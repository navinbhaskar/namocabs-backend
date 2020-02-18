from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^fetch_services_data/$', views.fetch_services_data, name='fetch_services_data'),
	url(r'^fetch_services_data_location_wise/$', views.fetch_services_data_location_wise, name='fetch_services_data_location_wise'),
	url(r'^fetch_promo_code/$', views.fetch_promo_code, name='fetch_promo_code'),
	url(r'^fetch_promotion_code/$', views.fetch_promotion_code, name='fetch_promotion_code'),
	url(r'^add_location/$', views.add_location, name='add_location'),
	url(r'^fetch_saved_locations/$', views.fetch_saved_locations, name='fetch_saved_locations'),
	url(r'^delete_locations/(?P<location_id>[a-zA-Z0-9_.-]+)/$', views.delete_locations, name='delete_locations')
]

