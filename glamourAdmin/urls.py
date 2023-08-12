from django.urls import path
from .views import *

app_name = 'my_admin'

urlpatterns = [
    path('', dashboard, name="dashboard"),
    # ########################################
    # Order urls
    # ########################################
    path('users/', all_user, name="users"),
    path('user/<int:user_id>', user_detail, name="user_detail"),

    # ########################################
    # Products urls
    # ########################################
    path('products/', all_products, name="products"),
    path('products/<int:product_id>', product_detail, name="product_detail"),
    path('product/add/', add_product, name="add_product"),

    # ########################################
    # Category urls
    # ########################################
    path('category/', all_category, name="categories"),
    path('category/<int:categoryb_id>', category_detail, name="category_detail"),
    path('category/add/', add_category, name="add_category"),

    # ########################################
    # Sub Category urls
    # ########################################
    path('sub-category/', all_sub_category, name="sub_categories"),
    path('sub-category/<int:sub_category_id>', sub_category_detail, name="sub_category_detail"),
    path('sub-category/add/', add_sub_category, name="add_sub_category"),

    # ########################################
    # Size urls
    # ########################################
    path('sizes/', all_sizes, name="sizes"),
    path('size/<int:size_id>', size_detail, name="size_detail"),
    path('size/add/', add_size, name="add_size"),

    # ########################################
    # Order urls
    # ########################################
    path('orders', all_order, name="orders"),
    path('order/<int:order_id>', order_detail, name="order_detail"),
    path('order-update/<int:order_id>/shipped', mark_order_as_shipped, name="mark_order_as_shipped"),
    path('order-update/<int:order_id>/delivered', mark_order_as_delivered, name="mark_order_as_delivered"),
    path('order-update/<int:order_id>/failed-delivery', mark_order_as_failed_delivery, name="mark_order_as_failed_delivery"),
    path('order/pending-orders/', all_pending_orders, name="all_pending_orders"),
    path('order/shipped-orders/', all_shipped_orders, name="all_shipped_orders"),
    path('order/delivered-orders/', all_delivered_orders, name="all_delivered_orders"),
    path('order/failed-delivery-orders/', all_failed_delivery_orders, name="all_failed_delivery_orders"),


    # ########################################
    # Discount urls
    # ########################################
    path('discount-codes/', all_coupons, name="discount_codes"),
    path('discount/<int:coupon_id>', coupon_detail, name="coupon_detail"),
    path('discount/add/', create_coupon, name="create_coupon"),

    # ########################################
    # Shipping
    # ########################################
    path('shipping/', all_shipping_address, name="shipping_addresses"),
    path('shipping/<int:shipping_id>', shipping_detail, name="shipping_address"),

    # ########################################
    # Authentication
    # ########################################
    path('login/', admin_login, name="login"),
    path('logout/', admin_logout, name="logout"),
]