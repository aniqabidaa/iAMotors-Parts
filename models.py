from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from .makes_models import car_models

# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)
    description = models.TextField(null=False, blank=False)
    image = models.ImageField(upload_to='products/')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    condition = models.CharField(max_length=50, null=True, blank=True)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    brand = models.ForeignKey('Brand', on_delete=models.CASCADE)
    seller = models.ForeignKey('Seller', on_delete=models.CASCADE)
    model = models.CharField(max_length=255, null=True, blank=True, choices=[(i, i) for i in car_models])
    year = models.IntegerField(null=True, blank=True, choices=[(i, i) for i in range(1990, 2026)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)
    

class FeaturedProduct(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.product.name)


class Seller(models.Model):
    user = models.OneToOneField('accounts.CustomUser', on_delete=models.CASCADE)
    business_name = models.CharField(max_length=255)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.business_name)


@receiver(pre_delete, sender=Seller)
def change_is_seller_status(sender, instance, **kwargs):
    instance.user.is_seller = False
    instance.user.save()
    

class Category(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False, unique=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)
    

class Brand(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False, unique=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)
    

class Cart(models.Model):
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.user.email + ' ' + self.product.name)

    @property
    def total_price(self):
        return self.product.price * self.quantity


class Order(models.Model):
    buyer = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(name='order_date',auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(str(self.id) + " " + self.buyer.email)
    

class OrderDetail(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.order.buyer.email + ' ' + self.product.seller.user.email)
    
    @property
    def total_price(self):
        return self.price * self.quantity
    

class Payment(models.Model):
    order = models.OneToOneField('Order', on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=50)
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2)
    zip_code = models.CharField(max_length=10)
    created_at = models.DateTimeField(name='payment_date', auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.order.buyer.email)
    

class Shipping(models.Model):
    order = models.OneToOneField('Order', related_name='shipping', on_delete=models.CASCADE)
    shipping_method = models.CharField(max_length=50)
    estimated_delivery_date = models.DateTimeField()
    is_shipped = models.BooleanField(default=False)
    is_delivered = models.BooleanField(default=False)
    delivered_date = models.DateTimeField(null=True, blank=True)
    tracking_number = models.CharField(max_length=50)
    address = models.ForeignKey('Address', on_delete=models.CASCADE)
    created_at = models.DateTimeField(name='shipping_date', auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.order.buyer.email)
    

class Address(models.Model):
    buyer = models.ForeignKey('accounts.CustomUser', related_name='buyer_address', on_delete=models.CASCADE)
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.street + ' ' + self.city + ' ' + self.state)
    

class Review(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    buyer = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(name='review_date', auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.user.email + ' ' + self.product.name)