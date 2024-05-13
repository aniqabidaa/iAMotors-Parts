from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.db.models import Q, Prefetch, Avg
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import UpdateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

import stripe
import json
from datetime import datetime, timedelta

from .decorators import redirect_authenticated_user

from accounts.models import CustomUser
from .models import Seller, Product, Cart, FeaturedProduct, Order, OrderDetail, Shipping, Payment, Address, Review, Category
from .utitlities import cart_total_items, custom_round

# Create your views here.
def index(request):
    products = Product.objects.all().order_by('-id')[:6]
    featured_products = FeaturedProduct.objects.select_related('product').all()[:5]
    context = {
        'products': products,
        'featured_products': featured_products
    }

    return render(request, 'store/index.html', context)


@login_required(login_url='store:seller_login', redirect_field_name='next')
def seller_index(request):
    try:
        seller = Seller.objects.get(user=request.user)
    except Seller.DoesNotExist:
        return redirect('store:seller_login')

    orders = OrderDetail.objects.filter(product__seller=seller).select_related('order').prefetch_related('product', 'order__shipping').order_by('order__shipping__is_delivered').all()
    total_sales = sum([order.total_price for order in orders])
    products = Product.objects.filter(seller=seller)


    context = {
        'seller': seller,
        'orders': orders,
        'total_sales': total_sales,
        'products': products,
        'total_items_sold': sum([order.quantity for order in orders]),
        'total_orders': orders.count(),
        'total_products': products.count(),
        'total_customers': orders.values('order__buyer').distinct().count(),
        'recent_orders': orders[:2],
        'total_delivered_orders': orders.filter(order__shipping__is_delivered=True).count(),
        'sidebar_active': 'dashboard'
    }

    return render(request, 'store/seller_index.html', context)


def product_list(request):
    context = {
        'products': [],
    }
    search_query = request.GET.get('search', '')
    model = request.GET.get('models', '')
    year = request.GET.get('year', '')

    if year:
        year = int(year)

    products = Product.objects.all().order_by('-id')
    if search_query:
        print('search_query', search_query)
        # context['products'] = Product.objects.filter(Q(name__icontains=search_query) | Q(description__icontains=search_query) | Q(seller__business_name__icontains=search_query)).order_by('-id')
        products = products.filter(Q(name__icontains=search_query) | Q(description__icontains=search_query) | Q(seller__business_name__icontains=search_query)).order_by('-id')
    
    if model:
        products = products.filter(model=model)
    
    if year:
        products = products.filter(year=year)

    context['products'] = products

    return render(request, 'store/product_list.html', context)


@login_required(login_url='store:seller_login', redirect_field_name='next')
def seller_product_list(request):
    try:
        seller = Seller.objects.get(user=request.user)
    except Seller.DoesNotExist:
        return redirect('store:seller_login')
    
    context = {
        'products': [],
        'seller': seller,
        'sidebar_active': 'my-products'
    }
    search_query = request.GET.get('search', '')
    if search_query:
        context['products'] = Product.objects.filter(Q(seller=seller) & (Q(name__icontains=search_query) | Q(description__icontains=search_query) | Q(seller__business_name__icontains=search_query))).order_by('-id')
    else:
        context['products'] = Product.objects.filter(seller=seller).order_by('-id')

    return render(request, 'store/seller_product_list.html', context)


class SellerProductUpdate(UpdateView, LoginRequiredMixin):
    model = Product
    fields = ['name', 'description', 'image', 'price', 'quantity', 'condition', 'category', 'brand', 'model', 'year']
    template_name = 'store/seller_product_edit.html'
    success_url = '/seller-products/'

    def get_context_data(self, **kwargs):
        try:
            seller = Seller.objects.get(user=self.request.user)
        except Seller.DoesNotExist:
            return redirect('store:seller_login')
        context = super().get_context_data(**kwargs)
        context['header'] = "Update Product"
        context['seller'] = seller
        return context


class SellerProductCreate(CreateView, LoginRequiredMixin):
    model = Product
    fields = ['name', 'description', 'image', 'price', 'quantity', 'condition', 'category', 'brand', 'model', 'year']
    template_name = 'store/seller_product_edit.html'
    success_url = '/seller-products/'

    def get(self, request, *args, **kwargs):
        if not request.user.is_seller:
            return redirect('store:index', context={'error_message': 'You are not a seller'})
        else:
            seller = Seller.objects.get(user=request.user)
            if not seller.active:
                messages.error(request, 'Your account is not active yet')
                return redirect('store:seller_index')
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.seller = Seller.objects.get(user=self.request.user)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        try:
            seller = Seller.objects.get(user=self.request.user)
        except Seller.DoesNotExist:
            return redirect('store:seller_login')
        context = super().get_context_data(**kwargs)
        context['header'] = "Create Product"
        context['seller'] = seller
        return context


def product_detail(request, product_id):
    reviews_with_buyer = Review.objects.select_related('buyer').all()
    product = Product.objects.prefetch_related(
        Prefetch('review_set', queryset=reviews_with_buyer)
    ).get(id=product_id)

    avg_rating = product.review_set.aggregate(Avg('rating'))['rating__avg']
    avg_rating = avg_rating if avg_rating else 0
    avg_rating = custom_round(avg_rating)
    product.avg_rating = avg_rating if avg_rating else 0
    print('avg_rating', avg_rating, custom_round(5.255))

    context = {
        'product': product
    }
    return render(request, 'store/product_detail.html', context)


@login_required(login_url='store:login', redirect_field_name='next')
def add_review(request, product_id):
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        product = get_object_or_404(Product, id=product_id)
        Review.objects.create(product=product, buyer=request.user, rating=rating, comment=comment)
        return redirect('store:product_detail', product_id)


@login_required(login_url='store:seller_login', redirect_field_name='next')
def seller_product_detail(request, product_id):
    try:
        seller = Seller.objects.get(user=request.user)
    except Seller.DoesNotExist:
        return redirect('store:seller_login')
    context = {
        'product': Product.objects.get(id=product_id),
        'seller': seller
    }
    return render(request, 'store/seller_product_detail.html', context)


@login_required(login_url='store:seller_login', redirect_field_name='next')
def seller_order_list(request):
    try:
        seller = Seller.objects.get(user=request.user)
    except Seller.DoesNotExist:
        return redirect('store:seller_login')

    orders = OrderDetail.objects.filter(product__seller=seller).select_related('order').prefetch_related('product', 'order__shipping').order_by('order__shipping__is_delivered').all()

    context = {
        'orders': orders,
        'seller': seller,
        'sidebar_active': 'orders'
    }

    return render(request, 'store/seller_orders.html', context)


@login_required(login_url='store:seller_login', redirect_field_name='next')
def seller_order_detail(request, id):
    try:
        seller = Seller.objects.get(user=request.user)
    except Seller.DoesNotExist:
        return redirect('store:seller_login')

    order = OrderDetail.objects.filter(id=id).select_related('order').prefetch_related('product', 'order__shipping').first()

    context = {
        'order': order,
        'seller': seller,
        'sidebar_active': 'orders'
    }

    return render(request, 'store/seller_order_detail.html', context)


@login_required(login_url='store:seller_login', redirect_field_name='next')
def update_delivery_status(request, order_detail_id):
    order = OrderDetail.objects.get(id=order_detail_id).order
    shipping = Shipping.objects.get(order=order)
    shipping.is_delivered = True
    shipping.delivered_date = datetime.now()
    shipping.save()

    return redirect('store:seller_order_detail', order_detail_id)


@login_required(login_url='store:seller_login', redirect_field_name='next')
def update_shipped_status(request, order_detail_id):
    order = OrderDetail.objects.get(id=order_detail_id).order
    shipping = Shipping.objects.get(order=order)
    shipping.is_shipped = True
    shipping.save()

    return redirect('store:seller_order_detail', order_detail_id)


def category_product_list(request, category_id):
    category = {
        'name': ''
    }
    try:
        category = Category.objects.get(id=category_id)
    except Category.DoesNotExist:
        return redirect('store:index')
    context = {
        'products': Product.objects.filter(category_id=category_id),
        'search_category': category.name
    }
    return render(request, 'store/product_list.html', context)


@login_required(login_url='store:login', redirect_field_name='next')
def add_to_cart(request, product_id):
    referring_url = request.META.get('HTTP_REFERER')
    product = Product.objects.get(id=product_id)
    cart_item = Cart.objects.filter(user=request.user, product=product).first()
    if cart_item:
        cart_item.quantity += 1
        cart_item.save()
    else:
        Cart.objects.create(user=request.user, product=product, quantity=1)
    
    # return redirect('store:index')
    return redirect(referring_url)


@login_required(login_url='store:login', redirect_field_name='next')
def cart(request):
    cart_items = Cart.objects.filter(user=request.user).select_related('product')
    context = {
        'cart_items': cart_items,
        'cart_total_price': sum([cart_item.total_price for cart_item in cart_items]),
    }

    return render(request, 'store/cart.html', context)


@login_required(login_url='store:login', redirect_field_name='next')
def order_history(request):
    orders = Order.objects.filter(buyer=request.user).prefetch_related('orderdetail_set', 'orderdetail_set__product', 'shipping').all()
    context = {
        'orders': orders,
    }
    return render(request, 'store/order_history.html', context)


@login_required(login_url='store:login', redirect_field_name='next')
def remove_from_cart(request, cart_id):
    cart_item = Cart.objects.get(id=cart_id)
    cart_item.delete()
    
    return redirect('store:cart')


@login_required(login_url='store:login', redirect_field_name='next')
def increment_cart_item(request, cart_id):
    cart_item = Cart.objects.get(id=cart_id)
    cart_item.quantity += 1
    cart_item.save()
    
    return redirect('store:cart')


@login_required(login_url='store:login', redirect_field_name='next')
def decrement_cart_item(request, cart_id):
    cart_item = Cart.objects.get(id=cart_id)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    
    return redirect('store:cart')


@login_required(login_url='store:login', redirect_field_name='next')
def clear_cart(request):
    Cart.objects.filter(user=request.user).delete()
    
    return redirect('store:cart')


@login_required(login_url='store:login', redirect_field_name='next')
def checkout(request):
    address = Address.objects.filter(buyer=request.user).first()
    cart_items = Cart.objects.filter(user=request.user).select_related('product')
    context = {
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
        'cart_items': cart_items,
        'cart_total_price': sum([cart_item.total_price for cart_item in cart_items]),
        'address': address,
    }

    order, created = Order.objects.get_or_create(
        buyer=request.user, 
        is_completed=False, 
        defaults={
            'total_amount': context['cart_total_price']
        }
    )

    if not created:
        OrderDetail.objects.filter(order=order).delete()

    order_details_to_create = []

    for cart_item in cart_items:
        order_detail = OrderDetail(
            order=order,
            product=cart_item.product,
            quantity=cart_item.quantity,
            price=cart_item.product.price,
        )
        order_details_to_create.append(order_detail)

    # Bulk create the order details
    OrderDetail.objects.bulk_create(order_details_to_create)

    order.total_amount = context['cart_total_price']
    order.save()
    context['order_id'] = order.id

    return render(request, 'store/stripe_checkout.html', context)


def create_intent(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    if request.method == 'POST':
        body = json.loads(request.body)
        amount = body.get('amount')

        if not amount:
            return JsonResponse({'error': 'Invalid data'})
        
        amount = int(amount)
        order_id = body.get('order_id')
        order_id = int(order_id)
        
        # address from post
        address = body.get('shipping').get('address')
        street = address.get('street')
        city = address.get('city')
        state = address.get('state')
        zip_code = address.get('zip_code')

        # update or create address
        address, created = Address.objects.update_or_create(
            buyer=request.user,
            defaults={
                'street': street,
                'city': city,
                'state': state,
                'zip_code': zip_code
            }
        )

        order = Order.objects.get(id=order_id)
        shipping, created = Shipping.objects.update_or_create(
            order=order, 
            defaults={
                'shipping_method': 'standard', 
                'estimated_delivery_date': datetime.now() + timedelta(days=7),
                'tracking_number': '1234567890',
                'address': address
            }
        )

        customer = stripe.Customer.create(
            email=request.user.email,
            name=request.user.first_name if request.user.first_name else "N/A",
            address={
                'line1': street,
                'city': city,
                'state': state,
                'postal_code': zip_code,
                'country': 'US',
            },
        )

        # Create a Payment object
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency='usd',
            customer=customer.id,
            description=f"Payment for order {order_id}",
            metadata={
                'integration_check': 'accept_a_payment',
                'order_id': order_id,
                'zip_code': zip_code
            },
        )
        return JsonResponse({'client_secret': intent.client_secret})
    return JsonResponse({'error': 'Invalid request'})


def payment_success(request):
    http_referer = request.META.get('HTTP_REFERER')
    if http_referer and 'checkout' in http_referer:
        cart = Cart.objects.filter(user=request.user).delete()
    return render(request, 'store/payment_success.html')


@csrf_exempt
def stripe_webhooks(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    endpoint_secret = settings.STRIPE_WH_SECRET

    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        print(f'Error parsing payload {str(e)}')
        return HttpResponse(status=400)

    # Handle the event
    if event.type == 'payment_intent.succeeded':
        payment_intent = event.data.object # contains a stripe.PaymentIntent

        order = Order.objects.get(id=payment_intent.metadata.order_id)
        order.is_completed = True
        order.save()

        payment = Payment.objects.create(
            order=order,
            payment_method='stripe',
            payment_amount=payment_intent.amount / 100,
            zip_code=payment_intent.metadata.zip_code
        )
    elif event.type == 'payment_method.attached':
        payment_method = event.data.object # contains a stripe.PaymentMethod
        # Then define and call a method to handle the successful attachment of a PaymentMethod.
        # handle_payment_method_attached(payment_method)
    # ... handle other event types
        print('Payment method attached', payment_method)
    else:
        print('Unhandled event type {}'.format(event.type))

    return HttpResponse(status=200)


# Create a signin view
@redirect_authenticated_user
def signin(request):
    context = {
        'total_items': cart_total_items(request)
    }
    if request.method == 'POST':
        # Get the email and password from the request
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Authenticate the user
        user = authenticate(request, email=email, password=password)
        
        # If the user is authenticated
        if user is not None:
            # Log the user in
            login(request, user)
            
            return redirect(request.GET.get('next', 'store:index')) # Redirect to the next page if it exists
        else:
            # Return an 'invalid login' error message
            return render(request, 'store/login.html', {'error_message': 'Invalid login'})
    
    return render(request, 'store/login.html', context)


@redirect_authenticated_user
def seller_signin(request):
    context = {
        'total_items': cart_total_items(request)
    }
    if request.method == 'POST':
        # Get the email and password from the request
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Authenticate the user
        user = authenticate(request, email=email, password=password)
        
        # If the user is authenticated
        if user is not None and user.is_seller:
            # Log the user in
            login(request, user)
            
            return redirect(request.GET.get('next', 'store:seller_index'))
        else:
            # Return an 'invalid login' error message
            return render(request, 'store/seller_login.html', {'error_message': 'Invalid login'})
    
    return render(request, 'store/seller_login.html', context)


# create signup view
@redirect_authenticated_user
def signup(request):
    if request.method == 'POST':
        # Get the email and password from the request
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        address = request.POST.get('address')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Check if the passwords match
        if password1 != password2:
            # Return an 'passwords do not match' error message
            return render(request, 'store/signup.html', {'error_message': 'Passwords do not match'})
        
        # Create a user
        user = CustomUser.objects.create_user(email=email, password=password1, first_name=first_name, last_name=last_name, address=address)
        
        # Authenticate the user
        user = authenticate(request, email=email, password=password1)
        
        # If the user is authenticated
        if user is not None:
            # Log the user in
            login(request, user)
            
            return redirect('store:index')
        else:
            # Return an 'invalid login' error message
            return render(request, 'store/login.html', {'error_message': 'Invalid login'})
    
    return render(request, 'store/signup.html')


@redirect_authenticated_user
def seller_signup(request):
    if request.method == 'POST':
        # Get the email and password from the request
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        address = request.POST.get('address')
        business = request.POST.get('business')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Check if the passwords match
        if password1 != password2:
            # Return an 'passwords do not match' error message
            return render(request, 'store/seller_signup.html', {'error_message': 'Passwords do not match'})
        
        # Create a user
        user = CustomUser.objects.create_user(email=email, password=password1, first_name=first_name, last_name=last_name, address=address, is_seller=True)
        
        # Authenticate the user
        user = authenticate(request, email=email, password=password1)
        
        # If the user is authenticated
        if user is not None:
            seller = Seller.objects.create(user=user, business_name=business, rating=1)
            # Log the user in
            login(request, user)
            
            return redirect('store:seller_index')
        else:
            # Return an 'invalid login' error message
            return render(request, 'store/seller_login.html', {'error_message': 'Invalid login'})
    
    return render(request, 'store/seller_signup.html')


def upgrade_to_seller(request):
    if request.method == 'POST':
        # Get the email and password from the request
        business = request.POST.get('business')
        user = request.user
        user.is_seller = True
        user.save()
        seller = Seller.objects.create(user=user, business_name=business, rating=1)
        
        return redirect('store:seller_index')
    
    return render(request, 'store/upgrade_to_seller.html')


# Create a signout view
@login_required(login_url='store:login')
def signout(request):
    logout(request)
    
    return redirect('store:index')