from django.http import JsonResponse
from .makes_models import car_models
from django.views.decorators.cache import cache_page

@cache_page(60 * 15)
def get_car_models(request):
    return JsonResponse(car_models, safe=False)