from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^fetch_user_data/$', views.fetch_user_data, name='fetch_user_data'),
	url(r'^create_profile/$', views.create_profile, name='create_profile'),
	url(r'^fetch_user_data_new_booking/$', views.fetch_user_data_new_booking, name='fetch_user_data_new_booking'),
	url(r'^fetch_driver_data/$', views.fetch_driver_data, name='fetch_driver_data'),
	url(r'^create_profile_driver/$', views.create_profile_driver, name='create_profile_driver'),
	url(r'^check_user_status/$', views.check_user_status, name='check_user_status'),
	url(r'^update_user_profile/$', views.update_user_profile, name='update_user_profile'),
	url(r'^fetch_driver_data_to_user/$', views.fetch_driver_data_to_user, name='fetch_driver_data_to_user'),
]

