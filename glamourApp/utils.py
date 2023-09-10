from random import sample
from django.core.mail import EmailMessage
from .models import ProductImage, Notification, DiscountCode
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from dotenv import load_dotenv
from django.template.loader import render_to_string
import os

load_dotenv()


def get_products_with_images(products_list):
    products_with_images = []
    for product in products_list:
        try:
            image = ProductImage.objects.filter(product=product).latest('id')
        except ProductImage.DoesNotExist:
            print("Image does not exist for product")
            image = None

        products_with_images.append({'product': product, 'image': image})
    return products_with_images

def send_message(subject, message, html_message, sender, reciepient):
    send_mail(
        subject,
        message,
        sender,
        [reciepient],
        html_message=html_message,
        fail_silently=False
    )

def create_notification(title, notification, notification_type='Reports'):
    new_notification = Notification(
        title=title,
        notification=notification,
        notification_type=notification_type,
    )
    new_notification.save()

def send_order_email(request, order):
    subject = f"Your Order Confirmation - Order #{order.id}"
    recipient_email = order.user.email  # Assuming you have the user's email
    APP_NAME = os.getenv('APP_NAME')
    APP_URL = os.getenv('APP_URL')

    order_items = order.items.all()
    shipping_fee = float(settings.SHIPPING_FEE)

    for order_item in order_items:
        order_item.first_image = order_item.product.productimage_set.first()
        order_item.subtotal = order_item.quantity * order_item.product.price

    discount_code = request.session.get("discount_code", None)
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
        "order_items": order_items,
        "order": order,
        "total_amount": total_amount,
        "shipping_fee": shipping_fee,
        "total_amount_shipping": total_amount_shipping,
        "APP_NAME": APP_NAME,
        "APP_URL": APP_URL
    }

    message = render_to_string("email/order_confirmation.html", context)

    send_mail(
        subject,
        "",
        settings.DEFAULT_EMAIL,  # Sender's email
        [recipient_email],  # Recipient's email
        html_message=message,
    )

def send_admin_order_email(request, order):
    subject = f"Order Confirmation - Order #{order.order_number}"
    recipient_email = settings.DEFAULT_EMAIL
    APP_NAME = os.getenv('APP_NAME')
    APP_URL = os.getenv('APP_URL')

    order_items = order.items.all()
    shipping_fee = float(settings.SHIPPING_FEE)

    for order_item in order_items:
        order_item.first_image = order_item.product.productimage_set.first()
        order_item.subtotal = order_item.quantity * order_item.product.price

    discount_code = request.session.get("discount_code", None)
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
        "order_items": order_items,
        "order": order,
        "total_amount": total_amount,
        "shipping_fee": shipping_fee,
        "total_amount_shipping": total_amount_shipping,
        "APP_NAME": APP_NAME,
        "APP_URL": APP_URL
    }

    message = render_to_string("email/admin_order_confirmation.html", context)

    send_mail(
        subject,
        "",
        settings.DEFAULT_EMAIL,  # Sender's email
        [recipient_email],  # Recipient's email
        html_message=message,
    )

def calculate_discounted_total(total, discount_percentage):
    discount_amount = (discount_percentage / 100) * total
    discounted_total = total - discount_amount
    return discounted_total