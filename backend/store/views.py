from django.shortcuts import render,get_object_or_404
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Category,Product,Cart,CartItem,Order,OrderItem,UserProfile
from .serializer import CategorySerializer,ProductsSerializer,CartSerializer,CartItemSerializer,RegisterSerializer,UserSerializer



@api_view(['GET'])
def get_products(request):
    products=Product.objects.all()
    serializer=ProductsSerializer(products,many=True)
    return Response(serializer.data,status=status.HTTP_200_OK)

@api_view(['GET'])
def get_product(request,pk):
    product=get_object_or_404(Product,id=pk)
    serializer=ProductsSerializer(product,context={'request':request})
    return Response(serializer.data,status=status.HTTP_200_OK)


@api_view(['GET'])
def get_category(request):
    categories=Category.objects.all()
    serializer=CategorySerializer(categories,many=True)
    return Response(serializer.data,status=status.HTTP_200_OK)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_cart(request):
    cart,created=Cart.objects.get_or_create(user=request.user)
    serializer=CartSerializer(cart)
    return Response(serializer.data,status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_cart(request):
    product_id=request.data.get('product_id')
    product=get_object_or_404(Product,id=product_id)
    cart,created=Cart.objects.get_or_create(user=request.user)
    item,created=CartItem.objects.get_or_create(cart=cart,product=product)
    if not created:
        item.quantity+=1
        item.save()
    return Response({'Message':'Product added to cart','Cart':CartSerializer(cart).data},status=status.HTTP_200_OK)
    


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_cart_quantity(request):
    item_id=request.data.get('item_id')
    quantity=request.data.get('quantity')
    if not item_id or quantity is None:
        return Response({'error':'Item id and quantity required'},status=status.HTTP_400_BAD_REQUEST)
    item=get_object_or_404(CartItem,id=item_id,cart__user=request.user)
    quantity=int(quantity)
    if quantity<1:
        item.delete()
        return Response({'Message':'Product remove from cart'},status=status.HTTP_200_OK)
    item.quantity=quantity
    item.save()
    serializer=CartItemSerializer(item)
    return Response(serializer.data,status=status.HTTP_200_OK)




@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_from_cart(request):
    item_id=request.data.get('item_id')
    CartItem.objects.filter(id=item_id,cart__user=request.user).delete()
    return Response({'Message':'Item remove from cart'},status=status.HTTP_200_OK)



@api_view(['POST'])
def register_view(request):
    serializer=RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user=serializer.save()
        return Response({'Message':'Registration successful','User':UserSerializer(user).data},status=status.HTTP_201_CREATED)
    return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    data=request.data 
    name=data.get('name')
    phone=data.get('phone')
    address=data.get('address')
    payment=data.get('payment','COD')

    if not name or not phone or not address:
        return Response({'Error':'Name,phone or address required'},status=status.HTTP_400_BAD_REQUEST)
    if not phone.isdigit() or len(phone)!=11:
        return Response({'Error':'Required a valid phone number'},status=status.HTTP_400_BAD_REQUEST)
    
    cart,created=Cart.objects.get_or_create(user=request.user)
    if not cart.items.exists():
        return Response({'Message':'Cart is empty'},status=status.HTTP_400_BAD_REQUEST)

    items=cart.items.all()
    total=sum(item.product.price*item.quantity for item in items)

    order=Order.objects.create(user=request.user,
                               name=name,
                               phone=phone,
                               address=address,
                               payment_method=payment,
                               total_amount=total)
    for item in items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price,
        )
    items.delete()
    return Response({'Message':'Order created successfully','Order id':order.id},status=status.HTTP_201_CREATED)
