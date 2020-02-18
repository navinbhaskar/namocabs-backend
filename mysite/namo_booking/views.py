from django.shortcuts import render
from rest_framework.views import APIView
from django.http import HttpResponse
from django.http import JsonResponse
import json
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
import datetime
import google.oauth2.id_token
import google.auth.transport.requests
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from firebase_admin import firestore
from operator import attrgetter
import random
import string
from . models import ride_history, booking, coupon, ride_later_booking
import sys
sys.path.append("..")
from mysite.namo_user.models import namo_user, driver
from mysite.namo_services.models import services, vehicle
import http.client

HTTP_REQUEST = google.auth.transport.requests.Request()

@csrf_exempt
def near_me(request):
   #id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
   #claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
   #if not claims:
   #   return HttpResponse('Unauthorized')

   user_json_data=json.loads(request.body)
   longitude = user_json_data['longitude']
   latitude = user_json_data['latitude']
   service_type = user_json_data['type']

   db = firestore.Client()
   doc_ref = db.collection(u'locations').where(u'type', u'==', service_type)

   doc = doc_ref.get()
   
   driver_list = []

   for el in doc:
      all_data = el.to_dict()
      if(all_data['status'] != 'booked'):
         distance = (float(all_data['longitude']) - longitude)**2 + (float(all_data['latitude']) - latitude)**2
         data = {
            "longitude": float(all_data['longitude']),
            "latitude": float(all_data['latitude']),
            "phone_number": all_data['phone_number'],
            "distance": distance
         }
         driver_list.append(dict(data))

   driver_list.sort(key=lambda x: x['distance'], reverse=False)

   if(len(driver_list) <= 10):
      return HttpResponse(json.dumps(driver_list), content_type='application/json')
   else:
      return HttpResponse(json.dumps(driver_list[0:10]), content_type='application/json')


@csrf_exempt
def book_now(request):
   id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
   claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
   if not claims:
      return HttpResponse('Unauthorized')

   user_json_data=json.loads(request.body)
   longitude = user_json_data['longitude']
   latitude = user_json_data['latitude']
   service_type = user_json_data['type']

   db = firestore.Client()
   doc_ref = db.collection(u'locations').where(u'type', u'==', service_type)

   doc = doc_ref.get()
   
   driver_list = []

   for el in doc:
      all_data = el.to_dict()
      if(all_data['is_available']):
         distance = (float(all_data['longitude']) - longitude)**2 + (float(all_data['latitude']) - latitude)**2
         data = {
            "longitude": float(all_data['longitude']),
            "latitude": float(all_data['latitude']),
            "phone_number": all_data['phone_number'],
            "distance": distance
         }
         driver_list.append(dict(data))

   driver_list.sort(key=lambda x: x['distance'], reverse=False)

   return HttpResponse(json.dumps(driver_list[0:9]), content_type='application/json')


@csrf_exempt
def ride_history_customer(request):
   id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
   claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
   if not claims:
      return HttpResponse('Unauthorized')

   username = claims['firebase']['identities']['phone'][0][3:13]
   #username = '8840885843'

   ride_list_object = ride_history.objects.select_related('driver').filter(customer__phone_number=username)

   ride_list = []

   for ride in ride_list_object:
      data = {
         "fare": ride.total_fare,
         "driver": ride.driver.firstname + " " + ride.driver.lastname,
         "pickup_location_longitude": ride.drop_location_longitude,
         "pickup_location_latitude": ride.drop_location_latitude,
         "drop_location_longitude": ride.drop_location_longitude,
         "drop_location_latitude": ride.drop_location_latitude
      }

      ride_list.append(data)

   
   return JsonResponse(ride_list, safe = False)


@csrf_exempt
def ride_history_driver(request):
   id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
   claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
   if not claims:
      return HttpResponse('Unauthorized')

   username = claims['firebase']['identities']['phone'][0][3:13]
   #username = '9555579357'

   ride_list_object = ride_history.objects.select_related('customer').filter(driver__phone_number=username)

   ride_list = []

   for ride in ride_list_object:
      data = {
         "fare": ride.total_fare,
         "driver": ride.customer.firstname + " " + ride.customer.lastname,
         "pickup_location_longitude": ride.drop_location_longitude,
         "pickup_location_latitude": ride.drop_location_latitude,
         "drop_location_longitude": ride.drop_location_longitude,
         "drop_location_latitude": ride.drop_location_latitude
      }

      ride_list.append(data)

   
   return JsonResponse(ride_list, safe = False)


@csrf_exempt
def store_ride_details(request):
   id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
   claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
   if not claims:
      return HttpResponse('Unauthorized')
   phone_number = claims['firebase']['identities']['phone'][0][3:13]
   #phone_number="9555579357"

   user_json_data=json.loads(request.body)
        
   customer_phone_number = user_json_data['customer_phone_number']
   fare = user_json_data['fare']
   pickup_location_longitude = user_json_data['pickup_location_longitude']
   pickup_location_latitude = user_json_data['pickup_location_latitude']
   drop_location_longitude = user_json_data['drop_location_longitude']
   drop_location_latitude = user_json_data['drop_location_latitude']
   
   customer = namo_user.objects.get(phone_number=customer_phone_number)
   driver_details = driver.objects.get(phone_number=phone_number)

   try:
      ride_data = ride_history(
                           total_fare = fare,
                           driver = driver_details,
                           customer = customer,
                           pickup_location_longitude = pickup_location_longitude,
                           pickup_location_latitude = pickup_location_latitude,
                           drop_location_longitude = drop_location_longitude,
                           drop_location_latitude = drop_location_latitude
                           )
      
      ride_data.save()
      return JsonResponse({'status': '201', 'message': 'Successfully created'})
   except Exception as e:
      return HttpResponse(e)

@csrf_exempt
def add_favourite_location(request):
   id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
   claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
   if not claims:
      return HttpResponse('Unauthorized')
   phone_number = claims['firebase']['identities']['phone'][0][3:13]
   #phone_number="9555579357"

   user_json_data=json.loads(request.body)
        
   customer_phone_number = user_json_data['customer_phone_number']
   fare = user_json_data['fare']
   pickup_location_longitude = user_json_data['pickup_location_longitude']
   pickup_location_latitude = user_json_data['pickup_location_latitude']
   drop_location_longitude = user_json_data['drop_location_longitude']
   drop_location_latitude = user_json_data['drop_location_latitude']
   
   customer = namo_user.objects.get(phone_number=customer_phone_number)
   driver_details = driver.objects.get(phone_number=phone_number)

   try:
      ride_data = ride_history(
                           total_fare = fare,
                           driver = driver_details,
                           customer = customer,
                           pickup_location_longitude = pickup_location_longitude,
                           pickup_location_latitude = pickup_location_latitude,
                           drop_location_longitude = drop_location_longitude,
                           drop_location_latitude = drop_location_latitude
                           )
      
      ride_data.save()
      return JsonResponse({'status': '201', 'message': 'Successfully created'})
   except Exception as e:
      return HttpResponse(e)


@csrf_exempt
def customer_bookings(request):
   id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
   claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
   if not claims:
      return HttpResponse('Unauthorized')

   username = claims['firebase']['identities']['phone'][0][3:13]
   #username = '9933956490'

   ride_list_object = booking.objects.select_related('driver').filter(customer__phone_number=username)
   
   ride_list = []

   for ride in ride_list_object:
      data = {
         "fare": ride.final_amount,
         "driver": ride.driver.firstname + " " + ride.driver.lastname,
         "pickup_location_longitude": ride.drop_location_longitude,
         "pickup_location_latitude": ride.drop_location_latitude,
         "drop_location_longitude": ride.drop_location_longitude,
         "drop_location_latitude": ride.drop_location_latitude,
         "status": ride.trip_status,
         "payment_mode": ride.payment_mode,
         "timestamp": ride.timestamp
      }

      ride_list.append(data)

   
   return JsonResponse(ride_list, safe = False)

@csrf_exempt
def driver_bookings(request):
   id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
   claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
   if not claims:
      return HttpResponse('Unauthorized')

   username = claims['firebase']['identities']['phone'][0][3:13]
   #username = '1234567895'

   ride_list_object = booking.objects.select_related('customer').filter(driver__phone_number=username)
   
   ride_list = []

   for ride in ride_list_object:
      data = {
         "fare": ride.final_amount,
         "customer": ride.customer.firstname + " " + ride.customer.lastname,
         "pickup_location_longitude": ride.drop_location_longitude,
         "pickup_location_latitude": ride.drop_location_latitude,
         "drop_location_longitude": ride.drop_location_longitude,
         "drop_location_latitude": ride.drop_location_latitude,
         "status": ride.trip_status,
         "payment_mode": ride.payment_mode,
         "timestamp": ride.timestamp
      }

      ride_list.append(data)

   
   return JsonResponse(ride_list, safe = False)


@csrf_exempt
def add_booking(request):
   #id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
   #claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
   #if not claims:
   #   return HttpResponse('Unauthorized')
   #phone_number = claims['firebase']['identities']['phone'][0][3:13]
   #phone_number="9555579357"

   booking_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
   otp = ''.join(random.choices(string.digits, k=4))

   user_json_data=json.loads(request.body)
        
   customer_phone_number = user_json_data['customer_phone_number']
   driver_phone_number = user_json_data['driver_phone_number']
   base_fare = user_json_data['base_fare']
   #service_type = user_json_data['service_type']
   #vehicle_number = user_json_data['vehicle_number']
   pickup_location_longitude = user_json_data['pickup_location_longitude']
   pickup_location_latitude = user_json_data['pickup_location_latitude']
   drop_location_longitude = user_json_data['drop_location_longitude']
   drop_location_latitude = user_json_data['drop_location_latitude']
   payment_mode = user_json_data['payment_mode']
   total_distance_travelled = user_json_data['total_distance_travelled']
   
   customer = namo_user.objects.get(phone_number=customer_phone_number)
   driver_details = driver.objects.get(phone_number=driver_phone_number)
   selected_vehicle = vehicle.objects.get(driver=driver_details)
   selected_service = services.objects.get(name=selected_vehicle.service_type)
   

   try:
      ride_data = booking(
                           booking_id = booking_id,
                           driver = driver_details,
                           customer = customer,
                           service_type = selected_service,
                           vehicle = selected_vehicle,
                           pickup_location_longitude = pickup_location_longitude,
                           pickup_location_latitude = pickup_location_latitude,
                           drop_location_longitude = drop_location_longitude,
                           drop_location_latitude = drop_location_latitude,
                           otp = otp,
                           verified = False,
                           base_fare = base_fare,
                           final_amount = base_fare,
                           trip_status = 'ongoing',
                           payment_mode = payment_mode,
                           total_distance_travelled = total_distance_travelled,
                           payment_id = ''
                           )
      
      ride_data.save()

      driver.objects.filter(phone_number=driver_phone_number).update(availability='busy')

      return JsonResponse({'status': '201', 'message': 'Successfully created', 'booking_id': booking_id, 'otp': otp})
   except Exception as e:
      return HttpResponse(e)

@csrf_exempt
def cancel_booking(request):
   id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
   claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
   if not claims:
      return HttpResponse('Unauthorized')
   phone_number = claims['firebase']['identities']['phone'][0][3:13]
   #phone_number="1234567894"

   user_json_data=json.loads(request.body)
        
   booking_id = user_json_data['booking_id']

   if(booking.objects.filter(booking_id=booking_id).exists()):
      
      try:
         db = firestore.Client()
         doc_ref = db.collection(u'locations').document(phone_number)
         doc = doc_ref.get()
         allCourseBlocks = doc.to_dict()

         customer = allCourseBlocks['customer']
         allCourseBlocks['customer'] = 'null'
         allCourseBlocks['status'] = 'available'
         allCourseBlocks['booking_id'] = ''
         allCourseBlocks['otp'] = ''
         allCourseBlocks['otp_verified'] = False
         allCourseBlocks['pickup_latitude'] = ''
         allCourseBlocks['pickup_longitude'] = ''
         allCourseBlocks['drop_latitude'] = ''
         allCourseBlocks['drop_longitude'] = ''
         doc_ref.set(allCourseBlocks)

         doc_ref1 = db.collection(u'user_status').document(customer)
         doc1 = doc_ref1.get()
         allCourseBlocks1 = doc1.to_dict()
         
         allCourseBlocks1['driver'] = 'null'
         allCourseBlocks1['type'] = 'null'
         allCourseBlocks1['drop_latitude'] = 'null'
         allCourseBlocks1['drop_longitude'] = 'null'
         allCourseBlocks1['booking_id'] = ''
         allCourseBlocks1['otp'] = ''
         allCourseBlocks1['status'] = '1'
         
         doc_ref1.set(allCourseBlocks1)
         booking.objects.filter(booking_id=booking_id).update(trip_status='cancelled')
         driver.objects.filter(phone_number=phone_number).update(availability='available')
         return JsonResponse({'status': '201', 'message': 'Successfully created'})
      except Exception as e:
         return HttpResponse(e)
   else:
      return JsonResponse({'status': '404', 'message': 'Booking not found'})

@csrf_exempt
def verify_otp(request):
   id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
   claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
   if not claims:
      return HttpResponse('Unauthorized')
   
   user_json_data=json.loads(request.body)

   booking_id = user_json_data['booking_id']
   otp = user_json_data['otp']

   if(booking.objects.filter(booking_id=booking_id).exists()):
      booking_object = booking.objects.get(booking_id=booking_id)
      if(booking_object.otp == otp):
         try:
            booking.objects.filter(booking_id=booking_id).update(verified=True)
            return JsonResponse({'status': '202', 'message': 'verified'})
         except Exception as e:
            return HttpResponse(e)
      else:
         return JsonResponse({'status': '403', 'message': 'not verified'})
   else:
      return JsonResponse({'status': '404', 'message': 'Booking not found'})

@csrf_exempt
def verify_otp_new(request):
   id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
   claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
   if not claims:
      return HttpResponse('Unauthorized')

   phone_number = claims['firebase']['identities']['phone'][0][3:13]
   user_json_data=json.loads(request.body)

   booking_id = user_json_data['booking_id']
   customer = user_json_data['customer']

   db = firestore.Client()
   doc_ref2 = db.collection(u'locations').document(phone_number)
   doc2 = doc_ref2.get()
   allCourseBlocks2 = doc2.to_dict()
   allCourseBlocks2['otp_verified'] = True
   doc_ref2.update(allCourseBlocks2)

   doc_ref = db.collection(u'user_status').document(customer)
   doc = doc_ref.get()
   allCourseBlocks = doc.to_dict()

   if(booking_id == allCourseBlocks['booking_id']):
      allCourseBlocks['status'] = '4'
      doc_ref.update(allCourseBlocks)
      return JsonResponse({'status': '202', 'message': 'verified'})
   else:
      return JsonResponse({'status': '404', 'message': 'Booking not found'})

@csrf_exempt
def trip_completed(request):
   id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
   claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
   if not claims:
      return HttpResponse('Unauthorized')
   phone_number = claims['firebase']['identities']['phone'][0][3:13]
   #phone_number="7877220192"

   user_json_data=json.loads(request.body)
        
   booking_id = user_json_data['booking_id']

   if(booking.objects.filter(booking_id=booking_id).exists()):
      booking_object = booking.objects.get(booking_id=booking_id)
      
      final_amount = booking_object.base_fare
      if(booking_object.trip_status == 'ongoing'):
         try:
            
            db = firestore.Client()
            doc_ref = db.collection(u'locations').document(phone_number)
            doc = doc_ref.get()
            allCourseBlocks = doc.to_dict()

            customer = allCourseBlocks['customer']
            
            allCourseBlocks['customer'] = 'null'
            allCourseBlocks['status'] = 'available'
            allCourseBlocks['booking_id'] = ''
            allCourseBlocks['otp'] = ''
            allCourseBlocks['otp_verified'] = False
            allCourseBlocks['pickup_latitude'] = ''
            allCourseBlocks['pickup_longitude'] = ''
            allCourseBlocks['drop_latitude'] = ''
            allCourseBlocks['drop_longitude'] = ''
            doc_ref.set(allCourseBlocks)

            doc_ref1 = db.collection(u'user_status').document(customer)
            doc1 = doc_ref1.get()
            allCourseBlocks1 = doc1.to_dict()
            
            #allCourseBlocks1['driver'] = 'null'
            allCourseBlocks1['type'] = 'null'
            #allCourseBlocks1['drop_latitude'] = 'null'
            #allCourseBlocks1['drop_longitude'] = 'null'
            #allCourseBlocks1['booking_id'] = ''
            allCourseBlocks1['otp'] = ''
            allCourseBlocks1['status'] = '5'
            
            doc_ref1.set(allCourseBlocks1)


            booking.objects.filter(booking_id=booking_id).update(trip_status='completed', final_amount = final_amount)
            driver.objects.filter(phone_number=phone_number).update(availability='available')

            conn = http.client.HTTPSConnection("api.msg91.com")
            conn2 = http.client.HTTPSConnection("api.msg91.com")
            msg = "Thank%20you%20for%20choosing%20our%20service.%20You%20bill%20for%20the%20ride%20is%20"+str(allCourseBlocks['fare'])
            conn.request("GET", "/api/sendhttp.php?authkey=314569AF3eNOVZs5re5e294cc2P1&mobiles="+customer+"&unicode=&country=91&message="+msg+"&sender=NAMOIN&route=4")
            msg2 = "Please%20collect%20"+str(allCourseBlocks['fare'])+"%20cash%20from%20the%20customer%20for%20booking%20id%20"+booking_id+"."
            conn2.request("GET", "/api/sendhttp.php?authkey=314569AF3eNOVZs5re5e294cc2P1&mobiles="+phone_number+"&unicode=&country=91&message="+msg2+"&sender=NAMOIN&route=4")
            return JsonResponse({'status': '202', 'message': 'updated'})
         except Exception as e:
            return HttpResponse(e)
      else:
         return JsonResponse({'status': '404', 'message': 'Booking not found'})
   
   else:
      return JsonResponse({'status': '404', 'message': 'Booking not found'})


@csrf_exempt
def cancel_booking_user(request):
   id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
   claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
   if not claims:
      return HttpResponse('Unauthorized')
   phone_number = claims['firebase']['identities']['phone'][0][3:13]

   user_json_data=json.loads(request.body)
        
   booking_id = user_json_data['booking_id']

   if(booking.objects.filter(booking_id=booking_id).exists()):
      
      try:
         db = firestore.Client()
         doc_ref = db.collection(u'user_status').document(phone_number)
         doc = doc_ref.get()
         allCourseBlocks = doc.to_dict()

         driver = allCourseBlocks['driver']
         allCourseBlocks['driver'] = 'null'
         allCourseBlocks['status'] = '1'
         allCourseBlocks['booking_id'] = ''
         allCourseBlocks['otp'] = ''
         allCourseBlocks['fare'] = ''
         allCourseBlocks['drop_latitude'] = ''
         allCourseBlocks['drop_longitude'] = ''
         allCourseBlocks['type'] = 'null'
         doc_ref.set(allCourseBlocks)
         
         doc_ref1 = db.collection(u'locations').document(driver)
         doc1 = doc_ref1.get()
         allCourseBlocks1 = doc1.to_dict()
         
         allCourseBlocks1['customer'] = 'null'
         allCourseBlocks1['drop_latitude'] = 'null'
         allCourseBlocks1['drop_longitude'] = 'null'
         allCourseBlocks['otp_verified'] = False
         allCourseBlocks1['booking_id'] = ''
         allCourseBlocks['pickup_latitude'] = ''
         allCourseBlocks['pickup_longitude'] = ''
         allCourseBlocks1['otp'] = ''
         allCourseBlocks1['status'] = 'available'
         
         doc_ref1.set(allCourseBlocks1)
         booking.objects.filter(booking_id=booking_id).update(trip_status='cancelled')
         driver.objects.filter(phone_number=driver).update(availability='available')
         return JsonResponse({'status': '201', 'message': 'Successfully created'})
      except Exception as e:
         return HttpResponse(e)
   else:
      return JsonResponse({'status': '404', 'message': 'Booking not found'})


@csrf_exempt
def update_payment_info(request):
   id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
   claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
   if not claims:
      return HttpResponse('Unauthorized')
   phone_number = claims['firebase']['identities']['phone'][0][3:13]
   #phone_number="9971209698"

   user_json_data=json.loads(request.body)
        
   booking_id = user_json_data['booking_id']
   payment_mode = user_json_data['payment_mode']
   transaction_id = user_json_data['transaction_id']

   if(booking.objects.filter(booking_id=booking_id).exists()):
      booking_object = booking.objects.get(booking_id=booking_id)
      
      #final_amount = booking_object.base_fare
      try:
         
         db = firestore.Client()
         doc_ref = db.collection(u'user_status').document(phone_number)
         doc = doc_ref.get()
         allCourseBlocks = doc.to_dict()

         driver = allCourseBlocks['driver']

         doc_ref1 = db.collection(u'locations').document(driver)
         doc1 = doc_ref1.get()
         allCourseBlocks1 = doc1.to_dict()
         
         allCourseBlocks1['paid'] = True
         
         doc_ref1.set(allCourseBlocks1)

         booking.objects.filter(booking_id=booking_id).update(payment_mode=payment_mode, payment_id = transaction_id)
         return JsonResponse({'status': '202', 'message': 'updated'})
      except Exception as e:
         return HttpResponse(e)
   
   else:
      return JsonResponse({'status': '404', 'message': 'Booking not found'})


@csrf_exempt
def apply_coupon(request):
   id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
   claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
   if not claims:
      return HttpResponse('Unauthorized')
   phone_number = claims['firebase']['identities']['phone'][0][3:13]
   #phone_number="9971209698"

   user_json_data=json.loads(request.body)
        
   booking_id = user_json_data['booking_id']
   coupon_code = user_json_data['coupon_code']
   initial_amount = user_json_data['initial_amount']

   if(coupon.objects.filter(code=coupon_code).exists()):
      coupon_code_object = coupon.objects.get(code=coupon_code)

      if(coupon_code_object.used_count < coupon_code_object.max_limit):

         percentage = coupon_code_object.discount_percent
         discount = float(initial_amount) * percentage / 100
         if(discount <= coupon_code_object.maximum_discount):
            final_amount = float(initial_amount) - discount
         else:
            final_amount = float(initial_amount) - coupon_code_object.maximum_discount
      
         used_count = coupon_code_object.used_count

         coupon.objects.filter(code=coupon_code).update(used_count=used_count + 1)

         if(booking.objects.filter(booking_id=booking_id).exists()):
            booking_object = booking.objects.get(booking_id=booking_id)

            try:
               db = firestore.Client()
               doc_ref = db.collection(u'user_status').document(phone_number)
               doc = doc_ref.get()
               allCourseBlocks = doc.to_dict()

               driver = allCourseBlocks['driver']
               allCourseBlocks['fare'] = str(final_amount)

               doc_ref1 = db.collection(u'locations').document(driver)
               doc1 = doc_ref1.get()
               allCourseBlocks1 = doc1.to_dict()
               
               allCourseBlocks1['fare'] = str(final_amount)

               doc_ref.set(allCourseBlocks)
               doc_ref1.set(allCourseBlocks1)

               booking.objects.filter(booking_id=booking_id).update(final_amount=final_amount)
            except:
               return JsonResponse({'amount': float(initial_amount), 'message': 'Something went wrong'})               

         return JsonResponse({'amount': final_amount, 'message': 'Coupon applied'})

      return JsonResponse({'amount': float(initial_amount), 'message': 'Coupon expired'})

   return JsonResponse({'amount': float(initial_amount), 'message': 'Wrong coupon code'})

@csrf_exempt
def apply_coupon_before_booking(request):
   id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
   claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
   if not claims:
      return HttpResponse('Unauthorized')
   #phone_number = claims['firebase']['identities']['phone'][0][3:13]
   #phone_number="9971209698"

   user_json_data=json.loads(request.body)
        
   coupon_code = user_json_data['coupon_code']
   initial_amount = user_json_data['initial_amount']

   if(coupon.objects.filter(code=coupon_code).exists()):
      coupon_code_object = coupon.objects.get(code=coupon_code)

      if(coupon_code_object.used_count < coupon_code_object.max_limit):

         percentage = coupon_code_object.discount_percent
         discount = float(initial_amount) * percentage / 100
         if(discount <= coupon_code_object.maximum_discount):
            final_amount = float(initial_amount) - discount
         else:
            final_amount = float(initial_amount) - coupon_code_object.maximum_discount
      
         used_count = coupon_code_object.used_count

         coupon.objects.filter(code=coupon_code).update(used_count=used_count + 1)

         return JsonResponse({'amount': final_amount, 'message': 'Coupon applied'})

      return JsonResponse({'amount': float(initial_amount), 'message': 'Coupon expired'})

   return JsonResponse({'amount': float(initial_amount), 'message': 'Wrong coupon code'})


@csrf_exempt
def submit_review(request):
   id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
   claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
   if not claims:
      return HttpResponse('Unauthorized')
   phone_number = claims['firebase']['identities']['phone'][0][3:13]
   #phone_number = '9971209698'

   user_json_data=json.loads(request.body)
        
   booking_id = user_json_data['booking_id']
   rating = user_json_data['rating']
   review = user_json_data['review']

   if(booking.objects.filter(booking_id=booking_id).exists()):
      try:
         booking_object = booking.objects.filter(booking_id=booking_id).update(rating=rating, review=review)

         db = firestore.Client()
         doc_ref = db.collection(u'user_status').document(phone_number)
         doc = doc_ref.get()
         allCourseBlocks = doc.to_dict()

         driver_phone_number = allCourseBlocks['driver']

         driver_details = driver.objects.get(phone_number=driver_phone_number)

         if(rating == 5):
            total_five_stars = driver_details.five_stars + 1
            total_four_stars = driver_details.four_stars
            total_three_stars = driver_details.three_stars
            total_two_stars = driver_details.two_stars
            total_one_stars = driver_details.one_stars
         elif(rating == 4):
            total_five_stars = driver_details.five_stars
            total_four_stars = driver_details.four_stars + 1
            total_three_stars = driver_details.three_stars
            total_two_stars = driver_details.two_stars
            total_one_stars = driver_details.one_stars
         elif(rating == 3):
            total_five_stars = driver_details.five_stars
            total_four_stars = driver_details.four_stars
            total_three_stars = driver_details.three_stars + 1
            total_two_stars = driver_details.two_stars
            total_one_stars = driver_details.one_stars
         elif(rating == 2):
            total_five_stars = driver_details.five_stars
            total_four_stars = driver_details.four_stars
            total_three_stars = driver_details.three_stars 
            total_two_stars = driver_details.two_stars + 1
            total_one_stars = driver_details.one_stars
         elif(rating == 1):
            total_five_stars = driver_details.five_stars
            total_four_stars = driver_details.four_stars
            total_three_stars = driver_details.three_stars
            total_two_stars = driver_details.two_stars
            total_one_stars = driver_details.one_stars + 1
         else:
            total_five_stars = driver_details.five_stars
            total_four_stars = driver_details.four_stars
            total_three_stars = driver_details.three_stars
            total_two_stars = driver_details.two_stars
            total_one_stars = driver_details.one_stars
         
         driver.objects.filter(phone_number=driver_phone_number).update(five_stars=total_five_stars, four_stars=total_four_stars, three_stars=total_three_stars, two_stars=total_two_stars, one_stars=total_one_stars)
         return JsonResponse({'status': '201', 'message': 'Successfully updated'})
      except Exception as e:
         return HttpResponse(e)


   else:
      return JsonResponse({'status': '404', 'message': 'Booking not found'})

@csrf_exempt
def add_ride_later_bookings(request):
   id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
   claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
   if not claims:
      return HttpResponse('Unauthorized')
   phone_number = claims['firebase']['identities']['phone'][0][3:13]
   #phone_number = '9933956490'

   user_json_data=json.loads(request.body)
        
   pickup_location_longitude = user_json_data['pickup_location_longitude']
   pickup_location_latitude = user_json_data['pickup_location_latitude']
   drop_location_longitude = user_json_data['drop_location_longitude']
   drop_location_latitude = user_json_data['drop_location_latitude']
   timestamp = user_json_data['timestamp']
   service_type = user_json_data['service_type']
   payment_mode = user_json_data['payment_mode']

   booking_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
   user = namo_user.objects.get(phone_number=phone_number)
   selected_service = services.objects.get(name=service_type)

   try:
      ride_data = ride_later_booking(
                           booking_id = booking_id,
                           customer = user,
                           timestamp = datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f'),
                           pickup_location_longitude = float(pickup_location_longitude),
                           pickup_location_latitude = float(pickup_location_latitude),
                           drop_location_longitude = float(drop_location_longitude),
                           drop_location_latitude = float(drop_location_latitude),
                           service_type = selected_service,
                           payment_mode = payment_mode
                           )
      
      ride_data.save()      
      return JsonResponse({'status': '201', 'message': 'Successfully Added'})
   except Exception as e:
      return HttpResponse(e)


@csrf_exempt
def process_ride_later_bookings(request):
   booking_objects = ride_later_booking.objects.select_related('customer').filter(timestamp__gte=datetime.datetime.now() - datetime.timedelta(minutes=10), timestamp__lte=datetime.datetime.now() + datetime.timedelta(minutes=5))

   db = firestore.Client()

   for booking_object in booking_objects:
      
      try:
         
         doc_ref = db.collection(u'user_status').document(booking_object.customer.phone_number)
         doc = doc_ref.get()
         Blocks = doc.to_dict()
                  
         Blocks['status'] = '2'
         Blocks['longitude'] = str(booking_object.pickup_location_longitude)
         Blocks['latitude'] = str(booking_object.pickup_location_latitude)
         Blocks['drop_longitude'] = str(booking_object.drop_location_longitude)
         Blocks['drop_latitude'] = str(booking_object.drop_location_latitude)
         Blocks['type'] = booking_object.service_type.name.lower()
         Blocks['payment_mode'] = booking_object.payment_mode

         doc_ref.set(Blocks)

         ride_later_booking.objects.filter(booking_id=booking_object.booking_id).delete()

      except Exception as e:
         return HttpResponse(e)

   return JsonResponse({'status': '202', 'message': 'Job started'})

@csrf_exempt
def change_destination(request):
   id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
   claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
   if not claims:
      return HttpResponse('Unauthorized')
   phone_number = claims['firebase']['identities']['phone'][0][3:13]
   #phone_number="9933956490"

   user_json_data=json.loads(request.body)
        
   booking_id = user_json_data['booking_id']
   latitude = user_json_data['latitude']
   longitude = user_json_data['longitude']
   fare = user_json_data['fare']
   if(booking.objects.filter(booking_id=booking_id).exists()):
      booking_object = booking.objects.get(booking_id=booking_id)
      
      if(booking_object.trip_status == 'ongoing'):
         try:
            
            db = firestore.Client()

            doc_ref1 = db.collection(u'user_status').document(phone_number)
            doc1 = doc_ref1.get()
            allCourseBlocks1 = doc1.to_dict()
            driver_phone_number = allCourseBlocks1['driver']
            allCourseBlocks1['drop_latitude'] = str(latitude)
            allCourseBlocks1['drop_longitude'] = str(longitude)
            allCourseBlocks1['fare'] = str(fare)
            doc_ref1.set(allCourseBlocks1)


            doc_ref = db.collection(u'locations').document(driver_phone_number)
            doc = doc_ref.get()
            allCourseBlocks = doc.to_dict()
            
            allCourseBlocks['drop_latitude'] = str(latitude)
            allCourseBlocks['drop_longitude'] = str(longitude)
            allCourseBlocks['fare'] = str(fare)
            doc_ref.set(allCourseBlocks)

            booking.objects.filter(booking_id=booking_id).update(drop_location_longitude=longitude, drop_location_latitude=latitude, final_amount=float(fare))

            return JsonResponse({'status': '202', 'message': 'updated'})
         except Exception as e:
            return HttpResponse(e)
      else:
         return JsonResponse({'status': '404', 'message': 'Booking not found'})