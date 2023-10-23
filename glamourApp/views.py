import random
import re
import time
import string
import os
import requests
from dotenv import load_dotenv
from random import sample
from django.template.loader import render_to_string
from django.db.models import Sum, F, ExpressionWrapper, FloatField
from django.conf import settings
from django.utils.crypto import get_random_string
from django.contrib import messages
from users.models import CustomUser
from django.http import JsonResponse, Http404, HttpResponsePermanentRedirect
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth import get_user_model
from .utils import (
    get_products_with_images,
    send_message,
    create_notification,
    send_order_email,
    send_admin_order_email,
    calculate_discounted_total,
    calculate_order_details
)
from django.contrib.auth.models import Group
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.generic import (
    TemplateView,
    DetailView,
    ListView,
    CreateView,
    View,
    UpdateView,
)
from .models import *
from django.core.mail import send_mail
from django.utils.decorators import method_decorator
from .decorators import prevent_authenticated_access, cart_not_empty
from .paystack import Paystack
import paystack

load_dotenv()

class CategoryPageView(ListView):
    model = Product
    template_name = ""
    context_object_name = "products"
    paginate_by = 12
    category_name = "" 

    def get_queryset(self):
        category = get_object_or_404(Category, name=self.category_name)

        return Product.objects.filter(category=category).order_by("id")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_products = self.get_queryset()
        APP_NAME = os.getenv("APP_NAME")

        cart = None
        total_items = 0

        if self.request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=self.request.user)
            total_items = CartItem.objects.filter(cart=cart).aggregate(Sum("quantity"))[
                "quantity__sum"
            ]

            user_wishlist_items = WishListItem.objects.filter(user=self.request.user)
            wishlist_product_ids = user_wishlist_items.values_list("product__id", flat=True)

            product_wishlist_status = {}

            for product in all_products:
                is_in_wishlist = product.id in wishlist_product_ids
                product_wishlist_status[product.id] = is_in_wishlist
                
        else:
            product_wishlist_status = {product.id: False for product in all_products}

        wishlist_statuses = [product_wishlist_status[product.id] for product in all_products]

        # Paginate the products
        paginator = Paginator(all_products, self.paginate_by)
        page = self.request.GET.get("page")

        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            products = paginator.page(1)
        except EmptyPage:
            products = paginator.page(paginator.num_pages)

        context["all_products"] = get_products_with_images(products)
        products_in_wishlist = list(zip(get_products_with_images(products), wishlist_statuses))

        category_products = Product.objects.filter(
            category__name__in=[self.category_name]
        )
        sub_categories = SubCategory.objects.filter(
            product__in=category_products
        ).distinct()
        
        context["page_obj"] = products
        context["sub_categories"] = sub_categories
        context["products_in_wishlist"] = products_in_wishlist
        context["total_items_in_cart"] = total_items
        context["APP_NAME"] = APP_NAME.title()
        return context

# Create your views here.
class HomePageView(TemplateView):
    def get(self, request, *args, **kwargs):
        try:
            # Fetch all products ordered by date_created (latest first)
            products = Product.objects.order_by("?")
            new_products = Product.objects.order_by("?")[:12]
            # Fetch hot trends, bestsellers, and features using random sampling
            hot_trends = sample(list(products), 3)
            best_sellers = sample(list(products), 3)
            features = sample(list(products), 3)
            # Get products with their latest images for each category

            products_with_images = get_products_with_images(products)
            new_product_with_image = get_products_with_images(new_products)
            hot_trend = get_products_with_images(hot_trends)
            best_seller = get_products_with_images(best_sellers)
            feature = get_products_with_images(features)
            APP_NAME = os.getenv("APP_NAME")

            cart = None
            total_items = 0

            # Calculate total items in cart for both authenticated users and guest use

            if request.user.is_authenticated:
                cart, created = Cart.objects.get_or_create(user=request.user)
                total_items = CartItem.objects.filter(cart=cart).aggregate(
                    Sum("quantity")
                )["quantity__sum"]

                user_wishlist_items = WishListItem.objects.filter(user=request.user)
                wishlist_product_ids = user_wishlist_items.values_list("product__id", flat=True)

                product_wishlist_status = {}

                for entry in new_product_with_image:
                    product = entry['product']
                    is_in_wishlist = product.id in wishlist_product_ids
                    product_wishlist_status[product.id] = is_in_wishlist

            else:
                # Assuming all products are not in the wishlist for non-authenticated users
                product_wishlist_status = {product_info['product'].id: False for product_info in new_product_with_image}
            
            wishlist_statuses = [product_wishlist_status[product_info['product'].id] for product_info in new_product_with_image]
            # Combine products with wishlist statuses into a list of tuples
            products_in_wishlist = list(zip(new_product_with_image, wishlist_statuses)) 
            print(products_in_wishlist)           
            print(wishlist_statuses)
            
            
            context = {
                "products": products_with_images,
                "new_products": new_product_with_image,
                "hot_trends": hot_trend,
                "best_sellers": best_seller,
                "features": feature,
                "total_items_in_cart": total_items,
                "APP_NAME": APP_NAME.title(),
                "products_in_wishlist": products_in_wishlist,
            }
            return render(request, "index.html", context)
        except Exception as e:
            print(e)
            return render(request, "index.html")


class AboutPageView(TemplateView):
    template_name = "about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        APP_NAME = os.getenv("APP_NAME")
        FOUNDER_NAME = os.getenv("FOUNDER_NAME")

        cart = None
        total_items = 0
        if self.request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=self.request.user)
            total_items = CartItem.objects.filter(cart=cart).aggregate(Sum("quantity"))[
                "quantity__sum"
            ]

        context["APP_NAME"] = APP_NAME
        context["FOUNDER_NAME"] = FOUNDER_NAME
        context["total_items_in_cart"] = total_items
        return context


class WomenPageView(CategoryPageView):
    category_name = "Women"
    template_name = "women.html"


class MenPageView(CategoryPageView):
    category_name = "Men"
    template_name = "men.html"


class UnisexPageView(CategoryPageView):
    category_name = "Unisex"
    template_name = "unisex.html"


class KidsPageView(CategoryPageView):
    category_name = "Kids"
    template_name = "kids.html"


class AccessoriesPageView(CategoryPageView):
    category_name = "Accessories"
    template_name = "accessories.html"


class ShopPageView(TemplateView):
    def get(self, request, *args, **kwargs):
        all_products = Product.objects.all().order_by("?")
        paginator = Paginator(all_products, 12)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        APP_NAME = os.getenv("APP_NAME")

        cart = None
        total_items = 0

        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
            total_items = CartItem.objects.filter(cart=cart).aggregate(Sum("quantity"))[
                "quantity__sum"
            ]

            user_wishlist_items = WishListItem.objects.filter(user=self.request.user)
            wishlist_product_ids = user_wishlist_items.values_list("product__id", flat=True)

            product_wishlist_status = {}

            for product in all_products:
                is_in_wishlist = product.id in wishlist_product_ids
                product_wishlist_status[product.id] = is_in_wishlist
                
        else:
            product_wishlist_status = {product.id: False for product in all_products}


        wishlist_statuses = [product_wishlist_status[product.id] for product in all_products]

        products_with_images = get_products_with_images(page_obj)
        categories = Category.objects.prefetch_related("subcategories").all()

        products_in_wishlist = list(zip(products_with_images, wishlist_statuses))

        context = {
            "products": products_with_images,
            "page_obj": page_obj,
            "total_items_in_cart": total_items,
            "categories": categories,
            "products_in_wishlist": products_in_wishlist,
            "APP_NAME": APP_NAME,
        }
        return render(request, "shop.html", context)


class ContactPageView(TemplateView):
    def get(self, request, *args, **kwargs):
        cart = None
        total_items = 0
        APP_NAME = os.getenv("APP_NAME")

        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
            total_items = CartItem.objects.filter(cart=cart).aggregate(Sum("quantity"))[
                "quantity__sum"
            ]

        context = {
            "total_items_in_cart": total_items,
            "APP_NAME": APP_NAME,
        }
        return render(request, "contact.html", context)


class ProductDetailPageView(DetailView):
    model = Product
    context_object_name = "product"
    template_name = "product-details.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        APP_NAME = os.getenv("APP_NAME")
        try:
            product_image = ProductImage.objects.filter(product=self.object)
        except ProductImage.DoesNotExist:
            product_image = None

        cart = None
        total_items = 0

        if self.request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=self.request.user)
            total_items = CartItem.objects.filter(cart=cart).aggregate(Sum("quantity"))[
                "quantity__sum"
            ]

        if self.request.user.is_authenticated:
            product_in_wishlist = WishListItem.objects.filter(user=self.request.user, product=self.object).exists()
        else:
            product_in_wishlist = False

        reviews = Review.objects.filter(product=self.object)

        context["product_image"] = product_image
        context["total_items_in_cart"] = total_items
        context["product_in_wishlist"] = product_in_wishlist

        # Get four products in the same category
        related_products = Product.objects.filter(category=self.object.category)[:4]
        context["related_products"] = related_products
        context["APP_NAME"] = APP_NAME.title()
        context["reviews"] = reviews
        return context


class ShopCartPageView(TemplateView):
    def get(self, request, *args, **kwargs):
        user = request.user
        total_amount = 0
        total_items = 0
        cart_items = None
        cart = None
        total_amount_shipping = 0
        shipping_fee = float(settings.SHIPPING_FEE)
        APP_NAME = os.getenv("APP_NAME")
        
        selected_currency = request.session.get('currency_preference')

        if selected_currency == 'USD':
            shipping_fee = float(settings.SHIPPING_FEE_USD)
        elif selected_currency == 'EUR':
            shipping_fee = float(settings.SHIPPING_FEE_EUR)
    

        # If the user is authenticated, handle their cart
        if user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=user)
            cart_items = cart.items.all()

            for cart_item in cart_items:
                cart_item.first_image = cart_item.product.productimage_set.first()
                cart_item.subtotal = cart_item.subtotal(selected_currency)

            total_items = CartItem.objects.filter(cart=cart).aggregate(Sum("quantity"))[
                "quantity__sum"
            ]
            total_amount = sum(cart_item.subtotal for cart_item in cart_items)
            total_amount_shipping = float(total_amount) + shipping_fee

        if not cart_items:
            shipping_fee = 0.00
            total_amount = 0.00
            total_amount_shipping = 0.00
            shipping_fee = 0.00

        context = {
            "total_items_in_cart": total_items,
            "cart_items": cart_items,
            "cart": cart,
            "total_amount": total_amount,
            "shipping_fee": shipping_fee,
            "total_amount_shipping": total_amount_shipping,
            "APP_NAME": APP_NAME,
        }

        return render(request, "shop-cart.html", context)

    def post(self, request, *args, **kwargs):
        user = request.user
        total_amount = 0
        total_items = 0
        cart_items = None
        cart = None
        shipping_fee = settings.SHIPPING_FEE
        total_amount_shipping = 0
        APP_NAME = os.getenv("APP_NAME")

        # If the user is authenticated, handle their cart
        if user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=user)
            cart_items = cart.items.all()

            for cart_item in cart_items:
                cart_item.first_image = cart_item.product.productimage_set.first()
                cart_item.subtotal = cart_item.quantity * cart_item.product.price

            total_items = CartItem.objects.filter(cart=cart).aggregate(Sum("quantity"))[
                "quantity__sum"
            ]
            total_amount = float(sum(cart_item.subtotal for cart_item in cart_items))
            total_amount_shipping = int(total_amount) + shipping_fee

        discount_code = request.POST.get("code")
        try:
            discount = DiscountCode.objects.get(code=discount_code)
        except DiscountCode.DoesNotExist:
            discount = None

        if discount:
            request.session["discount_code"] = discount_code
            discount_amount = (discount.percentage / 100) * total_amount
            total_amount -= discount_amount
            total_amount_shipping = int(total_amount) + shipping_fee

        context = {
            "total_items_in_cart": total_items,
            "cart_items": cart_items,
            "cart": cart,
            "total_amount": total_amount,
            "shipping_fee": shipping_fee,
            "total_amount_shipping": total_amount_shipping,
            "APP_NAME": APP_NAME,
        }

        return render(request, "shop-cart.html", context)


@method_decorator(cart_not_empty, name="dispatch")
class CheckoutPageView(LoginRequiredMixin, CreateView):
    def get(self, request, *args, **kwargs):
        cart, created = Cart.objects.get_or_create(user=request.user)
        total_items = CartItem.objects.filter(cart=cart).aggregate(Sum("quantity"))[
            "quantity__sum"
        ]
        cart_items = cart.items.all()
        # Default shipping fee (in NGN)
        shipping_fee = float(settings.SHIPPING_FEE)
        selected_currency = request.session.get('currency_preference')

        if selected_currency == 'USD':
            shipping_fee = float(settings.SHIPPING_FEE_USD)
        elif selected_currency == 'EUR':
            shipping_fee = float(settings.SHIPPING_FEE_EUR)

        APP_NAME = os.getenv("APP_NAME")
        PAYSTACK_PUBLIC_KEY = os.getenv("PAYSTACK_PUBLIC_KEY")
        selected_currency = request.session.get('currency_preference')

        for cart_item in cart_items:
            cart_item.first_image = cart_item.product.productimage_set.first()
            cart_item.subtotal = cart_item.subtotal(selected_currency)

        discount_code = request.session.get("discount_code", None)
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
            "total_items_in_cart": total_items,
            "cart_items": cart_items,
            "cart": cart,
            "total_amount": total_amount,
            "shipping_fee": shipping_fee,
            "total_amount_shipping": total_amount_shipping,
            "APP_NAME": APP_NAME,
            "PAYSTACK_PUBLIC_KEY": PAYSTACK_PUBLIC_KEY,
            "user_email": request.user.email,
        }

        return render(request, "checkout.html", context)

    def post(self, request, *args, **kwargs):
        if request.method == "POST":
            try:
                shipping_address = ShippingAddress.objects.create(
                    user=request.user,
                    address=request.POST.get("address"),
                    phone=request.POST.get("phone"),
                    country=request.POST.get("country"),
                    city=request.POST.get("city"),
                    state=request.POST.get("state"),
                    zipcode=request.POST.get("zipcode"),
                )

                shipping_address.save()
                
                # Check if the "same_billing" checkbox is checked
                same_billing = request.POST.get("same_billing_address") == "on"
                print("Same billing: ", same_billing)

                # Create billing address based on the checkbox value
                if same_billing:
                    billing_address = BillingDetails.objects.create(
                        user=request.user,
                        street_address=request.POST.get("address"),
                        apartment_suite=request.POST.get("billing_address_optional"),
                        city=request.POST.get("city"),
                        state_province=request.POST.get("state"),
                        postal_zip_code=request.POST.get("zipcode"),
                        country=request.POST.get("country"),
                    )

                    billing_address.save()
                else:
                    billing_address = BillingDetails.objects.create(
                        user=request.user,
                        street_address=request.POST.get("billing_address"),
                        apartment_suite=request.POST.get("billing_address_optional"),
                        city=request.POST.get("billing_city"),
                        state_province=request.POST.get("billing_state"),
                        postal_zip_code=request.POST.get("billing_zipcode"),
                        country=request.POST.get("billing_country"),
                    )
                    billing_address.save()

                cart = Cart.objects.get(user=request.user)
                cart_items = cart.items.all()

                total_price = sum(item.product.price_ngn * item.quantity for item in cart_items)
                shipping_fee = float(settings.SHIPPING_FEE)
                
                selected_currency = request.session.get('currency_preference')
                if selected_currency == 'USD':
                    shipping_fee = float(settings.SHIPPING_FEE_USD)
                elif selected_currency == 'EUR':
                    shipping_fee = float(settings.SHIPPING_FEE_EUR)

                discount_code = request.session.get("discount_code", None)
                try:
                    discount = DiscountCode.objects.get(code=discount_code)
                except DiscountCode.DoesNotExist:
                    discount = None

                if discount:
                    discount_amount = (discount.percentage / 100) * float(total_price)
                    total_price = float(total_price) - discount_amount
                    total_amount_shipping = int(total_price) + shipping_fee
                    discount.is_used = True
                    discount.save()
                else:
                    total_amount_shipping = int(total_price) + shipping_fee

                # Verify the payment
                reference = request.POST.get("paystack_reference")
                print(reference)
                if reference:
                    # Verify the payment using the Paystack class or method you've implemented
                    paystack = Paystack()
                    status, result = paystack.verify_payment(reference)
                    print(status)
                    print(result)

                    if status:
                        # Check if result is a string (i.e., an error message)
                        if isinstance(result, str):
                            return JsonResponse({"success": False, "message": f"Paystack API Error: {result}"})

                        # Payment was successful; continue with order creation
                        payment = Payment.objects.create(
                            user=request.user,
                            amount=total_amount_shipping,  # Update with the correct amount
                            ref=reference
                        )
                        payment.save()
                        result['amount'] = int(result['amount'] / 100)

                        # Check if the 'amount' key is present in the result dictionary
                        if 'amount' in result and isinstance(result['amount'], int):
                            result_amount = float(result['amount'])

                            if result_amount == payment.amount:
                                # Mark the payment as verified in your database
                                payment.verified = True
                                payment.save()

                                order = Order.objects.create(
                                    user=request.user,
                                    shipping_address=shipping_address,
                                    total_price=total_amount_shipping,
                                    billing_details=billing_address
                                )
                                order.payment_status = 'Paid'
                                order.save()

                                for cart_item in cart_items:
                                    order_items = OrderItem.objects.create(
                                        order=order,
                                        product=cart_item.product,
                                        quantity=cart_item.quantity,
                                        price=cart_item.product.price_ngn,
                                        size=cart_item.size,
                                        color=cart_item.color,
                                    )

                                    order.items.add(order_items)
                                cart.delete()
                                cart.save()

                                send_order_email(request, order, selected_currency)

                                send_admin_order_email(request, order, selected_currency)
                                return JsonResponse({"success": True, 'order_id': order.id})
                            else:
                                return JsonResponse({"success": False, "message": "Invalid payment amount"})
                        else:
                            return JsonResponse({"success": False, "message": "Unexpected response format from Paystack"})
                    else:
                        return JsonResponse({"success": False, "message": result['message']})
                else:
                    return JsonResponse({"success": False, "message": "Missing reference parameter"})

            except Exception as e:
                return JsonResponse({"success": False, "message": str(e)})

        return JsonResponse({"success": False})


class AccountPageView(LoginRequiredMixin, UpdateView):
    def get(self, request, *args, **kwargs):
        
        cart, created = Cart.objects.get_or_create(user=request.user)
        total_items = CartItem.objects.filter(cart=cart).aggregate(Sum("quantity"))[
            "quantity__sum"
        ]

        context = {
            "total_items_in_cart": total_items,
            "APP_NAME": os.getenv("APP_NAME"),
        }
        return render(request, "account.html", context)

    def post(self, request, *args, **kwargs):
        return render(request, "account.html")


class SecurityAccountPageView(LoginRequiredMixin, UpdateView):
    def get(self, request, *args, **kwargs):

        cart, created = Cart.objects.get_or_create(user=request.user)
        total_items = CartItem.objects.filter(cart=cart).aggregate(Sum("quantity"))[
            "quantity__sum"
        ]

        context = {
            "total_items_in_cart": total_items,
            "APP_NAME": os.getenv("APP_NAME"),
        }

        return render(request, "security-account.html", context)


@method_decorator(prevent_authenticated_access("app:home_page"), name="dispatch")
class LoginPageView(TemplateView):
    def get(self, request, *args, **kwargs):
        return render(request, "login.html", {"APP_NAME": os.getenv("APP_NAME")})


@method_decorator(prevent_authenticated_access("app:home_page"), name="dispatch")
class RegisterPageView(TemplateView):
    def get(self, request, *args, **kwargs):
        return render(request, "register.html", {"APP_NAME": os.getenv("APP_NAME")})


@method_decorator(prevent_authenticated_access("app:home_page"), name="dispatch")
class ForgotPasswordPage(TemplateView):
    template_name = "forgot_password.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        APP_NAME = os.getenv("APP_NAME")

        context["APP_NAME"] = APP_NAME
        return context


class OrderHistoryPage(LoginRequiredMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        user = request.user
        orders = Order.objects.filter(user=user).order_by("-created_at")
        cart = None
        total_items = 0
        APP_NAME = os.getenv("APP_NAME")

        cart, created = Cart.objects.get_or_create(user=request.user)
        total_items = CartItem.objects.filter(cart=cart).aggregate(Sum("quantity"))[
            "quantity__sum"
        ]

        order_data = []
        for order in orders:
            order_items = OrderItem.objects.filter(order=order)
            order_item_data = []

            for order_item in order_items:
                first_image = (
                    order_item.product.productimage_set.first()
                    if order_item.product.productimage_set.exists()
                    else None
                )
                order_item_data.append(
                    {"order_item": order_item, "first_image": first_image}
                )

            order_data.append(
                {
                    "order": order,
                    "order_items": order_item_data,
                }
            )

        context = {
            "order_data": order_data,
            "APP_NAME": APP_NAME,
            "total_items_in_cart": total_items,
        }
        return render(request, "order_history.html", context)


# views.py
class OrderDetailsPage(LoginRequiredMixin, DetailView):
    def get(self, request, *args, **kwargs):
        order = get_object_or_404(Order, id=kwargs["order_id"])
        cart, created = Cart.objects.get_or_create(user=request.user)
        total_items = CartItem.objects.filter(cart=cart).aggregate(Sum("quantity"))[
            "quantity__sum"
        ]
        order_items = order.items.all()
        shipping_fee = float(settings.SHIPPING_FEE)
        APP_NAME = os.getenv("APP_NAME")

        discount_code = request.session.get("discount_code", None)
        currency_preference = request.session.get('currency_preference', 'NGN')

        context = {
            "total_items_in_cart": total_items,
            "order_items": order_items,
            "order": order,
            "APP_NAME": APP_NAME,
        }

        context.update(calculate_order_details(order_items, discount_code, currency_preference))

        return render(request, "order_details.html", context)


class OrderCompletePageView(LoginRequiredMixin, DetailView):
    def get(self, request, *args, **kwargs):
        order = get_object_or_404(Order, id=kwargs["order_id"])
        cart, created = Cart.objects.get_or_create(user=request.user)
        total_items = CartItem.objects.filter(cart=cart).aggregate(Sum("quantity"))[
            "quantity__sum"
        ]
        order_items = order.items.all()
        APP_NAME = os.getenv("APP_NAME")

        discount_code = request.session.get("discount_code", None)
        currency_preference = request.session.get('currency_preference', 'NGN')

        context = {
            "total_items_in_cart": total_items,
            "order_items": order_items,
            "order": order,
            "APP_NAME": APP_NAME,
        }

        context.update(calculate_order_details(order_items, discount_code, currency_preference))

        return render(request, "order_complete.html", context)


class WishListPage(ListView):
    template_name = "wishlist.html"

    def get_queryset(self):
        wishlist_item = []

        if self.request.user.is_authenticated:
            wishlist_item = WishListItem.objects.filter(user=self.request.user)
        
        products_in_wishlist = [item.product for item in wishlist_item]
        return products_in_wishlist

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_products = self.get_queryset()
        APP_NAME = os.getenv("APP_NAME")

        cart = None
        total_items = 0
        if self.request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=self.request.user)
            total_items = CartItem.objects.filter(cart=cart).aggregate(Sum("quantity"))[
                "quantity__sum"
            ]

            user_wishlist_items = WishListItem.objects.filter(user=self.request.user)
            wishlist_product_ids = user_wishlist_items.values_list("product__id", flat=True)

            product_wishlist_status = {}

            for product in all_products:
                is_in_wishlist = product.id in wishlist_product_ids
                product_wishlist_status[product.id] = is_in_wishlist
                
        else:
            product_wishlist_status = {product.id: False for product in all_products}


        wishlist_statuses = [product_wishlist_status[product.id] for product in all_products]

        products_in_wishlist = list(zip(get_products_with_images(all_products), wishlist_statuses))

        context["total_items_in_cart"] = total_items
        context["products_in_wishlist"] = products_in_wishlist
        context["APP_NAME"] = APP_NAME.title()
        return context


# Legal Views
class FAQPageView(TemplateView):
    def get(self, request, *args, **kwargs):
        cart = None
        total_items = 0
        APP_NAME = os.getenv("APP_NAME")

        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
            total_items = CartItem.objects.filter(cart=cart).aggregate(Sum("quantity"))[
                "quantity__sum"
            ]

        context = {
            "APP_NAME": APP_NAME,
            "total_items_in_cart": total_items,
        }
        return render(request, "faqs.html", context)


class TermsOfServicePageView(TemplateView):
    template_name = "terms_of_service.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        APP_NAME = os.getenv("APP_NAME")

        cart = None
        total_items = 0
        if self.request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=self.request.user)
            total_items = CartItem.objects.filter(cart=cart).aggregate(Sum("quantity"))[
                "quantity__sum"
            ]

        context["APP_NAME"] = APP_NAME
        context["total_items_in_cart"] = total_items
        return context


class ReturnAndRefund(TemplateView):
    template_name = "returns_and_refund.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        APP_NAME = os.getenv("APP_NAME")

        cart = None
        total_items = 0
        if self.request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=self.request.user)
            total_items = CartItem.objects.filter(cart=cart).aggregate(Sum("quantity"))[
                "quantity__sum"
            ]

        context["APP_NAME"] = APP_NAME
        context["total_items_in_cart"] = total_items
        return context


class DropShipping(TemplateView):
    template_name = "drop_shipping.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        APP_NAME = os.getenv("APP_NAME")

        cart = None
        total_items = 0
        if self.request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=self.request.user)
            total_items = CartItem.objects.filter(cart=cart).aggregate(Sum("quantity"))[
                "quantity__sum"
            ]

        context["APP_NAME"] = APP_NAME
        context["total_items_in_cart"] = total_items
        return context


# Function based handler views
def handleUserRegistration(request):
    try:
        firstName = request.POST.get("firstName")
        lastName = request.POST.get("lastName")
        email = request.POST.get("email")
        password = request.POST.get("password")
        cmfpassword = request.POST.get("cmfpassword")
        username = "User" + ''.join(random.choices(string.digits, k=7))
        hased_password = make_password(password)

        if CustomUser.objects.filter(email=email).exists():
            return JsonResponse({"success": False, "message": "Email already exists"})

        if password != cmfpassword:
            return JsonResponse(
                {"success": False, "message": "Passwords do not match!"}
            )

        if (
            CustomUser.objects.filter(username=username).exists()
            and not CustomUser.objects.filter(email=email).exists()
        ):
            new_user = CustomUser.objects.create(
                username ="User" + ''.join(random.choices(string.digits, k=7)),
                first_name=firstName,
                last_name=lastName,
                email=email,
                password=hased_password,
            )

        new_user = CustomUser.objects.create(
            username=username,
            first_name=firstName,
            last_name=lastName,
            email=email,
            password=hased_password,
        )
        create_notification(
            title="User joined",
            notification="A user just created an account",
            notification_type="REGISTRATION",
        )

        # HANDLE SEND EMAIL AFTER REGISTRATION
        APP_NAME = os.getenv("APP_NAME")
        subject = f"🎉 Welcome to {APP_NAME}! 🛍️"
        APP_URL = os.getenv("APP_URL")
        context = {"APP_NAME": APP_NAME, "APP_URL": APP_URL}
        body = render_to_string("email/welcome.html", context)
        send_message(subject, "", body, settings.DEFAULT_EMAIL, email)
        new_user.save()
        login(request, new_user)

        return JsonResponse({"success": True, "message": "Registration successful"})

    except Exception as e:
        return JsonResponse({"message": str(e)})


def handleUserLogin(request):
    try:
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = get_object_or_404(CustomUser, email=email)
        if user is not None:
            if user.check_password(password):
                login(request, user)
                return JsonResponse({"success": True, "message": "Login successful"})
            else:
                return JsonResponse(
                    {"success": False, "message": "Invalid username or password"}
                )
        else:
            return JsonResponse({"success": False, "message": "Invalid username or password"})
    except Http404:
        return JsonResponse({"success": False, "message": "Account not found!"})
    except Exception as e:
        return JsonResponse({"success": False, "message": "An error occurred"})


@login_required
def handleUserLogout(request):
    logout(request)
    return redirect(reverse("app:home_page"))


def set_currency_preference(request):
    if request.method == 'POST':
        currency_preference = request.POST.get('currency_preference')
        print(currency_preference)

        if currency_preference:
            request.session['currency_preference'] = currency_preference
            request.session['prices_converted'] = False

            print(request.session.get('currency_preference', 'NGN'))

    return redirect(request.META.get('HTTP_REFERER', ''))


@login_required
def handleAddToCart(request, product_id, color_selected, size_selected, quantity_selected):
    product = get_object_or_404(Product, id=product_id)
    user = request.user

    product_price = product.price_ngn
    # If the user is authenticated, handle their cart
    cart, created = Cart.objects.get_or_create(user=user)

    try:
        cart_item = CartItem.objects.get(
            cart=cart, product=product, size=size_selected, color=color_selected
        )
        cart_item.quantity += int(quantity_selected)
        cart_item.save()
        
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            cart=cart,
            product=product,
            color=color_selected,
            size=size_selected,
            quantity=int(quantity_selected),
            price=product_price,
        )
    
    # Calculate the subtotal for the cart_item based on the user's selected currency
    selected_currency = request.session.get('currency_preference')
    cart_item_subtotal = cart_item.subtotal(selected_currency)

    print(cart_item_subtotal)

    return redirect(request.META.get('HTTP_REFERER', ''))


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
    return JsonResponse({"total_amount": total_amount})


def handleContactForm(request):
    name = request.POST.get("name")
    email = request.POST.get("email")
    message = request.POST.get("message")

    subject = ""
    APP_NAME = "GlamourGlam"
    context = {"APP_NAME": APP_NAME, "name": name, "email": email, "message": message}
    body = render(request, "", context)
    send_message(subject, body, email, settings.DEFAULT_EMAIL)
    return redirect(reverse("app:contact_page"))


def handleSearchForm(request):  
    search_query = request.GET.get("search_query").lower()
    products = Product.objects.all()

    cart = None
    total_items = 0

    if search_query:
        products = products.filter(name__icontains=search_query) | products.filter(category__name__icontains=search_query) | products.filter(sub_category__name__icontains=search_query)

    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        total_items = CartItem.objects.filter(cart=cart).aggregate(Sum("quantity"))[
            "quantity__sum"
        ]

        user_wishlist_items = WishListItem.objects.filter(user=request.user)
        wishlist_product_ids = user_wishlist_items.values_list("product__id", flat=True)
        print(wishlist_product_ids)

        product_wishlist_status = {}

        for product in products:
            is_in_wishlist = product.id in wishlist_product_ids
            product_wishlist_status[product.id] = is_in_wishlist

    else:
        product_wishlist_status = {}
    
    wishlist_statuses = [status for status in product_wishlist_status.values()]

    all_products = get_products_with_images(products)

    products_in_wishlist = zip(all_products, wishlist_statuses)

    context = {
        "search_query": search_query,
        "products": all_products,
        "total_items_in_cart": total_items,
        "APP_NAME": os.getenv("APP_NAME"),
        "product_in_wishlist": products_in_wishlist,
    }
    return render(request, "search_results.html", context)


@login_required
def handleUpdateCart(request, color, size):
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        quantity = request.POST.get("quantity")

        try:
            # If the user is authenticated, update the cart in the database
            if request.user.is_authenticated:
                cart, created = Cart.objects.get_or_create(user=request.user)
                cart_item = CartItem.objects.get(cart=cart, product_id=product_id, color=color, size=size)
                new_quantity = int(quantity)
                if new_quantity >= 1:
                    cart_item.quantity = new_quantity
                    cart_item.save()
                    return JsonResponse({"success": True, "new_quantity": new_quantity})
                else:
                    cart_item.delete()

        except CartItem.DoesNotExist:
            return JsonResponse(
                {"success": False, "message": "Cart item does not exist"}
            )

    return JsonResponse({"success": False, "message": "Invalid request"})


@login_required
def handleSubscribeToNewsLetter(request):
    if request.method == "POST":
        email = request.POST.get("email")
        print(email)

        # HANDLE SEND EMAIL AFTER REGISTRATION
        subject = "💌 Thanks for Joining Our Newsletter! 🎉"
        APP_NAME = os.getenv("APP_NAME")
        APP_URL = os.getenv("APP_URL")
        context = {"APP_NAME": APP_NAME, "APP_URL": APP_URL}
        body = render_to_string("email/newsletter.html", context)
        send_message(subject, "", body, settings.DEFAULT_EMAIL, email)

        try:
            user = CustomUser.objects.filter(email=email).first()
        except CustomUser.DoesNotExist:
            return None

        group, created = Group.objects.get_or_create(name='registered for newsletter')

        if user:
            user.groups.add(group)
        else:
            print("User not found!")
        
        return JsonResponse({"success": True, "message": "Subscribe to newsletter"})

    return JsonResponse({"success": False, "message": "Invalid request"})


@login_required
def handleUpdateSecurityDetail(request):
    try:
        if request.method == "POST":
            old_password = request.POST.get("oldPassword")
            new_password = request.POST.get("newPassword")
            confirm_password = request.POST.get("ConfirmPassword")
            hashed_password = make_password(new_password)


            user = CustomUser.objects.get(id=request.user.id)

            if not user.check_password(old_password):
                return JsonResponse(
                    {"success": False, "message": "Old password is incorrect!"}
                )
            
            if not new_password == confirm_password:
                return JsonResponse(
                    {"success": False, "message": "Passwords do not match!"}
                )

            if new_password == old_password:
                return JsonResponse(
                    {"success": False, "message": "New password cannot be your current password!"}
                )

            user.password = hashed_password
            user.save()
            return JsonResponse(
                {"success": True, "message": "Password updated successfully"}
            )

        return JsonResponse({"success": False})
    except CustomUser.DoesNotExist:
        return None
    except Exception as e:
        return JsonResponse({"success": False})


@login_required
def handleUpdateProfileDetail(request):
    try:
        if request.method == "POST":
            first_name = request.POST.get("firstName")
            last_name = request.POST.get("lastName")
            email = request.POST.get("email")
            username = request.POST.get("username")

            if CustomUser.objects.filter(email=email).exists() and not email == request.user.email:
                return JsonResponse({'success': False, "message": "Email already exists"})
            
            if CustomUser.objects.filter(username=username).exists() and not username == request.user.username:
                return JsonResponse({'success': False, "message": "Username already exists"})

            user = CustomUser.objects.get(id=request.user.id)
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.username = username
            user.save()
            return JsonResponse(
                {"success": True, "message": "Profile updated successfully"}
            )

        return JsonResponse({"success": False, "message": "Invalid request"})
    except CustomUser.DoesNotExist:
        return None
    except Exception as e:
        print("An error occurred: %s" % str(e))


def handleAddProductReview(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        if request.method == "POST":
            fullName = request.POST.get("fullName")
            email = request.POST.get("email")
            phone = request.POST.get("phone")
            message = request.POST.get("message")
            rating = int(request.POST.get("rating"))

            new_review = Review.objects.create(
                review=message,
                authorFullName=fullName,
                authorEmail=email,
                authorPhoneNumber=phone,
                product=product,
                ratings=rating,
            )
            new_review.save()

            return JsonResponse({"success": True})

    except Exception as e:
        print("An error occurred: %s" % str(e))

    return render(
        request,
        "product-details.html",
    )


@login_required
def handleAddToWishList(request):
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        user = request.user
        product = get_object_or_404(Product, id=product_id)

        try:
            wishlist_item = WishListItem.objects.get(user=user, product=product)
            wishlist_item.delete()
            added = False
        except WishListItem.DoesNotExist:
            WishListItem.objects.create(user=user, product=product)
            added = True

        return JsonResponse({"added": added})
    return JsonResponse({"message": "Invalid request method"})


@login_required
def handleDeleteAccount(request):
    if request.method == "POST":
        current_user_email = request.user.email
        user = CustomUser.objects.get(email=current_user_email)
        user.delete()

        return redirect(reverse('app:login_page'))
    return JsonResponse({"error": "Invalid request method"})
