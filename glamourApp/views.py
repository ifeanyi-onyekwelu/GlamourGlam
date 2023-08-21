import random
import re
import os
from dotenv import load_dotenv
from random import sample
from django.template.loader import render_to_string
from django.db.models import Sum
from django.conf import settings
from django.contrib import messages
from users.models import CustomUser
from django.http import JsonResponse, Http404, HttpResponsePermanentRedirect
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import login, logout, authenticate, get_user_model
from .utils import get_products_with_images, send_message, create_notification
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.generic import TemplateView, DetailView, ListView, CreateView, View, UpdateView
from .models import Product, ShippingAddress, Order, OrderItem, Category, ProductImage, Cart, CartItem, Notification, SubCategory, DiscountCode
from django.core.mail import send_mail
from django.utils.decorators import method_decorator
from .decorators import prevent_authenticated_access

load_dotenv()

# Create your views here.
class HomePageView(TemplateView):
    def get(self, request, *args, **kwargs):
        try:
            # Fetch all products ordered by date_created (latest first)
            products = Product.objects.order_by('-date_created')[:6]
            # Fetch hot trends, bestsellers, and features using random sampling
            hot_trends = sample(list(products), 3)
            best_sellers = sample(list(products), 3)
            features = sample(list(products), 3)
            # Get products with their latest images for each category

            products_with_images = get_products_with_images(products)
            hot_trend = get_products_with_images(hot_trends)
            best_seller = get_products_with_images(best_sellers)
            feature = get_products_with_images(features)
            APP_NAME = os.getenv('APP_NAME')

            cart = None
            total_items = 0

            # Calculate total items in cart for both authenticated users and guest use

            if request.user.is_authenticated:
                cart, created = Cart.objects.get_or_create(user=request.user)
                total_items = CartItem.objects.filter(cart=cart).aggregate(Sum('quantity'))['quantity__sum']
            else:
                cart = request.session.get('cart', {})
                total_items = sum(item['quantity'] for item in cart.values())

            context = {
                'products': products_with_images,
                'hot_trends': hot_trend,
                'best_sellers': best_seller,
                'features': feature,
                'total_items_in_cart': total_items,
                'APP_NAME': APP_NAME.title()
            }
            return render(request, 'index.html', context)
        except Exception as e:
            print(e)
            return render(request, 'index.html')

class AboutPageView(TemplateView):
    template_name = 'about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        APP_NAME = os.getenv('APP_NAME')

        cart = None
        total_items = 0
        if self.request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=self.request.user)
            total_items = CartItem.objects.filter(cart=cart).aggregate(Sum('quantity'))['quantity__sum']
        
        context['APP_NAME'] = APP_NAME
        context['total_items_in_cart'] = total_items
        return context

class PrivacyPolicyPageView(TemplateView):
    template_name = 'privacy_policy.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        APP_NAME = os.getenv('APP_NAME')

        cart = None
        total_items = 0
        if self.request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=self.request.user)
            total_items = CartItem.objects.filter(cart=cart).aggregate(Sum('quantity'))['quantity__sum']
        
        context['APP_NAME'] = APP_NAME
        context['total_items_in_cart'] = total_items
        return context

class TermsOfServicePageView(TemplateView):
    template_name = 'terms_of_service.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        APP_NAME = os.getenv('APP_NAME')

        cart = None
        total_items = 0
        if self.request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=self.request.user)
            total_items = CartItem.objects.filter(cart=cart).aggregate(Sum('quantity'))['quantity__sum']
        
        context['APP_NAME'] = APP_NAME
        context['total_items_in_cart'] = total_items
        return context

class WomenPageView(ListView):
    model = Product
    template_name = 'women.html'
    context_object_name = 'products'
    paginate_by = 9

    def get_queryset(self):
        category = get_object_or_404(Category, name='Women')
        return Product.objects.filter(category=category).order_by('id')  

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_products = self.get_queryset()
        APP_NAME = os.getenv('APP_NAME')
        
        cart = None
        total_items = 0
        if self.request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=self.request.user)
            total_items = CartItem.objects.filter(cart=cart).aggregate(Sum('quantity'))['quantity__sum']

        # Paginate the products
        paginator = Paginator(all_products, self.paginate_by)
        page = self.request.GET.get('page')

        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            products = paginator.page(1)
        except EmptyPage:
            products = paginator.page(paginator.num_pages)

        context['all_products'] = get_products_with_images(products)
        
        women_and_unisex_products = Product.objects.filter(category__name__in=['Women', 'Unisex'])
        sub_categories = SubCategory.objects.filter(product__in=women_and_unisex_products).distinct()
        context['sub_categories'] = sub_categories
        context['total_items_in_cart'] = total_items
        context['APP_NAME'] = APP_NAME.title()
        return context

class MenPageView(ListView):
    model = Product
    template_name = 'men.html'
    context_object_name = 'products'
    paginate_by = 9

    def get_queryset(self):
        category = get_object_or_404(Category, name='Men')
        return Product.objects.filter(category=category).order_by('id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_products = self.get_queryset()
        APP_NAME = os.getenv('APP_NAME')

        cart = None
        total_items = 0
        if self.request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=self.request.user)
            total_items = CartItem.objects.filter(cart=cart).aggregate(Sum('quantity'))['quantity__sum']

        # Paginate the products
        paginator = Paginator(all_products, self.paginate_by)
        page = self.request.GET.get('page')

        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            products = paginator.page(1)
        except EmptyPage:
            products = paginator.page(paginator.num_pages)

        context['all_products'] = get_products_with_images(products)

        men_and_unisex_products = Product.objects.filter(category__name__in=['Men', 'Unisex'])
        sub_categories = SubCategory.objects.filter(product__in=men_and_unisex_products).distinct()
        context['sub_categories'] = sub_categories
        context['total_items_in_cart'] = total_items
        context['APP_NAME'] = APP_NAME.title()
        return context

class KidsPageView(ListView):
    model = Product
    template_name = 'kids.html'
    context_object_name = 'products'
    paginate_by = 9

    def get_queryset(self):
        category = get_object_or_404(Category, name='Kids')
        return Product.objects.filter(category=category).order_by('id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_products = self.get_queryset()
        APP_NAME = os.getenv('APP_NAME')

        cart = None
        total_items = 0
        if self.request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=self.request.user)
            total_items = CartItem.objects.filter(cart=cart).aggregate(Sum('quantity'))['quantity__sum']


        # Paginate the products
        paginator = Paginator(all_products, self.paginate_by)
        page = self.request.GET.get('page')

        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            products = paginator.page(1)
        except EmptyPage:
            products = paginator.page(paginator.num_pages)

        context['all_products'] = get_products_with_images(products)

        kids_and_unisex_products = Product.objects.filter(category__name__in=['Kids'])
        sub_categories = SubCategory.objects.filter(product__in=kids_and_unisex_products).distinct()
        context['sub_categories'] = sub_categories
        context['total_items_in_cart'] = total_items
        context['APP_NAME'] = APP_NAME.title()
        return context

class AccessoriesPageView(ListView):
    model = Product
    template_name = 'accessories.html'
    context_object_name = 'products'
    paginate_by = 9

    def get_queryset(self):
        category = get_object_or_404(Category, name='Accessories')
        return Product.objects.filter(category=category).order_by('id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_products = self.get_queryset()
        APP_NAME = os.getenv('APP_NAME')

        cart = None
        total_items = 0
        if self.request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=self.request.user)
            total_items = CartItem.objects.filter(cart=cart).aggregate(Sum('quantity'))['quantity__sum']

        # Paginate the products
        paginator = Paginator(all_products, self.paginate_by)
        page = self.request.GET.get('page')

        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            products = paginator.page(1)
        except EmptyPage:
            products = paginator.page(paginator.num_pages)

        context['all_products'] = get_products_with_images(products)

        accessories_and_unisex_products = Product.objects.filter(category__name__in=['Accessories'])
        sub_categories = SubCategory.objects.filter(product__in=accessories_and_unisex_products).distinct()
        context['sub_categories'] = sub_categories
        context['total_items_in_cart'] = total_items
        context['APP_NAME'] = APP_NAME.title()
        return context

class ShopPageView(TemplateView):
    def get(self, request, *args, **kwargs):
        all_products = Product.objects.all().order_by('id')
        paginator = Paginator(all_products, 9)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        APP_NAME = os.getenv('APP_NAME')

        cart = None
        total_items = 0

        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
            total_items = CartItem.objects.filter(cart=cart).aggregate(Sum('quantity'))['quantity__sum']


        products_with_images = get_products_with_images(page_obj)
        categories = Category.objects.prefetch_related('subcategories').all()
        
        context = {
            'products': products_with_images,
            'page_obj': page_obj,
            'total_items_in_cart': total_items,
            'categories': categories,
            'APP_NAME': APP_NAME,
        }
        return render(request, 'shop.html', context)

class ContactPageView(TemplateView):
    def get(self, request, *args, **kwargs):
        cart = None
        total_items = 0
        APP_NAME = os.getenv('APP_NAME')

        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
            total_items = CartItem.objects.filter(cart=cart).aggregate(Sum('quantity'))['quantity__sum']

        context = {
            'total_items_in_cart': total_items,
            'APP_NAME': APP_NAME,
        }
        return render(request, 'contact.html', context)

class ProductDetailPageView(DetailView):
    model = Product
    context_object_name = 'product'
    template_name = 'product-details.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        APP_NAME = os.getenv('APP_NAME')
        try:
            product_image = ProductImage.objects.filter(product=self.object)
        except ProductImage.DoesNotExist:
            product_image = None
        
        original_price = self.object.price
        price_with_increase = float(original_price) * 1.25

        cart = None
        total_items = 0
        if self.request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=self.request.user)
            total_items = CartItem.objects.filter(cart=cart).aggregate(Sum('quantity'))['quantity__sum']

        context['price_with_increase'] = price_with_increase
        context['product_image'] = product_image
        context['total_items_in_cart'] = total_items

        # Get four products in the same category
        related_products = Product.objects.filter(category=self.object.category)[:4]
        context['related_products'] = related_products
        context['APP_NAME'] = APP_NAME.title()
        return context

class ShopCartPageView(TemplateView):
    def get(self, request, *args, **kwargs):
        user = request.user
        total_amount = 0
        total_items = 0
        cart_items = None
        cart = None
        shipping_fee = 3500.00
        total_amount_shipping = 0
        APP_NAME = os.getenv('APP_NAME')

        # If the user is authenticated, handle their cart
        if user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=user)
            cart_items = cart.items.all()

            for cart_item in cart_items:
                cart_item.first_image = cart_item.product.productimage_set.first()
                cart_item.subtotal = cart_item.quantity * cart_item.product.price

            total_items = CartItem.objects.filter(cart=cart).aggregate(Sum('quantity'))['quantity__sum']
            total_amount = sum(cart_item.subtotal for cart_item in cart_items)
            total_amount_shipping = int(total_amount) + shipping_fee

        if not cart_items:
            shipping_fee = 0.00
            total_amount = 0.00
            total_amount_shipping = 0.00
        # else:
        #     # For guest users, retrieve the cart from the session
        #     cart = request.session.get('cart', {})
        #     cart_items = []
        #     total_items = 0
        #     total_amount = 0

        #     for item_id, item_info in cart.items():
        #         product_id = item_id
        #         quantity = item_info['quantity']
        #         product = get_object_or_404(Product, id=product_id)

        #         # For guest users, get the first image URL related to the product
        #         try:
        #             product_image = ProductImage.objects.filter(product_id=product_id).first()
        #             product.first_image = product_image.image.url if product_image else None
        #         except ProductImage.DoesNotExist:
        #             # Handle the case when there is no image associated with the product
        #             product.first_image = None

        #         subtotal = product.price * quantity
        #         total_items += quantity
        #         total_amount += subtotal
        #         total_amount_shipping = int(total_amount) + shipping_fee

        #         cart_item = {
        #             'product': product,
        #             'quantity': quantity,
        #             'subtotal': subtotal,
        #         }
        #         cart_items.append(cart_item)

        context = {
            'total_items_in_cart': total_items,
            'cart_items': cart_items, 
            'cart': cart,
            'total_amount': total_amount,
            'shipping_fee': shipping_fee,
            'total_amount_shipping': total_amount_shipping,
            'APP_NAME': APP_NAME,
        }

        return render(request, 'shop-cart.html', context)
    
    def post(self, request, *args, **kwargs):
        user = request.user
        total_amount = 0
        total_items = 0
        cart_items = None
        cart = None
        shipping_fee = 3500.00
        total_amount_shipping = 0
        APP_NAME = os.getenv('APP_NAME')

        # If the user is authenticated, handle their cart
        if user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=user)
            cart_items = cart.items.all()

            for cart_item in cart_items:
                cart_item.first_image = cart_item.product.productimage_set.first()
                cart_item.subtotal = cart_item.quantity * cart_item.product.price

            total_items = CartItem.objects.filter(cart=cart).aggregate(Sum('quantity'))['quantity__sum']
            total_amount = float(sum(cart_item.subtotal for cart_item in cart_items))
            total_amount_shipping = int(total_amount) + shipping_fee

        discount_code = request.POST.get('code')
        try:
            discount = DiscountCode.objects.get(code=discount_code)
        except DiscountCode.DoesNotExist:
            discount = None
            return JsonResponse({'message': "Invalid code provided"})

        if discount:
            request.session['discount_code'] = discount_code
            discount_amount = (discount.percentage / 100) * total_amount
            total_amount -= discount_amount
            total_amount_shipping = int(total_amount) + shipping_fee

        context = {
            'total_items_in_cart': total_items,
            'cart_items': cart_items,
            'cart': cart,
            'total_amount': total_amount,
            'shipping_fee': shipping_fee,
            'total_amount_shipping': total_amount_shipping,
            'APP_NAME': APP_NAME
        }

        return render(request, 'shop-cart.html', context)

class CheckoutPageView(LoginRequiredMixin, CreateView):
    def get(self, request, *args, **kwargs):
        cart, created = Cart.objects.get_or_create(user=request.user)
        total_items = CartItem.objects.filter(cart=cart).aggregate(Sum('quantity'))['quantity__sum']
        cart_items = cart.items.all()
        shipping_fee = 3500.00
        APP_NAME = os.getenv('APP_NAME')

        for cart_item in cart_items:
            cart_item.first_image = cart_item.product.productimage_set.first()

            cart_item.subtotal = cart_item.quantity * cart_item.product.price
        
        discount_code = request.session.get('discount_code', None)
        try:
            discount = DiscountCode.objects.get(code=discount_code)
        except DiscountCode.DoesNotExist:
            discount = None

        total_amount = float(sum(cart_item.subtotal for cart_item in cart_items))
        total_amount_shipping = int(total_amount) + shipping_fee

        if discount:
            discount_amount = (discount.percentage / 100) * total_amount
            total_amount -= discount_amount
            total_amount_shipping = int(total_amount) + shipping_fee

        context = {
            'total_items_in_cart': total_items,
            'cart_items': cart_items, 
            'cart': cart,
            'total_amount': total_amount,
            'shipping_fee': shipping_fee,
            'total_amount_shipping': total_amount_shipping,
            'APP_NAME': APP_NAME,
        }

        return render(request, 'checkout.html', context)
    
    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            shipping_address = ShippingAddress.objects.create(
                user=request.user,
                address=request.POST.get('address'),
                phone=request.POST.get('phone'),
                country=request.POST.get('country'),
                city=request.POST.get('city'),
                state=request.POST.get('state'),
                zipcode=request.POST.get('zipcode'),
            )

            cart = Cart.objects.get(user=request.user)
            cart_items = cart.items.all()

            total_price = sum(item.product.price * item.quantity for item in cart_items)

            order = Order.objects.create(
                user=request.user,
                shipping_address=shipping_address,
                total_price=total_price
            )

            for cart_item in cart_items:
                order_items = OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )
            
                order.items.add(order_items)

            cart.delete()
            cart.save()
            
            send_order_email(order)
            return redirect('app:order_complete', order_id=order.id)
        else:
            return render(request, 'checkout.html')

class FAQPageView(TemplateView):
    def get(self, request, *args, **kwargs):
        cart = None
        total_items = 0
        APP_NAME = os.getenv('APP_NAME')

        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
            total_items = CartItem.objects.filter(cart=cart).aggregate(Sum('quantity'))['quantity__sum']

        context = {
            'APP_NAME': APP_NAME,
            'total_items_in_cart': total_items,
        }
        return render(request, 'faqs.html', context)

class AccountPageView(LoginRequiredMixin, UpdateView):
    def get(self, request, *args, **kwargs):
        return render(request, 'account.html')

    def post(self, request, *args, **kwargs):
        return render(request, 'account.html')

class SecurityAccountPageView(LoginRequiredMixin, UpdateView):
    def get(self, request, *args, **kwargs):
        return render(request, 'security-account.html')

    def post(self, request, *args, **kwargs):
        return render(request, 'security-account.html')

@method_decorator(prevent_authenticated_access('app:home_page'), name='dispatch')
class LoginPageView(TemplateView):
    def get(self, request, *args, **kwargs):
        return render(request, 'login.html', {'APP_NAME': os.getenv('APP_NAME')})

@method_decorator(prevent_authenticated_access('app:home_page'), name='dispatch')
class RegisterPageView(TemplateView):
    def get(self, request, *args, **kwargs):
        return render(request, 'register.html', {'APP_NAME': os.getenv('APP_NAME')})

class OrderHistoryPage(LoginRequiredMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        user = request.user
        orders = Order.objects.filter(user=user).order_by('-created_at')
        cart = None
        total_items = 0
        APP_NAME = os.getenv('APP_NAME')

        cart, created = Cart.objects.get_or_create(user=request.user)
        total_items = CartItem.objects.filter(cart=cart).aggregate(Sum('quantity'))['quantity__sum']

        order_data = []
        for order in orders:
            order_items = OrderItem.objects.filter(order=order)
            order_item_data = []
            
            for order_item in order_items:
                first_image = order_item.product.productimage_set.first() if order_item.product.productimage_set.exists() else None
                order_item_data.append({
                    'order_item': order_item,
                    'first_image': first_image
                })

            order_data.append({
                'order': order,
                'order_items': order_item_data,
            })

        context = {
            'order_data': order_data,
            'APP_NAME': APP_NAME,
            'total_items_in_cart': total_items,
        }
        return render(request, 'order_history.html', context)

class OrderDetailsPage(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'order_details.html'
    context_object_name = 'order'

    def get_object(self, queryset=None):
        return get_object_or_404(Order, id=self.kwargs['order_id'])
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = None
        total_items = 0
        APP_NAME = os.getenv('APP_NAME')

        cart, created = Cart.objects.get_or_create(user=self.request.user)
        total_items = CartItem.objects.filter(cart=cart).aggregate(Sum('quantity'))['quantity__sum']

        context['total_items_in_cart'] = total_items
        context['APP_NAME'] = APP_NAME
        return context

class OrderCompletePageView(LoginRequiredMixin, DetailView):
     def get(self, request, *args, **kwargs):
        order = get_object_or_404(Order, id=kwargs['order_id'])
        cart, created = Cart.objects.get_or_create(user=request.user)
        total_items = CartItem.objects.filter(cart=cart).aggregate(Sum('quantity'))['quantity__sum']
        order_items = order.items.all()
        shipping_fee = 3500.00
        APP_NAME = os.getenv('APP_NAME')

        for order_item in order_items:
            order_item.first_image = order_item.product.productimage_set.first()
            order_item.subtotal = order_item.quantity * order_item.product.price
        
        discount_code = request.session.get('discount_code', None)
        try:
            discount = DiscountCode.objects.get(code=discount_code)
            discount_percentage = discount.percentage
        except DiscountCode.DoesNotExist:
            discount = None

        total_amount = float(sum(order_item.subtotal for order_item in order_items))
        total_amount_shipping = int(total_amount) + shipping_fee

        if discount:
            discount_amount = (discount.percentage / 100) * total_amount
            total_amount -= discount_amount
            total_amount_shipping = int(total_amount) + shipping_fee

        context = {
            'total_items_in_cart': total_items,
            'order_items': order_items, 
            'order': order,
            'total_amount': total_amount,
            'shipping_fee': shipping_fee,
            'total_amount_shipping': total_amount_shipping,
            'APP_NAME': APP_NAME,
        }

        return render(request, 'order_complete.html', context)

# Function based views
def handleUserRegistration(request):
    try:
        firstName = request.POST.get('firstName')
        lastName = request.POST.get('lastName')
        email = request.POST.get('email')
        password = request.POST.get('password')
        cmfpassword = request.POST.get('cmfpassword')
        username = str(firstName) + str(lastName)
        hased_password = make_password(password)

        if CustomUser.objects.filter(username=username).exists() and not CustomUser.objects.filter(email=email).exists():
            new_user = CustomUser.objects.create(username=username + str(password), first_name=firstName, last_name=lastName, email=email, password=hased_password)
        
        if CustomUser.objects.filter(email=email).exists():
            return JsonResponse({'success': False, 'message': 'Email already exists'})

        if password != cmfpassword:
            return JsonResponse({'success': False, 'message': 'Passwords do not match!'})
        
        new_user = CustomUser.objects.create(username=username, first_name=firstName, last_name=lastName, email=email, password=hased_password)
        create_notification(title="User joined", notification="A user just created an account", notification_type="REGISTRATION")

        # HANDLE SEND EMAIL AFTER REGISTRATION
        APP_NAME = os.getenv('APP_NAME')
        subject = f"🎉 Welcome to {APP_NAME}! 🛍️"
        APP_URL = os.getenv('APP_URL')
        context = {
            'APP_NAME': APP_NAME,
            'APP_URL': APP_URL
        }
        body = render_to_string('email/welcome.html', context)
        send_message(subject, '', body, settings.DEFAULT_EMAIL, email)
        new_user.save()
        login(request, new_user)
        
        return JsonResponse({'success': False, 'message': "Registration successful"})

    except Exception as e:
        return JsonResponse({'message': str(e)})

def handleUserLogin(request):
    try:
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = get_object_or_404(CustomUser, email=email)
        if user is not None:
            if user.check_password(password):
                login(request, user)
                return JsonResponse({'success': True, 'message': 'Login successful'})
            else:
                return JsonResponse({'success': False, 'message': 'Invalid username or password'})
        else:
            return JsonResponse({'success': False, 'message': 'Account not found'})
    except Http404:
        return JsonResponse({'success': False, 'message': 'Account not found!'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': 'An error occurred'})

@login_required
def handleUserLogout(request):
    logout(request)
    return redirect(reverse('app:home_page'))

@login_required
def handleAddToCart(request, product_id, color_selected, size_selected, quantity_selected):
    product = get_object_or_404(Product, id=product_id)
    user = request.user

    product_price = product.price

    # If the user is authenticated, handle their cart
    cart, created = Cart.objects.get_or_create(user=user)

    try:
        cart_item = CartItem.objects.get(cart=cart, product=product)
        cart_item.quantity += int(quantity_selected)
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(cart=cart, product=product, color=color_selected, size=size_selected, quantity=int(quantity_selected), price=product_price)

    return redirect(reverse('app:cart_page'))

@login_required
def handleRemoveCartItem(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id)

    if cart_item.cart.user == request.user:
        cart_item.delete()

    # Retrieve the remaining cart items associated with the cart
    cart_items = CartItem.objects.filter(cart=cart_item.cart)
    
    total_amount = 0
    for item in cart_items:
        total_amount += item.price
    
    # Return the updated total amount in the JSON response
    return JsonResponse({'total_amount': total_amount})

def handleContactForm(request):
    name = request.POST.get('name')
    email = request.POST.get('email')
    message = request.POST.get('message')

    subject = ""
    APP_NAME = "GlamourGlam"
    context = {
        'APP_NAME':APP_NAME,
        'name': name,
        'email': email,
        'message': message
    }
    body = render(request, '', context)
    send_message(subject, body, email, settings.DEFAULT_EMAIL)
    return redirect(reverse('app:contact_page'))

def handleSearchForm(request):
    search_query = request.GET.get('search_query')
    products = Product.objects.all()

    cart = None
    total_items = 0

    if search_query:
        print(search_query)
        products = products.filter(name__icontains=search_query) | products.filter(category__name__icontains=search_query)

    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        total_items = CartItem.objects.filter(cart=cart).aggregate(Sum('quantity'))['quantity__sum']
    
    all_products = get_products_with_images(products)
    context = {
        'search_query': search_query, 
        'products': all_products,
        'total_items_in_cart': total_items
    }
    return render(request, 'search_results.html', context)

@login_required
def handleUpdateCart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = request.POST.get('quantity')

        try:
            # If the user is authenticated, update the cart in the database
            if request.user.is_authenticated:
                cart, created = Cart.objects.get_or_create(user=request.user)
                cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
                new_quantity = int(quantity)
                if new_quantity >= 1:
                    cart_item.quantity = new_quantity
                    cart_item.save()
                    return JsonResponse({'success': True, 'new_quantity': new_quantity})
                else:
                    return JsonResponse({'success': False, 'message': 'Quantity must be at least 1'})
            else:
                # For guest users, update the cart in the session
                cart = request.session.get('cart', {})
                cart_item = cart.get(str(product_id))
                if cart_item:
                    new_quantity = int(quantity)
                    if new_quantity >= 1:
                        cart_item['quantity'] = new_quantity
                        request.session['cart'] = cart
                        return JsonResponse({'success': True, 'new_quantity': new_quantity})
                    else:
                        return JsonResponse({'success': False, 'message': 'Quantity must be at least 1'})
                else:
                    return JsonResponse({'success': False, 'message': 'Cart item does not exist'})
        except CartItem.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Cart item does not exist'})

    return JsonResponse({'success': False, 'message': 'Invalid request'})

def handleSubscribeToNewsLetter(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        
        # HANDLE SEND EMAIL AFTER REGISTRATION
        subject = "💌 Thanks for Joining Our Newsletter! 🎉"
        APP_NAME = os.getenv('APP_NAME')
        APP_URL = os.getenv('APP_URL')
        context = {
            'APP_NAME': APP_NAME,
            'APP_URL': APP_URL
        }
        body = render_to_string('email/newsletter.html', context)
        send_message(subject, '', body, settings.DEFAULT_EMAIL, email)
        return JsonResponse({'success': True, 'message': 'Subscribe to newsletter'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@login_required
def handleUpdateSecurityDetail(request):
    try:
        if request.method == 'POST':
            old_password = request.POST.get('oldPassword')
            new_password = request.POST.get('newPassword')
            hashed_password = make_password(new_password)

            user = CustomUser.objects.get(id=request.user.id)
            
            if not user.check_password(old_password):
                return JsonResponse({'success': False, 'message': 'Old password is incorrect!'})

            user.password = hashed_password
            user.save()
            return JsonResponse({'success': True, 'message': "Password updated successfully"})

        return JsonResponse({'success': False, 'message': "Invalid request"})
    except CustomUser.DoesNotExist:
        return None
    except Exception as e:
        print("An error occurred: %s" % str(e))

@login_required
def handleUpdateProfileDetail(request):
    try:
        if request.method == 'POST':
            first_name = request.POST.get('firstName')
            last_name = request.POST.get('lastName')
            email = request.POST.get('email')
            username = request.POST.get('username')

            user = CustomUser.objects.get(id=request.user.id)
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.username = username
            user.save()
            return JsonResponse({'success': True, 'message': "Profile updated successfully"})
        return JsonResponse({'success': False, 'message': "Invalid request"})
    except CustomUser.DoesNotExist:
        return None
    except Exception as e:
        print("An error occurred: %s" % str(e))


def custom_error_404(request, exception):
    APP_NAME = os.getenv('APP_NAME')
    context = {
        'APP_NAME': APP_NAME,
    }
    return render(request, '404.html', context, status=404)

def custom_error_500(request):
    APP_NAME = os.getenv('APP_NAME')
    context = {
        'APP_NAME': APP_NAME,
    }
    return render(request, '500.html', context, status=500)