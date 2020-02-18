from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^ride_history_customer$', views.ride_history_customer, name='ride_history_customer'),
	url(r'^ride_history_driver$', views.ride_history_driver, name='ride_history_driver'),
	url(r'^near_me/$', views.near_me, name='near_me'),
	url(r'^store_ride_details/$', views.store_ride_details, name='store_ride_details'),
	url(r'^customer_bookings/$', views.customer_bookings, name='customer_bookings'),
	url(r'^driver_bookings/$', views.driver_bookings, name='driver_bookings'),
	url(r'^add_booking/$', views.add_booking, name='add_booking'),
	url(r'^cancel_booking/$', views.cancel_booking, name='cancel_booking'),
	url(r'^verify_otp/$', views.verify_otp, name='verify_otp'),
	url(r'^verify_otp_new/$', views.verify_otp_new, name='verify_otp_new'),
	url(r'^trip_completed/$', views.trip_completed, name='trip_completed'),
	url(r'^cancel_booking_user/$', views.cancel_booking_user, name='cancel_booking_user'),
	url(r'^update_payment_info/$', views.update_payment_info, name='update_payment_info'),
	url(r'^apply_coupon/$', views.apply_coupon, name='apply_coupon'),
	url(r'^apply_coupon_before_booking/$', views.apply_coupon_before_booking, name='apply_coupon_before_booking'),
	url(r'^submit_review/$', views.submit_review, name='submit_review'),
	url(r'^add_ride_later_bookings/$', views.add_ride_later_bookings, name='add_ride_later_bookings'),
	url(r'^process_ride_later_bookings/$', views.process_ride_later_bookings, name='process_ride_later_bookings'),
	url(r'^change_destination/$', views.change_destination, name='change_destination'),
]

