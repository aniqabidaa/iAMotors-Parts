from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views
from . import apis

app_name = "store"

urlpatterns = [
    path("", views.index, name="index"),
    path("api/get-car-models/", apis.get_car_models, name="get_car_models"),
    path("seller/", views.seller_index, name="seller_index"),
    path("products/", views.product_list, name="product_list"),
    path("product/<int:product_id>/", views.product_detail, name="product_detail"),
    path('product/review/<int:product_id>/', views.add_review, name='add_review'),
    path("seller-products/", views.seller_product_list, name="seller_product_list"),
    path("seller-product-update/<int:pk>/", views.SellerProductUpdate.as_view(), name="seller_product_update"),
    path("seller-product-create/", views.SellerProductCreate.as_view(), name="seller_product_create"),
    path("seller-product/<int:product_id>/", views.seller_product_detail, name="seller_product_detail"),
    path("seller/orders/", views.seller_order_list, name="seller_order_list"),
    path("seller/order/<int:id>/", views.seller_order_detail, name="seller_order_detail"),
    path("seller/order/<int:order_detail_id>/update-delivery/", views.update_delivery_status, name="update_delivery_status"),
    path("seller/order/<int:order_detail_id>/update-shipped/", views.update_shipped_status, name="update_shipped_status"),
    path("category/<int:category_id>/", views.category_product_list, name="category_product_list"),
    path("add-to-cart/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("remove-from-cart/<int:cart_id>/", views.remove_from_cart, name="remove_from_cart"),
    path("increment-cart-item/<int:cart_id>/", views.increment_cart_item, name="increment_cart_item"),
    path("decrement-cart-item/<int:cart_id>/", views.decrement_cart_item, name="decrement_cart_item"),
    path("clear-cart/", views.clear_cart, name="clear_cart"),
    path("cart/", views.cart, name="cart"),
    path("order-history/", views.order_history, name="order_history"),
    path("checkout/", views.checkout, name="checkout"),
    path("create-intent", views.create_intent, name="create_intent"),
    path("payment-success/", views.payment_success, name="payment_success"),
    path("stripe-webhooks/", views.stripe_webhooks, name="stripe_webhooks"),
    path("login/", views.signin, name="login"),
    path("seller-login/", views.seller_signin, name="seller_login"),
    path("signup/", views.signup, name="signup"),
    path("seller-signup/", views.seller_signup, name="seller_signup"),
    path("upgrate-to-seller/", views.upgrade_to_seller, name="upgrade_to_seller"),
    path("logout/", views.signout, name="logout"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
