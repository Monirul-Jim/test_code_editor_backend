from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import execute_code

# Define router and register views if needed
router = DefaultRouter()

urlpatterns = [
    path('execute/', execute_code, name='execute_code'),
    path('', include(router.urls)),
]
