from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
import os
from dotenv import load_dotenv
from .decorators import admin_only_login
from users.models import CustomUser
from django.contrib.auth import login, logout, authenticate
from glamourApp.models import *
from .utils import update_order_delivery_status, update_user_status, get_products_with_images, send_message, get_all_notifications, create_notification
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .forms import CategoryForm, CouponForm, SubCategoryForm, SizeForm, ColorForm
import string
import random
from django.utils import timezone
from datetime import timedelta
import calendar

load_dotenv()


@admin_only_login
def dashboard(request):
    orders = Order.objects.all()
    users = CustomUser.objects.all()

    # Just me performing some logic
    current_month = timezone.now().month
    current_year = timezone.now().year
    current_date = timezone.now().date()
    yesterday = current_date - timezone.timedelta(days=1)

    # To get the total orders of today
    orders_today = orders.filter(created_at__date=current_date)
    orders_yesterday = orders.filter(created_at__date=yesterday)

    total_order_today = orders_today.filter(delivery_status="P").count()
    total_order_yesterday = orders_yesterday.filter(
        delivery_status="P").count()
    percentage_change = 0
    if total_order_yesterday == 0:
        percentage_change = 100.0
    else:
        percentage_change = (
            (total_order_today - total_order_yesterday) / total_order_yesterday) * 100

    # Using these to perform some logic
    first_day = timezone.datetime(current_year, current_month, 1)
    last_day = timezone.datetime(current_year, current_month, calendar.monthrange(
        current_year, current_month)[1])

    # Get orders from this month
    filtered_monthly_orders = orders.filter(
        created_at__range=(first_day, last_day))
    # Get users that joined this month
    filtered_monthly_users_joined = users.filter(
        date_joined__range=(first_day, last_day)).count()

    # Get users that joined last month
    last_month = current_month - 1 if current_month > 1 else 12
    last_year = current_year if current_month > 1 else current_year - 1
    last_month_first_day = timezone.datetime(last_year, last_month, 1)
    last_month_last_day = timezone.datetime(
        last_year, last_month, calendar.monthrange(last_year, last_month)[1])
    filtered_last_month_users_joined = users.filter(
        date_joined__range=(last_month_first_day, last_month_last_day)).count()
    filtered_last_month_orders = orders.filter(
        created_at__range=(last_month_first_day, last_month_last_day))
    filtered_this_month_orders = orders.filter(
        created_at__range=(first_day, timezone.now()))

    percentage_change_users = 0
    if filtered_last_month_users_joined == 0:
        percentage_change_users = 100.0
    else:
        percentage_change_users = (
            (filtered_monthly_users_joined - filtered_last_month_users_joined) / filtered_last_month_users_joined) * 100

    # Get orders from last year
    last_year_first_day = timezone.datetime(current_year - 1, 1, 1)
    last_year_last_day = timezone.datetime(current_year - 1, 12, 31)
    filtered_last_year_orders = orders.filter(
        created_at__range=(last_year_first_day, last_year_last_day))

    percentage_change_users = 0
    if filtered_last_month_users_joined == 0:
        percentage_change_users = 100.0
    else:
        percentage_change_users = (
            (filtered_monthly_users_joined - filtered_last_month_users_joined) / filtered_last_month_users_joined) * 100

    total_orders = orders.count()
    percentage_change_orders_year = 0
    total_orders_last_year = filtered_last_year_orders.count()
    if total_orders_last_year == 0:
        percentage_change_orders_year = 100.0
    else:
        percentage_change_orders_year = (
            (total_orders - total_orders_last_year) / total_orders_last_year) * 100

    total_pending_orders = orders.filter(delivery_status="P").count()
    total_income = sum(order.total_price for order in filtered_monthly_orders)
    total_income_last_month = sum(
        order.total_price for order in filtered_last_month_orders)
    total_income_this_month = sum(
        order.total_price for order in filtered_this_month_orders)

    percentage_change_income = 0
    if total_income_last_month == 0:
        percentage_change_income = 100.0
    else:
        percentage_change_income = (
            (total_income - total_income_last_month) / total_income_last_month) * 100

    # Handle display of 6 random orders
    random_orders = orders.order_by('?')[:6]

    context = {
        'total_income': total_income,
        'total_users_joined_per_month': filtered_monthly_users_joined,
        'total_pending_orders': total_pending_orders,
        'total_orders': total_orders,
        'total_order_today': total_order_today,
        'total_order_yesterday': total_order_yesterday,
        'percentage_change': percentage_change,
        'percentage_change_users': percentage_change_users,
        'percentage_change_orders_year': percentage_change_orders_year,
        'percentage_change_income': percentage_change_income,
        'total_income_last_month': total_income_last_month,
        'total_income_this_month': total_income_this_month,
        'random_orders': random_orders,
        'notifications': get_all_notifications(),
        'APP_NAME': os.getenv('APP_NAME')
    }
    return render(request, 'admin_dashboard/index.html', context)

# ########################################
# User
# ########################################


@admin_only_login
def all_user(request):
    users = CustomUser.objects.all()
    context = {
        'users': users, 
        'APP_NAME': os.getenv('APP_NAME'), 
        'notifications': get_all_notifications(),
    }
    return render(request, 'admin_dashboard/user/all.html', context)


@admin_only_login
def user_detail(request, user_id):
    user = CustomUser.objects.get(id=user_id)
    return render(request, 'admin_dashboard/user/user_detail.html', {'user': user, 'APP_NAME': os.getenv('APP_NAME'), 'notifications': get_all_notifications(),})


@admin_only_login
def mark_user_as_active(request, user_id):
    update_user_status(user_id, True)
    return redirect('my_admin:users')


@admin_only_login
def mark_user_as_suspended(request, user_id):
    update_user_status(user_id, False)
    return redirect('my_admin:users')

# ########################################
# Product
# ########################################


@admin_only_login
def all_products(request):
    products = Product.objects.all()

    products_with_images = get_products_with_images(products)

    context = {
        'products': products_with_images,
        'APP_NAME': os.getenv('APP_NAME'),
        'notifications': get_all_notifications(),
    }

    return render(request, 'admin_dashboard/product/all.html', context)


@admin_only_login
def product_detail(request, product_id):
    product = Product.objects.get(id=product_id)
    productImage = ProductImage.objects.filter(product=product)
    original_price = product.price
    price_with_increase = float(original_price) * 1.25

    context = {
        'product': product,
        'productImage': productImage,
        'original_price': original_price,
        'price_with_increase': price_with_increase,
        'APP_NAME': os.getenv('APP_NAME'),
        'notifications': get_all_notifications(),
    }

    return render(request, 'admin_dashboard/product/product_detail.html', context)


@admin_only_login
def add_product(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        category = request.POST.get('category')
        category_matched = Category.objects.get(name=category)
        sub_category = request.POST.get('sub_category')
        sub_category_matched = SubCategory.objects.get(name=sub_category, category=category_matched)
        sizes = request.POST.getlist('size')
        colors = request.POST.getlist('color')
        images = request.FILES.getlist('image')
        product = Product.objects.create(
            name=name,
            sub_category=sub_category_matched,
            description=description,
            price=price,
            category=category_matched
        )

        for size_name in sizes:
            size = ProductSize.objects.create(name=size_name, product=product)
            product.sizes.add(size)
            size.save()
            product.save()

        for image in images:
            img = ProductImage.objects.create(product=product, image=image)
            product.images.add(img)
            img.save()
            product.save()

        for color in colors:
            col, created = ProductColor.objects.get_or_create(color=color)
            product.colors.add(col)
            col.save()
            product.save()

        return redirect('my_admin:product_detail', product_id=product.id)

    sub_categories = SubCategory.objects.all()
    categories = Category.objects.all()
    sizes = ProductSize.objects.all()
    colors = ProductColor.objects.all()
    print(sub_categories)
    context = {
        'sub_categories': sub_categories,
        'categories': categories,
        'sizes': sizes,
        'colors': colors,
        'APP_NAME': os.getenv('APP_NAME'),
        'notifications': get_all_notifications(),
    }
    return render(request, 'admin_dashboard/product/add.html', context)


@admin_only_login
def edit_product(request, product_id):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        category = request.POST.get('category')
        category_matched = Category.objects.get(name=category)
        sub_category = request.POST.get('sub_category')
        sub_category_matched = SubCategory.objects.get(name=sub_category, category=category_matched)
        sizes = request.POST.getlist('size')
        colors = request.POST.getlist('color')
        images = request.FILES.getlist('image')
        product = Product.objects.get(id=product_id)

        try:
            product.name = name
            product.sub_category = sub_category_matched
            product.description = description
            product.price = price
            product.category = category_matched

            # Handling sizes
            for size in product.sizes.all():
                if size.name not in sizes:
                    product.sizes.remove(size)

            for size_name in sizes:
                print(size_name)
                size, created = ProductSize.objects.get_or_create(
                    name=size_name, product=product)
                print("Size exists: ", created)
                if created:
                    product.sizes.add(size)
                size.save()

            for image in images:
                img, created = ProductImage.objects.get_or_create(
                    product=product, image=image)
                print("Image exists: ", created)
                if not created:
                    product.images.add(img)
                img.save()

            # Handling unchecked colors
            for color in product.colors.all():
                if color.color not in colors:
                    product.colors.remove(color)

            for color in colors:
                col, created = ProductColor.objects.get_or_create(color=color)
                print("Color exists: ", created)
                if not created:
                    product.colors.add(col)
                col.save()

            product.save()
            return redirect('my_admin:product_detail', product_id=product.id)
        except Product.DoesNotExist:
            print(Product.DoesNotExist(str(e)))

    sub_categories = SubCategory.objects.all()
    categories = Category.objects.all()
    sizes = ProductSize.objects.all()
    product = Product.objects.get(id=product_id)
    colors = ProductColor.objects.all()
    productImages = ProductImage.objects.filter(product=product)
    context = {
        'sub_categories': sub_categories,
        'categories': categories,
        'sizes': sizes,
        'colors': colors,
        'product': product,
        'productImages': productImages,
        'APP_NAME': os.getenv('APP_NAME'),
        'notifications': get_all_notifications(),
    }
    return render(request, 'admin_dashboard/product/edit.html', context)

# ########################################
# Category
# ########################################


@admin_only_login
def all_category(request):
    categories = Category.objects.all()
    return render(request, 'admin_dashboard/category/all.html', {'categories': categories, 'APP_NAME': os.getenv('APP_NAME'), 'notifications': get_all_notifications(),})


@admin_only_login
def category_detail(request, category_id):
    category = Category.objects.get(id=category_id)
    return render(request, 'admin_dashboard/category/category_detail.html', {'category': category, 'APP_NAME': os.getenv('APP_NAME'), 'notifications': get_all_notifications(),})


@admin_only_login
def add_category(request):
    if request.method == 'POST':
        category_form = CategoryForm(request.POST)

        if category_form.is_valid():
            category = category_form.save()
            return redirect('my_admin:category_detail', category_id=category.id)
    else:
        category_form = CategoryForm()
    return render(request, 'admin_dashboard/category/add.html', {'category_form': category_form, 'APP_NAME': os.getenv('APP_NAME'), 'notifications': get_all_notifications(),})


@admin_only_login
def edit_category(request, category_id):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')

        category = Category.objects.get(id=category_id)

        category.name = name
        category.description = description
        category.save()

        return redirect('my_admin:category_detail', category_id=category.id)

    return render(request, 'admin_dashboard/category/category_detail.html', {'APP_NAME': os.getenv('APP_NAME'), 'notifications': get_all_notifications(),})

def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    category.delete()
    return redirect('my_admin:categories')


@admin_only_login
def delete_all_category(request):
    Category.objects.all().delete()
    return redirect('my_admin:categories')


# ########################################
# Color
# ########################################
@admin_only_login
def all_product_color(request):
    colors = ProductColor.objects.all()
    print(colors)
    color_form = ColorForm()
    return render(request, 'admin_dashboard/color/all.html', {'colors': colors, 'color_form': color_form, 'APP_NAME': os.getenv('APP_NAME'), 'notifications': get_all_notifications(),})


@admin_only_login
def add_color(request):
    if request.method == 'POST':
        color_form = ColorForm(request.POST)

        if color_form.is_valid():
            color = color_form.save()
            return redirect('my_admin:colors')
    else:
        color_form = ColorForm()
    return render(request, 'admin_dashboard/color/all.html', {'color_form': color_form, 'notifications': get_all_notifications(),})


def delete_color(request, color_id):
    color = get_object_or_404(ProductColor, id=color_id)
    color.delete()
    return redirect('my_admin:colors')


@admin_only_login
def delete_all_colors(request):
    ProductColor.objects.all().delete()
    return redirect('my_admin:colors')

# ########################################
# Sub Category
# ########################################


@admin_only_login
def all_sub_category(request):
    sub_categories = SubCategory.objects.all()
    return render(request, "admin_dashboard/sub_category/all.html", {'sub_categories': sub_categories, 'APP_NAME': os.getenv('APP_NAME'), 'notifications': get_all_notifications(),})


@admin_only_login
def sub_category_detail(request, sub_category_id):
    sub_category = SubCategory.objects.get(id=sub_category_id)
    return render(request, "admin_dashboard/sub_category/sub_category_detail.html", {'sub_category': sub_category, 'APP_NAME': os.getenv('APP_NAME'), 'notifications': get_all_notifications(), 'categories': Category.objects.all()})


@admin_only_login
def add_sub_category(request):
    if request.method == 'POST':
        sub_category_form = SubCategoryForm(request.POST)

        if sub_category_form.is_valid():
            sub_category = sub_category_form.save()
            return redirect('my_admin:add_sub_category')
    else:
        sub_category_form = SubCategoryForm()
    return render(request, "admin_dashboard/sub_category/add.html", {'sub_category_form': sub_category_form, 'APP_NAME': os.getenv('APP_NAME'), 'notifications': get_all_notifications(),})


@admin_only_login
def edit_sub_category(request, sub_category_id):
    if request.method == 'POST':
        name = request.POST.get('name')
        category = request.POST.get('category')

        category_matched = Category.objects.get(id=category)

        sub_category = SubCategory.objects.get(id=sub_category_id)

        sub_category.name = name
        sub_category.category = category_matched
        sub_category.save()

        return redirect('my_admin:sub_category_detail', sub_category_id=sub_category.id)

    return render(request, 'admin_dashboard/sub_category/sub_category_detail.html', {'APP_NAME': os.getenv('APP_NAME'), 'notifications': get_all_notifications()})


def delete_sub_category(request, sub_category_id):
    sub_category = get_object_or_404(SubCategory, id=sub_category_id)
    sub_category.delete()
    return redirect('my_admin:sub_categories')


@admin_only_login
def delete_all_sub_category(request):
    SubCategory.objects.all().delete()
    return redirect('my_admin:sub_categories')


# ########################################
# Order
# ########################################
@admin_only_login
def all_order(request):
    orders = Order.objects.all()
    context = {
        'orders': orders,
        'APP_NAME': os.getenv('APP_NAME'),
        'notifications': get_all_notifications(),
    }
    return render(request, 'admin_dashboard/order/all.html', context)


@admin_only_login
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order_items = order.items.all()
    shipping_fee = 3500.00
    APP_NAME = os.getenv('APP_NAME')

    for order_item in order_items:
        order_item.first_image = order_item.product.productimage_set.first()
        order_item.subtotal = order_item.quantity * order_item.product.price

    discount_code = request.session.get('discount_code', None)
    try:
        discount = DiscountCode.objects.get(code=discount_code)
        discount_percentage = discount.percentage
    except DiscountCode.DoesNotExist:
        discount = None

    total_amount = float(
        sum(order_item.subtotal for order_item in order_items))
    total_amount_shipping = int(total_amount) + shipping_fee

    if discount:
        discount_amount = (discount.percentage / 100) * total_amount
        total_amount -= discount_amount
        total_amount_shipping = int(total_amount) + shipping_fee

    context = {
        'order_items': order_items,
        'order': order,
        'total_amount': total_amount,
        'shipping_fee': shipping_fee,
        'total_amount_shipping': total_amount_shipping,
        'APP_NAME': APP_NAME,
        'notifications': get_all_notifications(),
    }
    return render(request, 'admin_dashboard/order/order_detail.html', context)


@admin_only_login
def all_pending_orders(request):
    pending_orders = Order.objects.filter(delivery_status="P")
    return render(request, 'admin_dashboard/order/all_pending_orders.html', {'pending_orders': pending_orders, 'APP_NAME': os.getenv('APP_NAME'), 'notifications': get_all_notifications(),})


@admin_only_login
def all_shipped_orders(request):
    shipped_orders = Order.objects.filter(delivery_status="S")
    return render(request, 'admin_dashboard/order/all_shipped_orders.html', {'shipped_orders': shipped_orders, 'APP_NAME': os.getenv('APP_NAME'), 'notifications': get_all_notifications(),})


@admin_only_login
def all_delivered_orders(request):
    delivered_orders = Order.objects.filter(delivery_status="D")
    return render(request, 'admin_dashboard/order/all_delivered_orders.html', {'delivered_orders': delivered_orders, 'APP_NAME': os.getenv('APP_NAME'), 'notifications': get_all_notifications(),})


@admin_only_login
def all_failed_delivery_orders(request):
    failed_delivered_orders = Order.objects.filter(delivery_status="F")
    return render(request, 'admin_dashboard/order/all_failed_delivered_orders.html', {'failed_delivered_orders': failed_delivered_orders, 'APP_NAME': os.getenv('APP_NAME'), 'notifications': get_all_notifications(),})


@admin_only_login
def mark_order_as_shipped(request, order_id):
    update_order_delivery_status(order_id, 'S')
    return redirect('my_admin:orders')


@admin_only_login
def mark_order_as_delivered(request, order_id):
    update_order_delivery_status(order_id, 'D')
    return redirect('my_admin:orders')


@admin_only_login
def mark_order_as_failed_delivery(request, order_id):
    update_order_delivery_status(order_id, 'F')
    return redirect('order_detail', order_id=order_id)

# ########################################
# Discounts and Coupons
# ########################################


@admin_only_login
def all_coupons(request):
    coupons = DiscountCode.objects.all()
    coupon_form = CouponForm()

    context = {
        'coupons': coupons,
        'coupon_form': coupon_form,
        'APP_NAME': os.getenv('APP_NAME'),
        'notifications': get_all_notifications(),
    }
    return render(request, 'admin_dashboard/coupons/all.html', context)


@admin_only_login
def coupon_detail(request, coupon_id):
    coupon = DiscountCode.objects.get(id=coupon_id)
    return render(request, 'admin_dashboard/coupons/coupon_detail.html', {'coupon': coupon, 'APP_NAME': os.getenv('APP_NAME'), 'notifications': get_all_notifications(),})


@admin_only_login
def create_coupon(request):
    if request.method == 'POST':
        coupon_form = CouponForm(request.POST)
        if coupon_form.is_valid():
            percentage = coupon_form.cleaned_data['percentage']
            number_of_codes = int(coupon_form.cleaned_data['number_of_codes'])

            for _ in range(number_of_codes):
                code = ''.join(random.choices(
                    string.ascii_uppercase + string.digits, k=10))
                valid_from = timezone.now()
                valid_to = valid_from + timedelta(days=365)

                discount_code = DiscountCode(
                    code=code, percentage=percentage, valid_from=valid_from, valid_to=valid_to)
                discount_code.save()

            return redirect(reverse('my_admin:discount_codes'))
    else:
        coupon_form = CouponForm()
    return render(request, 'admin_dashboard/coupons/add.html', {'coupon_form': coupon_form, 'APP_NAME': os.getenv('APP_NAME'), 'notifications': get_all_notifications(),})


def delete_coupon(request, coupon_id):
    coupon = get_object_or_404(DiscountCode, id=coupon_id)
    coupon.delete()
    return redirect('my_admin:discount_codes')


@admin_only_login
def delete_all_coupons(request):
    DiscountCode.objects.all().delete()
    return redirect('my_admin:discount_codes')


# ########################################
# Shipping
# ########################################
@admin_only_login
def all_shipping_address(request):
    shipping_address = ShippingAddress.objects.all()
    return render(request, 'admin_dashboard/shipping/all.html', {'shipping_address': shipping_address, 'APP_NAME': os.getenv('APP_NAME'), 'notifications': get_all_notifications(),})


@admin_only_login
def shipping_detail(request, shipping_id):
    shipping_address = ShippingAddress.objects.get(id=shipping_id)
    return render(request, 'admin_dashboard/shipping/shipping_detail.html', {'shipping_address': shipping_address, 'APP_NAME': os.getenv('APP_NAME'), 'notifications': get_all_notifications(),})


def delete_shipping_address(request, shipping_id):
    shipping_address = get_object_or_404(ShippingAddress, id=shipping_id)
    shipping_address.delete()
    return redirect('my_admin:shipping_addresses')


@admin_only_login
def delete_all_shipping_addresses(request):
    ShippingAddress.objects.all().delete()
    return redirect('my_admin:shipping_addresses')


# ########################################
# Admin Authentication
# ########################################
def admin_login(request):
    try:
        if request.method == 'POST':
            email = request.POST.get('email')
            password = request.POST.get('password')

            user = CustomUser.objects.get(email=email)
            print(user)

            if user.check_password(password):
                login(request, user)
                create_notification(title="Login", notification="You logged in", notification_type="ACTIVITY")
                return redirect(reverse('my_admin:dashboard'))
            else:
                messages.error(request, "Account does not exists")
                return redirect(reverse('my_admin:login'))

    except CustomUser.DoesNotExist:
        messages.error(request, "Account does not exist!")
        return redirect(reverse('my_admin:login'))
    except Exception as e:
        messages.error(request, str(e))
        return redirect(reverse('my_admin:login'))

    return render(request, 'admin_dashboard/login.html', {'APP_NAME': os.getenv('APP_NAME'), 'notifications': get_all_notifications(),})


def admin_logout(request):
    logout(request)
    create_notification(
        title="Logout", notification="You logged out", notification_type="ACTIVITY")
    return redirect(reverse('app:home_page'))

# Error handling
def error404(request, e):
    APP_NAME = os.getenv('APP_NAME')
    context = {
        'APP_NAME': APP_NAME,
    }
    return render(request, '404.html', context)

def error500(request):
    APP_NAME = os.getenv('APP_NAME')
    context = {
        'APP_NAME': APP_NAME,
    }
    return render(request, '500.html', context)
