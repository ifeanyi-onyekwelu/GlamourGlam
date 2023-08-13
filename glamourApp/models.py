from django.db import models
from django.contrib.auth import get_user_model
import uuid
import random
from django.utils import timezone
import string


class Category(models.Model):
    name = models.CharField(max_length=255, default="")
    description = models.TextField(default="")

    def __str__(self):
        return self.name

class SubCategory(models.Model):
    name = models.CharField(max_length=255, default="")

    def __str__(self):
        return self.name

class Product(models.Model):
    id = models.UUIDField(
        primary_key=True,
        editable=False,
        default=uuid.uuid4
    )
    name = models.CharField(max_length=255, default="")
    sub_category = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    description = models.TextField(default="")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)

    sizes = models.ManyToManyField('ProductSize', related_name='products', null=True, blank=True)
    images = models.ManyToManyField('ProductImage', related_name='products')

    def __str__(self):
        return f'{self.name} for {self.category.name}, price: {self.price}'

class ProductSize(models.Model):
    name = models.CharField(max_length=20)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)


    def __str__(self):
        return self.name

class ProductColor(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    color = models.CharField(max_length=255)

    def __str__(self):
        return self.color

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images/')

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    review = models.TextField(default="")
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author.first_name} {self.author.last_name} says the product: '{self.product}' is {self.review}"

class Cart(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for {self.user.first_name} {self.user.last_name}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.quantity} {self.product} in cart"

    def subtotal(self):
        return self.product.price * self.quantity

class Order(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    items = models.ManyToManyField('OrderItem', related_name='orders')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    order_id = models.CharField(max_length=200, default="")
    payment_status_choices = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('CANCELLED', 'Cancelled'),
    ]
    DELIVERY_STATUS_CHOICES = (
        ('P', 'Pending'),
        ('S', 'Shipped'),
        ('D', 'Delivered'),
        ('F', 'Failed Delivery'),
    )
    payment_status = models.CharField(max_length=20, choices=payment_status_choices, default="Pending")
    delivery_status = models.CharField(max_length=1, choices=DELIVERY_STATUS_CHOICES, default='P')
    shipping_address = models.ForeignKey('ShippingAddress', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Order #{self.id} for {self.user.first_name} {self.user.last_name}"

    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=30))

        super(Order, self).save(*args, **kwargs)

class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.quantity}x {self.product.name} in Order #{self.order.id}"

    def subtotal(self):
        return self.item_price * self.quantity

class ShippingAddress(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    phone = models.CharField(max_length=30, default="")
    country = models.CharField(max_length=200)
    appartment = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    state = models.CharField(max_length=200)
    zipcode = models.CharField(max_length=200)
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} order to be shipped to {self.country} {self.state} {self.address}"

class Return(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    status = models.CharField(max_length=1, choices=(
        ('P', 'Pending'),
        ('A', 'Approved'),
        ('R', 'Rejected')
    ), default='P')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.order.user.first_name + ' ' + self.order.user.last_name + ' ' + self.reason

class DiscountCode(models.Model):
    code = models.CharField(max_length=20, default="")
    percentage = models.PositiveIntegerField()
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.code

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=20))

        current_time = timezone.now()

        if self.valid_from <= current_time <= self.valid_to:
            self.active = True
        else:
            self.active = False

        super(DiscountCode, self).save(*args, **kwargs)
