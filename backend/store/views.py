from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Category,Product,Cart,CartItem,Order,OrderItem
from .serializer import CategorySerializer,ProductsSerializer,CartSerilizer,CartItemSerializer


@api_view(['GET'])
def get_products(request):
    products=Product.objects.all()
    serializer=ProductsSerializer(products,many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_product(request,pk):
    try:
        product=Product.objects.get(id=pk)
        serializer=ProductsSerializer(product,context={'request':request})
        return Response(serializer.data)
    except Product.DoesNotExist:
        return Response({'error':'Product not found'},status=404)


@api_view(['GET'])
def get_category(request):
    category=Category.objects.all()
    serializer=CategorySerializer(category,many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_cart(request):
    cart,created=Cart.objects.get_or_create(user=request.user)
    serilizer=CartSerilizer(cart)
    return Response(serilizer.data)

@api_view(['POST'])
def add_to_cart(request):
    product_id=request.data.get('product_id')
    product=Product.objects.get(id=product_id)
    cart,created=Cart.objects.get_or_create(user=request.user)
    item,created=CartItem.objects.get_or_create(cart=cart,product=product)
    if not created:
        item.quantity +=1
        item.save()
    return Response({'message':'Product added to cart','cart':CartSerilizer(cart).data})

@api_view(['POST'])
def update_cart_quantity(request):
    item_id=request.data.get('item_id')
    quantity=request.data.get('quantity')
    if not item_id or quantity is None:
        return Response({'error':'Item id and quantity is required'},status=400)
    try:
        item=CartItem.objects.get(id=item_id)
        if int(quantity)<1:
            item.delete()
            return Response({'message': 'Item removed from cart'},status=200)
        item.quantity=quantity
        item.save()
        serializer=CartItemSerializer(item)
        return Response(serializer.data)
    except CartItem.DoesNotExist:
        return Response({'error':'Cart item is not found'},status=404)

@api_view(['POST'])
def remove_from_cart(request):
    item_id=request.data.get('item_id')
    CartItem.objects.filter(id=item_id).delete()
    return Response({'message':'Item remove from cart'})

