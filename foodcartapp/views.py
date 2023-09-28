import json
from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Product, Order, OrderItem


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['POST'])
def register_order(request):
    try:
        customer_data = request.data

        products = customer_data['products']

        if not isinstance(products, list):
            return Response({'error': 'Products key not presented or not list'},
                            status=400)
        order = Order(
            firstname=customer_data.get('firstname'),
            lastname=customer_data.get('lastname'),
            phonenumber=customer_data.get('phonenumber'),
            address=customer_data.get('address')
        )
        order.save()
        for product_data in customer_data['products']:
            product_id = product_data['product']
            quantity = product_data['quantity']

            product = Product.objects.get(pk=product_id)

            order_item = OrderItem(
                order=order,
                product_name=product.name,
                quantity=quantity,
                price=product.price
            )
            order_item.save()

        return Response({'message': 'Data successfully processed'})
    except json.JSONDecodeError as e:
        return Response({'error': 'Invalid JSON data', 'details': str(e)})
