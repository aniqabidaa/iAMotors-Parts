from django.contrib import admin
from .models import Product, Category, Brand, Seller, Cart, Order, OrderDetail, Payment, Shipping, Address, Review, FeaturedProduct

# Register your models here.

class ProductCategoryFilter(admin.SimpleListFilter):
    title = 'category'
    parameter_name = 'category'

    def lookups(self, request, model_admin):
        categories = Category.objects.all()
        return [(category.id, category.name) for category in categories]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(category__id=self.value())
        return queryset
    

class ProductBrandFilter(admin.SimpleListFilter):
    title = 'brand'
    parameter_name = 'brand'

    def lookups(self, request, model_admin):
        brands = Brand.objects.all()
        return [(brand.id, brand.name) for brand in brands]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(brand__id=self.value())
        return queryset


class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'image', 'name', 'price', 'category', 'brand', 'updated_at']
    list_filter = ['price', ProductCategoryFilter, ProductBrandFilter, 'updated_at']
    search_fields = ['name', 'description']


class FeaturedProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'updated_at']
    search_fields = ['product']


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description', 'updated_at']
    search_fields = ['name', 'description']


class BrandAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description', 'updated_at']
    search_fields = ['name', 'description']


class SellerAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'business_name', 'rating', 'active', 'updated_at']
    list_filter = ['business_name', 'rating', 'updated_at']
    search_fields = ['user', 'business_name']


class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'product', 'quantity', 'updated_at']
    list_filter = ['product', 'created_at', 'updated_at']
    search_fields = ['user', 'product']


class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'buyer', 'total_amount', 'is_completed', 'updated_at']
    list_filter = ['buyer', 'updated_at']
    search_fields = ['user', 'status']


class OrderDetailAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'product', 'quantity', 'price', 'total_price', 'updated_at']
    list_filter = ['order', 'product', 'updated_at']
    search_fields = ['order', 'product']


class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'payment_method', 'payment_amount', 'updated_at']
    list_filter = ['payment_method', 'payment_amount', 'updated_at']
    search_fields = ['related_order', 'payment_method']


class ShippingAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'address', 'shipping_method', 'updated_at']
    list_filter = ['shipping_method', 'updated_at']
    search_fields = ['order', 'address']


class AddressAdmin(admin.ModelAdmin):
    list_display = ['id', 'buyer', 'street', 'city', 'state', 'zip_code', 'updated_at']
    list_filter = ['city', 'state', 'zip_code', 'updated_at']
    search_fields = ['buyer', 'city']


class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'buyer', 'rating', 'updated_at']
    list_filter = ['rating', 'updated_at']
    search_fields = ['product', 'buyer']


admin.site.register(Product, ProductAdmin)
admin.site.register(FeaturedProduct, FeaturedProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Brand, BrandAdmin)
admin.site.register(Seller, SellerAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderDetail, OrderDetailAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Shipping, ShippingAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(Review, ReviewAdmin)
