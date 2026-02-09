from django.urls import path
from . import views

urlpatterns = [
    path('products/',views.get_products),
    path('category/',views.get_category),
]
