from django.urls import path
from .views import *

app_name = 'app'

urlpatterns = [
    path('', HomePageView.as_view(), name="home_page"),
    path('about/', AboutPageView.as_view(), name="about_page"),
    path('women/', WomenPageView.as_view(), name="women_page"),
    path('men/', MenPageView.as_view(), name="men_page"),
    path('shop/', ShopPageView.as_view(), name="shop_page"),
    path('kids/', KidsPageView.as_view(), name="kids_page"),
    path('unisex/', UnisexPageView.as_view(), name="unisex_page"),
    path('accessories/', AccessoriesPageView.as_view(), name="accessories_page"),
    path('contact/', ContactPageView.as_view(), name="contact_page"),
    path('product/<uuid:pk>/', ProductDetailPageView.as_view(), name="product_detail_page"),
    path('cart/', ShopCartPageView.as_view(), name="cart_page"),
    path('checkout/', CheckoutPageView.as_view(), name="checkout_page"),
    path('account/', AccountPageView.as_view(), name="account_page"),
    path('security/', SecurityAccountPageView.as_view(), name="security_account_page"),
    path('order-history/', OrderHistoryPage.as_view(), name="order_history"),
    path('order-details/<uuid:order_id>/', OrderDetailsPage.as_view(), name="order_details"),
    path('order-complete/<uuid:order_id>/complete/', OrderCompletePageView.as_view(), name="order_complete"),
    path('login/', LoginPageView.as_view(), name="login_page"),
    path('register/', RegisterPageView.as_view(), name="register_page"),
    path('faqs/', FAQPageView.as_view(), name="faqs_page"),
    path('privacy-policy/',PrivacyPolicyPageView.as_view(), name="privacy_policy_page"),
    path('terms-of-service/', TermsOfServicePageView.as_view(), name="terms_of_service_page"),
    path('returns-policy/', ReturnAndRefund.as_view(), name="returns_and_refunds_page"),
    path('dropshipping/', DropShipping.as_view(), name="dropshipping_page"),

    # Handler urls
    path('handle-registration/', handleUserRegistration, name="handleUserRegistration"),
    path('handle-login/', handleUserLogin, name="handleUserLogin"),
    path('add-to-cart/<uuid:product_id>/<str:color_selected>/<str:size_selected>/<int:quantity_selected>/', handleAddToCart, name="handleAddToCart"),
    path('remove-item/<uuid:cart_item_id>/', handleRemoveCartItem, name="handleRemoveCartItem"),
    path('send-message/', handleContactForm, name="handleContactForm"),
    path('search/', handleSearchForm, name="handleSearchForm"),
    path('subscribe-to-newsletter/', handleSubscribeToNewsLetter, name="handleSubscribeToNewsLetter"),
    path('update-profile/', handleUpdateProfileDetail, name="handleUpdateProfileDetail"),
    path('change-password/', handleUpdateSecurityDetail, name="handleUpdateSecurityDetail"),
    path('update-item/', handleUpdateCart, name="handleUpdateCart"),
    path('product/add-review/<uuid:product_id>/', handleAddProductReview, name="handleAddProductReview"),
    path('product/add-to-wishlist/', handleAddToWishList, name="handleAddToWishList"),
    path('logout/', handleUserLogout, name="handleUserLogout"),
    path('delete-account/', handleDeleteAccount, name="handleDeleteAccount"),

    # Error handling
    # path('error-404/', error404, name="error404"),
    # path('error-500/', error500, name="error500"),
]