from .models import Cart
from django.db.models import Sum
from django.db.models.functions import Coalesce

import math

def cart_total_items(request):
    return Cart.objects.filter(user=request.user).aggregate(total_items=Coalesce(Sum('quantity'),0))['total_items'] if request.user.is_authenticated else 0

def custom_round(number):
    if number - math.floor(number) < 0.5:
        return math.floor(number)
    return math.ceil(number)