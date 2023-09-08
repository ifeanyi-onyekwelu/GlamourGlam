from glamourApp.models import Order, Product, SubCategory, Category, ProductSize
from users.models import CustomUser
from glamourApp.models import ProductImage, Notification
from django.core.mail import send_mail # Import the TextIOWrapper class


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

def update_user_status(user_id, status):
    user = CustomUser.objects.get(id=user_id)
    user.is_active = status
    user.save()

def update_order_delivery_status(order_id, status):
    order = Order.objects.get(pk=order_id)
    order.delivery_status = status
    order.save()

def get_all_notifications():
    notifications = Notification.objects.order_by('-date_created')[:3]
    return notifications

def create_notification(title, notification, notification_type='Reports'):
    new_notification = Notification(
        title=title,
        notification=notification,
        notification_type=notification_type,
    )
    new_notification.save()