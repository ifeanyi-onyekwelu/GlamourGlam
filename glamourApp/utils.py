from random import sample
from django.core.mail import EmailMessage
from .models import ProductImage, Notification
from django.core.mail import send_mail
from django.conf import settings


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


def send_order_email(order):
    subject = f'New Order: Order #{order.id}'
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [order.user.email]

    # Prepare the context for rendering the HTML template
    context = {
        'order': order,
        'order_items': order.items.all()
    }

    # Render the email message content from an HTML template
    html_message = render_to_string('email/order_confirmation.html', context)

    # Create and send the email
    email = EmailMessage(subject, html_message, from_email, to_email)
    email.content_subtype = 'html'  # Set the content type to HTML
    email.send()

    # Send email to admin
    admin_email = 'admin@example.com'  # Replace with your admin's email
    email_to_admin = EmailMessage(subject, html_message, from_email, [admin_email])
    email_to_admin.content_subtype = 'html'
    email_to_admin.send()