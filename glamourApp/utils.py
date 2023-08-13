from random import sample
from .models import ProductImage
from django.core.mail import send_mail

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


def send_message(subject, message, sender, reciepient):
    send_mail(
        subject,
        message,
        sender,
        [reciepient],
        fail_silently=False
    )

def create_notification(title, notification, notification_type='Reports'):
    new_notification = Notification(
        title=title,
        notification=notification,
        notification_type=notification_type,
    )
    new_notification.save()

