from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse, JsonResponse
from .models import *
import json
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from .models import ShoppingAddress
# Create your views here.

def product(request):
    return render(request, 'app/product.html')

def payment(request):
    user = request.user
    checkout_data = request.session.get('checkout_data')
    message = None

    if request.user.is_authenticated:
        order, created = Order.objects.get_or_create(customer=user, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0}
        cartItems = order['get_cart_items']

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        if request.user.is_authenticated:
            order.complete = True
            order.save()
            message = "Cảm ơn bạn đã quan tâm và sử dụng website chúng tôi để đặt hàng. Mong rằng bạn sẽ có một trải nghiệm tốt khi sử dụng website của chúng tôi. Xin chân thành cảm ơn."
        else:
            message = "Vui lòng đăng nhập để hoàn tất thanh toán."
       
    return render(request, 'app/payment.html', {
        'checkout_data': checkout_data,
        'items': items,
        'order': order,
        'cartItems': cartItems,
        'message': message,
    })

def introduce(request):
    context = {}
    return render(request, 'app/introduce.html', context)

def detail(request, id):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0}
        cartItems = order['get_cart_items']

    product = get_object_or_404(Product, id=id)
    categories = Category.objects.filter(is_sub=False)

    # ✅ Lấy các category của sản phẩm
    product_categories = product.category.all()

    # ✅ Lấy các sản phẩm liên quan từ các category đó
    related_products = Product.objects.filter(
        category__in=product_categories
    ).exclude(id=product.id).distinct()[:4]

    context = {
        'items': items,
        'order': order,
        'cartItems': cartItems,
        'categories': categories,
        'products': [product],  # dùng trong for loop
        'related_products': related_products,  # nếu bạn dùng để gợi ý
    }
    return render(request, 'app/detail.html', context)

def category(request):
    categories = Category.objects.filter(is_sub=False)
    active_category = request.GET.get('category', '')
    category_obj = None
    products = []

    if active_category:
        category_obj = get_object_or_404(Category, slug=active_category)
        products = Product.objects.filter(category=category_obj)

    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0}
        cartItems = order['get_cart_items']

    context = {'categories': categories,'products': products,'active_category': active_category,'category_obj': category_obj,'cartItems': cartItems}
    return render(request, 'app/category.html', context)

import random
from django.shortcuts import render
from .models import Product, Category, Order

def home(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0}
        cartItems = order['get_cart_items']

    categories = Category.objects.filter(is_sub=False)
    active_category = request.GET.get('category', '')
    products = Product.objects.all()

    # === Flash Sale Random Products ===
    flash_sale_products = list(products)  # convert QuerySet to list
    random.shuffle(flash_sale_products)   # trộn ngẫu nhiên
    flash_sale_products = flash_sale_products[:6]  # chọn 6 sản phẩm

    # Gán ngẫu nhiên phần trăm giảm giá và tính giá sau giảm
    for product in flash_sale_products:
        product.discount_percent = random.choice([10, 15, 20, 25, 30])  # ví dụ ngẫu nhiên %
        product.sale_price = int(product.price * (100 - product.discount_percent) / 100)

    context = {
        'products': products,
        'flash_sale_products': flash_sale_products,
        'cartItems': cartItems,
        'categories': categories,
        'active_category': active_category,
    }
    return render(request, 'app/home.html', context)



def search(request):
    searched = ""
    keys = []
    if request.method == 'POST':
        # searched = request.POST['searched']
        # keys = Product.objects.filter(name__icontains=searched)
        searched = request.POST['searched'].strip().lower()  # Chuyển tất cả về chữ thường
        keys = Product.objects.filter(name__icontains=searched)  # Lọc sản phẩm với từ khóa không phân biệt hoa thường
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0}
        cartItems = order['get_cart_items']
    categories = Category.objects.filter(is_sub =False)
    products = Product.objects.all()
    return render(request,'app/search.html',{'searched':searched,'keys':keys,'products': products,'cartItems':cartItems,'categories':categories})

def register(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    context= {'form':form}
    return render(request,'app/register.html',context)

def loginPage(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, 'Tên người dùng hoặc mật khẩu không chính xác!')
    
    return render(request, 'app/login.html')

def logoutPage(request):
    logout(request)
    return redirect('login')

def cart(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0}  # Tránh lỗi khi truy cập các thuộc tính trong template
        cartItems = order['get_cart_items']
    categories = Category.objects.filter(is_sub =False)
    context = {'items':items,'order':order,'cartItems':cartItems,'categories':categories}
    return render(request, 'app/cart.html', context)

def checkout(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0}
        cartItems = order['get_cart_items']

    if request.method == 'POST':
        # Lấy thông tin từ form
        name = request.POST.get('name')
        email = request.POST.get('email')
        address = request.POST.get('address')
        number = request.POST.get('number')

        # Kiểm tra thông tin đã đầy đủ chưa
        if not name or not email or not address or not number:
            messages.error(request, 'Bạn chưa điền đủ thông tin. Vui lòng kiểm tra lại.')
            return redirect('checkout')  # Trả về trang checkout nếu thiếu thông tin

        # Lưu thông tin form vào session
        request.session['checkout_data'] = {
            'name': name,
            'email': email,
            'address': address,
            'number': number,
        }
        return redirect('payment')

    categories = Category.objects.filter(is_sub=False)
    context = {'items': items, 'order': order, 'cartItems': cartItems, 'categories': categories}
    return render(request, 'app/checkout.html', context)

def updateItem(request):
    data = json.loads(request.body)
    productId = data.get('productId')
    action = data.get('action')

    try:
        product = Product.objects.get(id=productId)
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)

    customer = request.user
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity += 1
    elif action == 'remove':
        orderItem.quantity -= 1

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    # Trả về phản hồi JSON với thông tin mới
    response_data = {
        'cartItems': order.get_cart_items,
        'cartTotal': order.get_cart_total,
    }
    return JsonResponse(response_data)


