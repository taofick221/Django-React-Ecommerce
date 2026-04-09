from django.shortcuts import render
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated,AllowAny
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response
from .models import Category,Product,Cart,CartItem,Order,OrderItem
from .serializer import CategorySerializer,ProductsSerializer,CartSerializer,CartItemSerializer,UserSerializer,RegisterSerializer


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
@permission_classes([IsAuthenticated])
def get_cart(request):
    cart,created=Cart.objects.get_or_create(user=request.user)
    serializer=CartSerializer(cart)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_cart(request):
    product_id=request.data.get('product_id')
    product=Product.objects.get(id=product_id)
    cart,created=Cart.objects.get_or_create(user=request.user)
    item,created=CartItem.objects.get_or_create(cart=cart,product=product)
    if not created:
        item.quantity +=1
        item.save()
    return Response({'message':'Product added to cart','cart':CartSerializer(cart).data})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
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
@permission_classes([IsAuthenticated])
def remove_from_cart(request):
    item_id=request.data.get('item_id')
    CartItem.objects.filter(id=item_id).delete()
    return Response({'message':'Item remove from cart'})


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    serializer=RegisterSerializer(data=request.data)
    if serializer.is_valid():
       user= serializer.save()
       return Response({"message":"Register successfully","user":UserSerializer(user).data},status=status.HTTP_201_CREATED)
    return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    try:
        data=request.data 
        name=data.get('name')
        address=data.get('address')
        phone=data.get('phone')
        payment=data.get('payment','COD')

        # phone number validation
        if not phone.isdigit() or len(phone)<10:
            return Response({"message":"Phone number is not valid"},status=400)
        
        # Get user cart
        cart,created=Cart.objects.get_or_create(user=request.user)
        if not cart.items.exists():
            return Response({"message":"Cart is empty"},status=400)
        
        total=sum([item.product.price * item.quantity for item in cart.items.all()])

        order= Order.objects.create(user=request.user,total_amount=total)

        for item in cart.items.all():
            OrderItem.objects.create(
            order=order,
           product=item.product,
           quantity=item.quantity,
           price=item.product.price,
            )
        # clear cart
        cart.items.all().delete()
        return Response({"message":"Order created successfully","order_id":order.id})
    except Exception as e:
        return Response({'error':str(e)},status=500)

