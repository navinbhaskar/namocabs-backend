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
from . models import services, vehicle, city_availability, promo_code, promotions, saved_location
import sys
sys.path.append("..")
from mysite.namo_user.models import namo_user, driver

HTTP_REQUEST = google.auth.transport.requests.Request()

@csrf_exempt
def fetch_services_data(request):
   id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
   claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
   if not claims:
      return HttpResponse('Unauthorized')

   services_list = []
   services_object = services.objects.all()

   all_drivers = driver.objects.all().count()
   available_drivers = driver.objects.filter(availability='available').count()
   #return HttpResponse(str(all_drivers)+"||"+str(available_drivers))
   multiplier=1
   if(all_drivers != 0):
      multiplier = all_drivers/(available_drivers+1)


   for service in services_object:
        data = {
            "name": service.name,
            "icon": service.icon,
            "card_image": service.card_image,
            "fixed_amount": service.fixed_amount,
            "rate": service.rate * multiplier
        }

        services_list.append(data)

   
   return JsonResponse(services_list, safe = False)


@csrf_exempt
def fetch_services_data_location_wise(request):
   id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
   claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
   if not claims:
      return HttpResponse('Unauthorized')

   location_data=json.loads(request.body)
   city = location_data['city']
   state =location_data['state']

   availability = city_availability.objects.select_related('service_type').filter(city = city).filter(state = state)
   #return HttpResponse(availability[0].service_type.name)

   services_list = []
   services_object = services.objects.all()


   for service in services_object:
      available = False
      for available_service in availability:
         if(service.name == available_service.service_type.name):
            available = True
            data = {
                  "name": service.name,
                  "icon": service.icon,
                  "card_image": service.card_image,
                  "availability": True
            }
            services_list.append(data)
      if not available:
         data = {
               "name": service.name,
               "icon": service.icon,
               "card_image": service.card_image,
               "availability": False
         }
         services_list.append(data)
  
   return JsonResponse(services_list, safe = False)

@csrf_exempt
def fetch_promo_code(request):
   id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
   claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
   if not claims:
      return HttpResponse('Unauthorized')

   promo_list = []
   promo_object = promo_code.objects.all()


   for code in promo_object:
        data = {
            "title": code.title,
            "subtitle": code.subtitle,
            "promo_code": code.promo_code,
            "terms": code.terms,
            "image": code.image
        }

        promo_list.append(data)

   
   return JsonResponse(promo_list, safe = False)


@csrf_exempt
def fetch_promotion_code(request):
   id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
   claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
   if not claims:
      return HttpResponse('Unauthorized')

   promo_list = []
   promo_object = promotions.objects.all()


   for code in promo_object:
        data = {
            "title": code.title,
            "subtitle": code.subtitle,
            "promo_code": code.promotion_code,
            "terms": code.terms,
            "image": code.image
        }

        promo_list.append(data)

   
   return JsonResponse(promo_list, safe = False)


@csrf_exempt
def add_location(request):
   id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
   claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
   if not claims:
      return HttpResponse('Unauthorized')
   phone_number = claims['firebase']['identities']['phone'][0][3:13]

   #phone_number = '8840885843'

   user_json_data=json.loads(request.body)

   user =  namo_user.objects.get(phone_number=phone_number)
        
   name = user_json_data['name']
   longitude = user_json_data['longitude']
   latitude = user_json_data['latitude']
   location = user_json_data['location']
   complete_address = user_json_data['complete_address']
   
   try:
      location = saved_location(user=user,
                           name=name,
                           longitude=longitude,
                           latitude=latitude,
                           location=location,
                           complete_address=complete_address
                           )
      
      location.save()
      return JsonResponse({'status': '201', 'message': 'Successfully created'})
   except Exception as e:
      return HttpResponse(e)

@csrf_exempt
def fetch_saved_locations(request):
   id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
   claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
   if not claims:
      return HttpResponse('Unauthorized')

   phone_number = claims['firebase']['identities']['phone'][0][3:13]

   #phone_number = '8840885843'

   locations_list = []
   location_object = saved_location.objects.filter(user__phone_number=phone_number)


   for location in location_object:
        data = {
            "id": location.location_id,
            "location": location.name,
            "longitude": location.longitude,
            "latitude": location.latitude,
            "location": location.location,
            "complete_address": location.complete_address
        }

        locations_list.append(data)

   
   return JsonResponse(locations_list, safe = False)

@csrf_exempt
def delete_locations(request, location_id):
   id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
   claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
   if not claims:
      return HttpResponse('Unauthorized')

   phone_number = claims['firebase']['identities']['phone'][0][3:13]

   #phone_number = '8840885843'

   locations_list = []
   location_object = saved_location.objects.filter(user__phone_number=phone_number, location_id = location_id).delete()

   return JsonResponse({'status': '200', 'message': 'Successfully deleted'})