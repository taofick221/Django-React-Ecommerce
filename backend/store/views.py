from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Category,Product
from .serializer import CategorySerializer,ProductsSerializer


@api_view(['GET'])
def get_products(request):
    products=Product.objects.all()
    serializer=ProductsSerializer(products,many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_category(request):
    category=Category.objects.all()
    serializer=CategorySerializer(category,many=True)
    return Response(serializer.data)