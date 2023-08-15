from django.urls import path
from .views import *

app_name = 'app'

urlpatterns = [
    path('', HomePageView.as_view(), name="home_page"),
    path('women/', WomenPageView.as_view(), name="women_page"),
    path('men/', MenPageView.as_view(), name="men_page"),
    path('shop/', ShopPageView.as_view(), name="shop_page"),
    path('kids/', KidsPageView.as_view(), name="kids_page"),
    path('accessories', AccessoriesPageView.as_view(), name="accessories_page"),
    path('contact/', ContactPageView.as_view(), name="contact_page"),
    path('<uuid:pk>/product', ProductDetailPageView.as_view(), name="product_detail_page"),
    path('cart/', ShopCartPageView.as_view(), name="cart_page"),
    path('checkout/', CheckoutPageView.as_view(), name="checkout_page"),
    path('login/', LoginPageView.as_view(), name="login_page"),
    path('register/', RegisterPageView.as_view(), name="register_page"),

    # Handler urls
    path('handle-registration/', handleUserRegistration, name="handleUserRegistration"),
    path('handle-login/', handleUserLogin, name="handleUserLogin"),
    path('add-to-cart/<uuid:product_id>/<str:color_selected>/<str:size_selected>/<int:quantity_selected>/', handleAddToCart, name="handleAddToCart"),
    path('delete-item/<int:cart_item_id>/', handleRemoveCartItem, name="handleRemoveCartItem"),
    path('send-message/', handleContactForm, name="handleContactForm"),
    path('search/', handleSearchForm, name="handleSearchForm"),
    path('subscribe-to-newsletter/', handleSubscribeToNewsLetter, name="handleSubscribeToNewsLetter"),
    path('update-item/', handleUpdateCart, name="handleUpdateCart"),
    path('logout/', handleUserLogout, name="handleUserLogout"),

    # Error handling
    # path('error-404/', error404, name="error404"),
    # path('error-500/', error500, name="error500"),
]