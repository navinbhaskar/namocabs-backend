"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from jet.dashboard.dashboard_modules import google_analytics_views
from django.contrib import admin
from django.urls import include, path


admin.site.site_header = "NamoCabs Admin"
admin.site.site_title = "NamoCabs Admin Portal"
admin.site.index_title = "Welcome to NamoCabs Admin Portal"

urlpatterns = [
    path('', admin.site.urls),
    path('jet_api/', include('jet_django.urls')),
    path(r'^jet/', include('jet.urls', 'jet')),
    path(r'^jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),
    path('admin/', admin.site.urls),
    path('booking/', include('mysite.namo_booking.urls')),
    path('user/', include('mysite.namo_user.urls')),
    path('services/', include('mysite.namo_services.urls')),
]
