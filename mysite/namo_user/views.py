from django.shortcuts import render
from rest_framework.views import APIView
from django.http import HttpResponse
from django.http import JsonResponse
import json
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
import datetime
import random
import google.oauth2.id_token
import google.auth.transport.requests
from django.views.decorators.csrf import csrf_exempt
from . models import namo_user, driver
from firebase_admin import firestore

HTTP_REQUEST = google.auth.transport.requests.Request()



@csrf_exempt
def fetch_user_data(request):
   id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
   claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
   if not claims:
      return HttpResponse('Unauthorized')

   username = claims['firebase']['identities']['phone'][0][3:13]
   #username = '8840885843'
   if(namo_user.objects.filter(phone_number=username).exists()):
      user = namo_user.objects.get(phone_number=username)

      data = {
         'firstname': user.firstname,
         'lastname': user.lastname,
         'gender': user.gender,
         'phone_number': user.phone_number,
         'email': user.email,
         'rating': user.rating,
         'photo': user.photo,
         'status': '200'
      }

      return JsonResponse(data)
   else:
      return JsonResponse({'status': '404', 'message': 'User Not Found'})

@csrf_exempt
def create_profile(request):
   id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
   claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
   if not claims:
      return HttpResponse('Unauthorized')
   phone_number = claims['firebase']['identities']['phone'][0][3:13]
   

   user_json_data=json.loads(request.body)

   if namo_user.objects.filter(phone_number=phone_number).exists():
        return JsonResponse({'status': '208', 'message': 'User already exists'})
        
   firstname = user_json_data['firstname']
   lastname = user_json_data['lastname']
   gender = user_json_data['gender']
   email = user_json_data['email']
   
   try:
      userData = namo_user(firstname=firstname,
                           lastname=lastname,
                           gender=gender,
                           phone_number=phone_number,
                           email=email,
                           login_type='phone'
                           )
      
      userData.save()

      db = firestore.Client()
      doc_ref = db.collection(u'user_status').document(phone_number)
      doc = doc_ref.get()

      new_dict = {
         "booking_id": "",
         "driver": "null",
         "drop_latitude": "",
         "drop_longitude": "",
         "fare": "",
         "is_available": True,
         "latitude": "",
         "longitude": "",
         "otp": "",
         "phone_number": phone_number,
         "status": 1,
         "type": "null"
      }

      try:
         if(doc.to_dict() == None):
            doc_ref.set(new_dict)
      except:
            pass

      return JsonResponse({'status': '201', 'message': 'Successfully created'})
   except Exception as e:
      return HttpResponse(e)


@csrf_exempt
def fetch_user_data_new_booking(request):
   id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
   claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
   if not claims:
      return HttpResponse('Unauthorized')

   user_json_data=json.loads(request.body)

   #try:
   #   longitude = user_json_data['longitude']
   #   latitude = user_json_data['latitude']
   #except: 
   #   return JsonResponse({'status': '400', 'message': 'Bad Request'})

   user = namo_user.objects.get(phone_number=user_json_data['phone_number'])

   data = {
        'firstname': user.firstname,
        'lastname': user.lastname,
        'gender': user.gender,
        'phone_number': user.phone_number,
        'rating': user.rating,
        #'longitude': longitude,
        #'latitude': latitude,
        'status': '200'
   }

   return JsonResponse(data)

@csrf_exempt
def fetch_driver_data_to_user(request):
   id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
   claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
   if not claims:
      return HttpResponse('Unauthorized')

   user_json_data=json.loads(request.body)

   if(driver.objects.filter(phone_number=user_json_data['phone_number']).exists()):

      user = driver.objects.get(phone_number=user_json_data['phone_number'])

      total_ratings = user.five_stars + user.four_stars + user.three_stars + user.two_stars + user.one_stars
      rating = round((5 * user.five_stars + 4 * user.four_stars + 3 * user.three_stars + 2 * user.two_stars + user.one_stars) / total_ratings, 2) if total_ratings != 0 else 'Null'

      data = {
         'firstname': user.firstname,
         'lastname': user.lastname,
         'gender': user.gender,
         'phone_number': user.phone_number,
         'rating': rating,
         'photo': user.photo,
         'number_of_trips': user.number_of_trips,
         'status': '200'
      }

      return JsonResponse(data)
   else:
      return JsonResponse({'status': '404', 'message': 'User Not Found'})


@csrf_exempt
def fetch_driver_data(request):
   id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
   claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
   if not claims:
      return HttpResponse('Unauthorized')

   username = claims['firebase']['identities']['phone'][0][3:13]
   

   if(driver.objects.filter(phone_number=username).exists()):
      user = driver.objects.get(phone_number=username)

      total_ratings = user.five_stars + user.four_stars + user.three_stars + user.two_stars + user.one_stars
      rating = round((5 * user.five_stars + 4 * user.four_stars + 3 * user.three_stars + 2 * user.two_stars + user.one_stars) / total_ratings, 2) if total_ratings != 0 else 'Null'

      data = {
         'firstname': user.firstname,
         'lastname': user.lastname,
         'gender': user.gender,
         'phone_number': user.phone_number,
         'rating': rating,
         'photo': user.photo,
         'number_of_trips': user.number_of_trips,
         'status': '200'
      }

      return JsonResponse(data)
   else:
      return JsonResponse({'status': '404', 'message': 'User Not Found'})


@csrf_exempt
def create_profile_driver(request):
   id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
   claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
   if not claims:
      return HttpResponse('Unauthorized')
   phone_number = claims['firebase']['identities']['phone'][0][3:13]
   #phone_number = '8005580211'
   user_json_data=json.loads(request.body)

   if driver.objects.filter(phone_number=phone_number).exists():
      return JsonResponse({'status': '409', 'message': 'User already exists'})
        
   firstname = user_json_data['firstname']
   lastname = user_json_data['lastname']
   gender = user_json_data['gender']
   address = user_json_data['address']
   licence_number = user_json_data['licence_number']
   city = user_json_data['city']
   pan_card = user_json_data['pan_card']


   try:
      userData = driver(firstname=firstname,
                           lastname=lastname,
                           gender=gender,
                           phone_number=phone_number,
                           address=address,
                           photo='',
                           number_of_trips=0,
                           current_debt_amount=0,
                           city = city,
                           pan_card = pan_card,
                           licence_number=licence_number
                           )
      
      userData.save()

      db = firestore.Client()
      doc_ref = db.collection(u'locations').document(phone_number)
      doc = doc_ref.get()

      new_dict = {
         "booking_id": "",
         "customer": "null",
         "drop_latitude": "",
         "drop_longitude": "",
         "fare": "",
         "is_available": True,
         "latitude": "0",
         "longitude": "0",
         "otp": "",
         "otp_verified": "",
         "phone_number": phone_number,
         "pickup_latitude": "",
         "pickup_longitude": "",
         "status": "available",
         "type": "null"
      }

      try:
         if(doc.to_dict() == None):
            doc_ref.set(new_dict)
      except:
            pass

      return JsonResponse({'status': '201', 'message': 'Successfully created'})
   except Exception as e:
      return HttpResponse(e)


@csrf_exempt
def check_user_status(request):
   id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
   claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
   if not claims:
      return HttpResponse('Unauthorized')
   phone_number = claims['firebase']['identities']['phone'][0][3:13]
   #phone_number = '9933956490'
      
   if namo_user.objects.filter(phone_number=phone_number).exists():
      return JsonResponse({'data': True, 'status': '409', 'message': 'User already exists'})
   else:
      return JsonResponse({'data': False, 'status': '404', 'message': 'User not found'})


@csrf_exempt
def update_user_profile(request):
   id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
   claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
   if not claims:
      return HttpResponse('Unauthorized')
   user_json_data=json.loads(request.body)
   phone_number = claims['firebase']['identities']['phone'][0][3:13]
   #phone_number = "8840885843"
   
   if namo_user.objects.filter(phone_number=phone_number).exists():
      namo_user_object = namo_user.objects.get(phone_number=phone_number)
      try:
         if user_json_data['firstname'] is not None:
            namo_user_object.firstname = user_json_data['firstname']
      except Exception as e:
         pass
      
      try:
         if user_json_data['lastname'] is not None:
            namo_user_object.lastname = user_json_data['lastname']
      except Exception as e:
         pass
      
      try:
         if user_json_data['email'] is not None:
            namo_user_object.email = user_json_data['email']
      except Exception as e:
         pass
      
      try:
         if user_json_data['photo'] is not None:
            namo_user_object.photo = user_json_data['photo']
      except Exception as e:
         pass

      try:
         if user_json_data['gender'] is not None:
            if(user_json_data['gender'] == 'Male'):
               namo_user_object.gender = '1'
            elif(user_json_data['gender']=='Female'):
               namo_user_object.gender = '2'
            else:
               pass
      except Exception as e:
         pass

      namo_user_object.save()
      return JsonResponse({'status': '202', 'message': 'Successfully updated'})