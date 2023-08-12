from django.shortcuts import render, redirect, reverse
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from .decorators import admin_only_login
from users.models import CustomUser
from django.contrib.auth import login, logout, authenticate
from glamourApp.models import *
from .utils import update_order_delivery_status, update_user_status, get_products_with_images, send_message
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .forms import CategoryForm, CouponForm, SubCategoryForm, SizeForm
import string
import random
from django.utils import timezone
from datetime import timedelta
import calendar

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
    total_order_yesterday = orders_yesterday.filter(delivery_status="P").count()
    percentage_change = 0
    if total_order_yesterday == 0:
        percentage_change = 100.0
    else:
        percentage_change = ((total_order_today - total_order_yesterday) / total_order_yesterday) * 100

    # Using these to perform some logic
    first_day = timezone.datetime(current_year, current_month, 1)
    last_day = timezone.datetime(current_year, current_month, calendar.monthrange(current_year, current_month)[1])

    # Get orders from this month
    filtered_monthly_orders = orders.filter(created_at__range=(first_day, last_day))
    # Get users that joined this month
    filtered_monthly_users_joined = users.filter(date_joined__range=(first_day, last_day)).count()

    # Get users that joined last month
    last_month = current_month - 1 if current_month > 1 else 12
    last_year = current_year if current_month > 1 else current_year - 1
    last_month_first_day = timezone.datetime(last_year, last_month, 1)
    last_month_last_day = timezone.datetime(last_year, last_month, calendar.monthrange(last_year, last_month)[1])
    filtered_last_month_users_joined = users.filter(date_joined__range=(last_month_first_day, last_month_last_day)).count()
    filtered_last_month_orders = orders.filter(created_at__range=(last_month_first_day, last_month_last_day))
    filtered_this_month_orders = orders.filter(created_at__range=(first_day, timezone.now()))

    percentage_change_users = 0
    if filtered_last_month_users_joined == 0:
        percentage_change_users = 100.0
    else:
        percentage_change_users = ((filtered_monthly_users_joined - filtered_last_month_users_joined) / filtered_last_month_users_joined) * 100

    # Get orders from last year
    last_year_first_day = timezone.datetime(current_year - 1, 1, 1)
    last_year_last_day = timezone.datetime(current_year - 1, 12, 31)
    filtered_last_year_orders = orders.filter(created_at__range=(last_year_first_day, last_year_last_day))

    percentage_change_users = 0
    if filtered_last_month_users_joined == 0:
        percentage_change_users = 100.0
    else:
        percentage_change_users = ((filtered_monthly_users_joined - filtered_last_month_users_joined) / filtered_last_month_users_joined) * 100

    total_orders = orders.count()
    percentage_change_orders_year = 0
    total_orders_last_year = filtered_last_year_orders.count()
    if total_orders_last_year == 0:
        percentage_change_orders_year = 100.0
    else:
        percentage_change_orders_year = ((total_orders - total_orders_last_year) / total_orders_last_year) * 100

    total_pending_orders = orders.filter(delivery_status="P").count()
    total_income = sum(order.total_price for order in filtered_monthly_orders)
    total_income_last_month = sum(order.total_price for order in filtered_last_month_orders)
    total_income_this_month = sum(order.total_price for order in filtered_this_month_orders)

    percentage_change_income = 0
    if total_income_last_month == 0:
        percentage_change_income = 100.0
    else:
        percentage_change_income = ((total_income - total_income_last_month) / total_income_last_month) * 100

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
    }
    return render(request, 'admin_dashboard/index.html', context)

# ########################################
# User
# ########################################
@admin_only_login
@staff_member_required
def all_user(request):
    users = CustomUser.objects.all()
    return render(request, 'admin_dashboard/user/all.html', {'users': users})

@admin_only_login
@staff_member_required
def user_detail(request, user_id):
    user = CustomUser.objects.get(id=user_id)
    return render(request, 'admin_dashboard/user/user_detail.html', {'user': user})

@admin_only_login
@staff_member_required
def mark_user_as_active(request, user_id):
    update_user_status(user_id, True)
    return redirect('user_detail', user_id=user_id)

@admin_only_login
@staff_member_required
def mark_user_as_suspended(request, user_id):
    update_user_status(user_id, False)
    return redirect('user_detail', user_id=user_id)

# ########################################
# Product
# ########################################
@admin_only_login
def all_products(request):
    products = Product.objects.all()
    paginator = Paginator(products, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    products_with_images = get_products_with_images(products)

    context = {
        'products': products_with_images,
        'page_obj': page_obj,
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
        'price_with_increase': price_with_increase
    }

    return render(request, 'admin_dashboard/product/product_detail.html', context)

@admin_only_login
def add_product(request):
    sub_categories = SubCategory.objects.all()
    categories = Category.objects.all()
    sizes = ProductSize.objects.all()

    if request.method == 'POST':
        name = request.POST.get('name')
        sub_category = request.POST.get('sub_category')
        description = request.POST.get('description')
        price = request.POST.get('price')
        category = request.POST.get('category')
        sizes = [x.name for x in ProductSize.objects.all()]
        size_ids = []
        for x in sizes:
            size_ids.append(request.POST.get(x))
        print(size_ids)
    else:
        return render(request, 'admin_dashboard/product/add.html')

    context = {
        'sub_categories': sub_categories,
        'categories': categories,
        'sizes': sizes
    }
    return render(request, 'admin_dashboard/product/add.html', context)

# ########################################
# Category
# ########################################
@admin_only_login
def all_category(request):
    categories = Category.objects.all()
    return render(request, 'admin_dashboard/category/all.html', {'categories': categories})

@admin_only_login
def category_detail(request, category_id):
    category = Category.objects.get(id=category_id)
    return render(request, 'admin_dashboard/category/category_detail.html', {'category': category})

@admin_only_login
def add_category(request):
    if request.method == 'POST':
        category_form = CategoryForm(request.POST)

        if category_form.is_valid():
            category = category_form.save()
            return redirect('my_admin:category_detail', category_id=category.id)
    else:
        category_form = CategoryForm()
    return render(request, 'admin_dashboard/category/add.html', {'category_form': category_form})


# ########################################
# Sub Category
# ########################################
@admin_only_login
@staff_member_required()
def all_sub_category(request):
    sub_categories = SubCategory.objects.all()
    return render(request, "admin_dashboard/sub_category/all.html", {'sub_categories': sub_categories})

@admin_only_login
@staff_member_required()
def sub_category_detail(request, sub_category_id):
    sub_category = SubCategory.objects.get(id=sub_category_id)
    return render(request, "admin_dashboard/sub_category/sub_category_detail.html", {'sub_category': sub_category})

@admin_only_login
@staff_member_required()
def add_sub_category(request):
    if request.method == 'POST':
        sub_category_form = SubCategoryForm(request.POST)

        if sub_category_form.is_valid():
            sub_category = sub_category_form.save()
            return redirect('my_admin:sub_category_detail', sub_category_id=sub_category.id)
    else:
        sub_category_form = SubCategoryForm()
    return render(request, "admin_dashboard/sub_category/add.html", {'sub_category_form': sub_category_form})


# ########################################
# Sizes
# ########################################
@admin_only_login
@staff_member_required()
def all_sizes(request):
    sizes = ProductSize.objects.all()
    return render(request, "admin_dashboard/size/all.html", {'sizes': sizes})

@admin_only_login
@staff_member_required()
def size_detail(request, size_id):
    size = ProductSize.objects.get(id=size_id)
    return render(request, "admin_dashboard/size/size_detail.html", {'size': size})

@admin_only_login
@staff_member_required()
def add_size(request):
    if request.method == 'POST':
        size_form = SizeForm(request.POST)

        if size_form.is_valid():
            size = size_form.save()
            return redirect('my_admin:size_detail', size_id=size.id)
    else:
        size_form = SizeForm()
    return render(request, "admin_dashboard/size/add.html", {'size_form': size_form})


# ########################################
# Order
# ########################################
@admin_only_login
@staff_member_required
def all_order(request):
    orders = Order.objects.all()
    context = {
        'orders': orders
    }
    return render(request, 'admin_dashboard/order/all.html', context)

@admin_only_login
@staff_member_required
def order_detail(request, order_id):
    order = Order.objects.get(id=order_id)
    context = {
        'order': order
    }
    return render(request, 'admin_dashboard/order/order_detail.html', context)

@admin_only_login
@staff_member_required
def all_pending_orders(request):
    pending_orders = Order.objects.filter(delivery_status="P")
    return render(request, 'admin_dashboard/order/all_pending_orders.html', {'pending_orders': pending_orders})

@admin_only_login
@staff_member_required
def all_shipped_orders(request):
    shipped_orders = Order.objects.filter(delivery_status="S")
    return render(request, 'admin_dashboard/order/all_shipped_orders.html', {'shipped_orders': shipped_orders})

@admin_only_login
@staff_member_required
def all_delivered_orders(request):
    delivered_orders = Order.objects.filter(delivery_status="D")
    return render(request, 'admin_dashboard/order/all_delivered_orders.html', {'delivered_orders': delivered_orders})

@admin_only_login
@staff_member_required
def all_failed_delivery_orders(request):
    failed_delivered_orders = Order.objects.filter(delivery_status="F")
    return render(request, 'admin_dashboard/order/all_failed_delivered_orders.html', {'failed_delivered_orders': failed_delivered_orders})

@admin_only_login
@staff_member_required
def mark_order_as_shipped(request, order_id):
    update_order_delivery_status(order_id, 'S')
    return redirect('order_detail', order_id=order_id)

@admin_only_login
@staff_member_required
def mark_order_as_delivered(request, order_id):
    update_order_delivery_status(order_id, 'D')
    return redirect('order_detail', order_id=order_id)

@admin_only_login
@staff_member_required
def mark_order_as_failed_delivery(request, order_id):
    update_order_delivery_status(order_id, 'F')
    return redirect('order_detail', order_id=order_id)

# ########################################
# Discounts and Coupons
# ########################################
@admin_only_login
def all_coupons(request):
    coupons = DiscountCode.objects.all()
    return render(request, 'admin_dashboard/coupons/all.html', {'coupons': coupons})

@admin_only_login
def coupon_detail(request, coupon_id):
    coupon = DiscountCode.objects.get(id=coupon_id)
    return render(request, 'admin_dashboard/coupons/coupon_detail.html', {'coupon': coupon})

@admin_only_login
def create_coupon(request):
    if request.method == 'POST':
        coupon_form = CouponForm(request.POST)
        if coupon_form.is_valid():
            percentage = request.cleaned_data('percentage')
            number_of_codes = int(request.cleaned_data('number_of_codes'))

            for _ in range(number_of_codes):
                code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
                valid_from = timezone.now()
                valid_to = valid_from + timedelta(days=365)

                discount_code = DiscountCode(code=code, percentage=percentage, valid_from=valid_from, valid_to=valid_to)
                discount_code.save()

            return redirect(reverse('my_admin:discount_codes'))
    else:
        coupon_form = CouponForm()
    return render(request, 'admin_dashboard/coupons/add.html', {'coupon_form': coupon_form})

# ########################################
# Shipping
# ########################################
@admin_only_login
@staff_member_required
def all_shipping_address(request):
    shipping_address = ShippingAddress.objects.all()
    return render(request, 'admin_dashboard/shipping/all.html', {'shipping_address': shipping_address})

@admin_only_login
@staff_member_required
def shipping_detail(request, shipping_id):
    shipping_address = ShippingAddress.objects.get(id=shipping_id)
    return render(request, 'admin_dashboard/shipping/shipping_detail.html', {'shipping_address': shipping_address})

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
                return redirect(reverse('my_admin:dashboard'))
            else:
                messages.error(request, "Account does not exists")
                return redirect(reverse('my_admin:login'))

    except Exception as e:
        messages.error(request, str(e))
        return redirect(reverse('my_admin:login'))
    except CustomUser.DoesNotExist:
        messages.error(request, "Account does not exist!")
        return redirect(reverse('my_admin:login'))

    return render(request, 'admin_dashboard/login.html')

def admin_logout(request):
    logout(request)
    return redirect(reverse('app:home_page'))