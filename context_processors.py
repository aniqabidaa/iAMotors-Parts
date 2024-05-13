from .models import Category
from .utitlities import cart_total_items

def categories(request):
    return {
        'categories': Category.objects.all()
    }

def total_items(request):
    return {
        'total_items': cart_total_items(request)
    }