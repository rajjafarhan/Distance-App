from django.urls import path
from . import views

# URL configuration for playground app
urlpatterns = [
    path('', views.say_hello),  # This will make the root URL (/) show the hello page
    path('hello/', views.say_hello),  # Keep the hello page as well
    path('calculate/', views.calculate_distance),  # Your distance calculator
]
