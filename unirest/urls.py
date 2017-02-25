"""unirest URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

from rest_framework_mongoengine import routers

# this is DRF router for REST API viewsets
from enrollments.viewsets import CourseViewSet, StudentViewSet
from rest_framework_swagger.views import get_swagger_view

swagger_view = get_swagger_view(title='Unirest API')

router = routers.DefaultRouter()

# register REST API endpoints with DRF router
router.register(r'courses', CourseViewSet, r"courses")
router.register(r'students', StudentViewSet, r"students")

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include(router.urls, namespace='api')),
    url(r'^docs/', swagger_view),
]
