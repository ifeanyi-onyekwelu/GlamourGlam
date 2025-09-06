from django.contrib import admin
# from .models import (
#     Product,
#     Order,
#     ShippingAddress,
#     OrderItem,
#     Review,
#     Category,
#     Cart,
#     CartItem,
#     ProductImage,
#     DiscountCode,
#     ProductSize, 
#     Notification,
#     ProductColor
# )

from .models import Payment

# # Register your models here.

# class ProductImageInline(admin.TabularInline):
#     model = ProductImage

# class ProductSizeInline(admin.TabularInline):
#     model = ProductSize

# class ReviewAdmin(admin.TabularInline):
#     model = Review

# class ProductAdmin(admin.ModelAdmin):
#     list_display = [
#         "name",
#         "description",
#         'sub_category',
#         "category",
#         "date_created",
#     ]

#     inlines = [ProductImageInline,  ProductSizeInline, ReviewAdmin]


# class CategoryAdmin(admin.ModelAdmin):
#     model = Category
#     list_display = ["name", "description"]

# class NotificationAdmin(admin.ModelAdmin):
#     model = Notification
#     list_display = ["title", "notification_type", 'notification', 'date_created']

# class ColorAdmin(admin.ModelAdmin):
#     model = ProductColor
#     list_display = ["color"]


# class CartItemInline(admin.TabularInline):
#     model = CartItem


# class CartAdmin(admin.ModelAdmin):
#     list_display = ["user", "created_at", "updated_at", "get_cart_items"]

#     def get_cart_items(self, obj):
#         return ", ".join([item.product.name for item in obj.items.all()])

#     get_cart_items.short_decription = "Cart items"
#     inlines = [CartItemInline]


# class OrderItemInline(admin.TabularInline):
#     model = OrderItem


# class OrderAdmin(admin.ModelAdmin):
#     list_display = [
#         "user",
#         "total_price",
#         "created_at",
#         "order_number",
#         "payment_status",
#         "shipping_address",
#         "get_order_items",
#     ]

#     def get_order_items(self, obj):
#         return ", ".join([item.product.name for item in obj.items.all()])

#     get_order_items.short_decription = "Order items"
#     inlines = [OrderItemInline]


# class ShippingAdmin(admin.ModelAdmin):
#     model = ShippingAddress
#     list_display = [
#         "user",
#         "order",
#         "phone",
#         "country",
#         "appartment",
#         "address",
#         "city",
#         "state",
#         "zipcode",
#         "date_added",
#     ]

# class DiscountAdmin(admin.ModelAdmin):
#     model = DiscountCode
#     list_display = [
#         "code",
#         "percentage",
#         "valid_from",
#         "valid_to",
#         "active"
#     ]

class  PaymentAdmin(admin.ModelAdmin):
    list_display  = ["id", "ref", 'amount', "verified", "date_created"]

admin.site.register(Payment, PaymentAdmin)


# admin.site.register(Product, ProductAdmin)
# admin.site.register(Order, OrderAdmin)
# admin.site.register(ShippingAddress, ShippingAdmin)
# admin.site.register(Cart, CartAdmin)
# admin.site.register(Category, CategoryAdmin)
# admin.site.register(DiscountCode, DiscountAdmin)
# admin.site.register(Notification, NotificationAdmin)
# admin.site.register(ProductColor, ColorAdmin)
