from random import sample
from .models import ProductImage
from django.core.mail import send_mail

def get_products_with_images(products_list):
    products_with_images = []
    for product in products_list:
        try:
            image = ProductImage.objects.filter(product=product).latest('id')
        except ProductImage.DoesNotExist:
            image = None

        products_with_images.append({'product': product, 'image': image})
    return products_with_images


def send_message(subject, message, reciepient, sender):
    send_mail(
        subject,
        message,
        sender,
        [reciepient],
        fail_silently=False
    )

