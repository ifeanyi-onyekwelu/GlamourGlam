from django.urls import path
from .views import *

app_name = 'my_admin'

urlpatterns = [
    path('', dashboard, name="dashboard"),
    # ########################################
    # Order urls
    # ########################################
    path('users/', all_user, name="users"),
    path('user/<uuid:user_id>', user_detail, name="user_detail"),
    path('user/<uuid:user_id>/active', mark_user_as_active, name="mark_user_as_active"),
    path('user/<uuid:user_id>/suspended', mark_user_as_suspended, name="mark_user_as_suspended"),

    # ########################################
    # Products urls
    # ########################################
    path('product/', all_products, name="products"),
    path('product/<uuid:product_id>', product_detail, name="product_detail"),
    path('product/add/', add_product, name="add_product"),
    path('product/edit/<uuid:product_id>/', edit_product, name="edit_product"),

    # ########################################
    # Category urls
    # ########################################
    path('category/', all_category, name="categories"),
    path('category/<uuid:category_id>', category_detail, name="category_detail"),
    path('category/add/', add_category, name="add_category"),
    path('category/<uuid:category_id>/edit', edit_category, name="edit_category"),
    path('category/delete/<uuid:category_id>', delete_category, name="delete_category"),
    path('category/delete/all/', delete_all_category, name="delete_all_category"),

    # ########################################
    # Color urls
    # ########################################
    path('color/', all_product_color, name="colors"),
    path('color/add/', add_color, name="add_color"),  
    path('color/delete/<int:color_id>', delete_color, name="delete_color"),
    path('color/delete/all/', delete_all_colors, name="delete_all_colors"),  

    # ########################################
    # Sub Category urls
    # ########################################
    path('sub-category/', all_sub_category, name="sub_categories"),
    path('sub-category/<uuid:sub_category_id>', sub_category_detail, name="sub_category_detail"),
    path('sub-category/add/', add_sub_category, name="add_sub_category"),
    path('sub-category/<uuid:sub_category_id>/edit', edit_sub_category, name="edit_sub_category"),
    path('sub-category/delete/<uuid:sub_category_id>', delete_sub_category, name="delete_sub_category"),
    path('sub-category/delete/all/', delete_all_sub_category, name="delete_all_sub_category"),

    # ########################################
    # Order urls
    # ########################################
    path('orders', all_order, name="orders"),
    path('order/<uuid:order_id>', order_detail, name="order_detail"),
    path('order-update/<uuid:order_id>/shipped', mark_order_as_shipped, name="mark_order_as_shipped"),
    path('order-update/<uuid:order_id>/delivered', mark_order_as_delivered, name="mark_order_as_delivered"),
    path('order-update/<uuid:order_id>/failed-delivery', mark_order_as_failed_delivery, name="mark_order_as_failed_delivery"),
    path('order/pending-orders/', all_pending_orders, name="all_pending_orders"),
    path('order/shipped-orders/', all_shipped_orders, name="all_shipped_orders"),
    path('order/delivered-orders/', all_delivered_orders, name="all_delivered_orders"),
    path('order/failed-delivery-orders/', all_failed_delivery_orders, name="all_failed_delivery_orders"),


    # ########################################
    # Discount urls
    # ########################################
    path('discount-codes/', all_coupons, name="discount_codes"),
    path('discount/<uuid:coupon_id>', coupon_detail, name="coupon_detail"),
    path('discount/add/', create_coupon, name="create_coupon"),
    path('discount/delete/all', delete_all_coupons, name="delete_all_coupons"),
    path('discount/delete/<uuid:coupon_id>', delete_coupon, name="delete_coupon"),


    # ########################################
    # Newsletter urls
    # ########################################
    path('subscribed-to-news-letter/', news_letter_subscribers, name="subscribed_to_news_letter"),
    path('compose-news-letter/', compose_and_send_message, name="compose_and_send_message"),
    path('remove-from-newsletter/<int:user_id>/', remove_newsletter_subscriber, name='remove_newsletter_subscriber'),

    # ########################################
    # Shipping urls
    # ########################################
    path('shipping-address/', all_shipping_address, name="shipping_addresses"),
    path('shipping-address/<uuid:shipping_id>', shipping_detail, name="shipping_detail"),
    path('shipping-address/delete/<uuid:shipping_id>', delete_shipping_address, name="delete_shipping_address"),
    path('shipping-address/delete/all', delete_all_shipping_addresses, name="delete_all_shipping_address"),


    # ########################################
    # Profile urls
    # ########################################
    path('profile/', admin_profile_page, name="profile"),
    path('edit-profile/', edit_profile, name="edit_profile"),
    path('change-password/', change_password, name="change_password"),

    # ########################################
    # Authentication urls
    # ########################################
    path('login/', admin_login, name="login"),
    path('signup/', admin_signup, name="signup"),
    path('logout/', admin_logout, name="logout"),

    # Error handling
    # path('error-404/', error404, name="error404"),
    # path('error-500/', error500, name="error500"),
]
