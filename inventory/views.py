from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .models import Product, Sale
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
@login_required
def dashboard(request):
    total_products = Product.objects.count()
    available_stock = sum(product.quantity for product in Product.objects.all())
    low_stock = Product.objects.filter(quantity__lt=10).count()
    low_stock_products = Product.objects.filter(quantity__lt=10)
    total_sales = sum(sale.total_price for sale in Sale.objects.all())
    
    sales = Sale.objects.all().order_by('-id')
    return render(request, 'inventory/dashboard.html', {
    'total_products': total_products,
    'available_stock': available_stock,
    'low_stock': low_stock,
    'total_sales': total_sales,
    'sales': sales,
    'low_stock_products': low_stock_products,
})
@login_required
def add_product(request):
    if request.method == 'POST':
        name = request.POST['name']
        category = request.POST['category']
        price = request.POST['price']
        quantity = request.POST['quantity']
        supplier = request.POST['supplier']

        Product.objects.create(
            name=name,
            category=category,
            price=price,
            quantity=quantity,
            supplier=supplier
        )

        return redirect('dashboard')

    return render(request, 'inventory/add_product.html')
@login_required
def products(request):
    search = request.GET.get('search')

    if search:
        all_products = Product.objects.filter(name__icontains=search)
    else:
        all_products = Product.objects.all()

    return render(request, 'inventory/products.html', {
        'products': all_products
    })
@login_required
def edit_product(request, id):
    product = Product.objects.get(id=id)
    if request.method == 'POST':
        product.name = request.POST['name']
        product.category = request.POST['category']
        product.price = request.POST['price']
        product.quantity = request.POST['quantity']
        product.supplier = request.POST['supplier']

        product.save()

        return redirect('products')

    return render(request, 'inventory/edit_product.html', {
        'product': product
    }) 
@login_required   
def delete_product(request, id):
    product = Product.objects.get(id=id)
    product.delete()
    return redirect('products')
@login_required
def suppliers(request):
    all_products = Product.objects.all()
    return render(request, 'inventory/suppliers.html', {
        'products': all_products
    })
@login_required
def reports(request):
    all_products = Product.objects.all()

    total_products = Product.objects.count()
    total_stock = sum(product.quantity for product in all_products)
    low_stock = Product.objects.filter(quantity__lt=10).count()
    inventory_value = sum(
        product.price * product.quantity
        for product in all_products
    )

    return render(request, 'inventory/reports.html', {
        'products': all_products,
        'total_products': total_products,
        'total_stock': total_stock,
        'low_stock': low_stock,
        'inventory_value': inventory_value,
    })
@login_required
def add_sale(request):
    products = Product.objects.all()

    if request.method == 'POST':
        product = Product.objects.get(id=request.POST['product'])
        quantity = int(request.POST['quantity'])

        if quantity > product.quantity:
            return render(request, 'inventory/add_sale.html', {
                'products': products,
                'error': 'Not enough stock available!'
            })

        total_price = product.price * quantity

        Sale.objects.create(
            product=product,
            quantity=quantity,
            total_price=total_price
        )

        product.quantity -= quantity
        product.save()

        return redirect('dashboard')

    return render(request, 'inventory/add_sale.html', {
        'products': products
    })
@login_required
def sales_history(request):
    sales = Sale.objects.all().order_by('-id')

    return render(request, 'inventory/sales_history.html', {
        'sales': sales
    })
def product_detail(request, id):
    product = Product.objects.get(id=id)

    return render(request, 'inventory/product_detail.html', {
        'product': product
    })
def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'inventory/login.html', {
                'error': 'Invalid username or password'
            })



    return render(request, 'inventory/login.html')
def user_logout(request):
    logout(request)
    return redirect('login')
def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        from django.contrib.auth.models import User
        if User.objects.filter(username=username).exists():
            return render(request, 'inventory/register.html', {
                'error': 'Username already exists'
            })

        User.objects.create_user(
            username=username,
            password=password
        )

        return redirect('login')

    return render(request, 'inventory/register.html')
@login_required    
def profile(request):
    return render(request, 'inventory/profile.html')
@login_required
def edit_profile(request):
    if request.method == 'POST':
        request.user.email = request.POST['email']
        request.user.save()
        return redirect('profile')

    return render(request, 'inventory/edit_profile.html')
@login_required
def change_password(request):
    from django.contrib.auth import authenticate
    from django.contrib.auth import update_session_auth_hash

    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = authenticate(
            username=request.user.username,
            password=current_password
        )

        if user is None:
            return render(request, 'inventory/change_password.html', {
                'error': 'Current password is incorrect.'
            })

        if new_password != confirm_password:
            return render(request, 'inventory/change_password.html', {
                'error': 'New passwords do not match.'
            })

        request.user.set_password(new_password)
        request.user.save()

        update_session_auth_hash(request, request.user)

        return redirect('profile')

    return render(request, 'inventory/change_password.html')
@login_required
def settings(request):
    return render(request, 'inventory/settings.html')
@login_required
def stock_prediction(request):
    products = Product.objects.all()

    predictions = []

    for product in products:
        sales = Sale.objects.filter(
            product=product,
            sale_date__gte=timezone.now() - timedelta(days=30)
        )

        total_sold = sales.aggregate(
            total=Sum('quantity')
        )['total'] or 0

        average_daily_sales = total_sold / 30

        if average_daily_sales > 0:
            days_left = product.quantity / average_daily_sales
        else:
            days_left = None

        predictions.append({
            'product': product,
            'total_sold': total_sold,
            'average_daily_sales': round(average_daily_sales, 2),
            'days_left': round(days_left, 1) if days_left is not None else None,
        })

    return render(
        request,
        'inventory/stock_prediction.html',
        {'predictions': predictions}
    )
@login_required
def inventory_health(request):
    products = Product.objects.all()

    total_products = products.count()
    low_stock_products = products.filter(quantity__lt=10).count()
    out_of_stock_products = products.filter(quantity=0).count()

    if total_products > 0:
        health_score = 100

        health_score -= (low_stock_products / total_products) * 30
        health_score -= (out_of_stock_products / total_products) * 40

        health_score = max(0, round(health_score))
    else:
        health_score = 0

    return render(
        request,
        'inventory/inventory_health.html',
        {
            'health_score': health_score,
            'total_products': total_products,
            'low_stock_products': low_stock_products,
            'out_of_stock_products': out_of_stock_products,
        }
    )
@login_required
def dead_stock(request):
    products = Product.objects.all()

    dead_products = []

    for product in products:
        recent_sales = Sale.objects.filter(
            product=product,
            sale_date__gte=timezone.now() - timedelta(days=30)
        ).exists()

        if not recent_sales and product.quantity > 0:
            dead_products.append(product)

    return render(
        request,
        'inventory/dead_stock.html',
        {
            'dead_products': dead_products,
        }
    )
@login_required
def restock_suggestions(request):
    products = Product.objects.all()

    suggestions = []

    for product in products:
        sales = Sale.objects.filter(
            product=product,
            sale_date__gte=timezone.now() - timedelta(days=30)
        )

        total_sold = sales.aggregate(
            total=Sum('quantity')
        )['total'] or 0

        average_daily_sales = total_sold / 30

        if average_daily_sales > 0:
            estimated_days_left = product.quantity / average_daily_sales
        else:
            estimated_days_left = None

        if estimated_days_left is not None and estimated_days_left <= 10:
            suggestions.append({
                'product': product,
                'total_sold': total_sold,
                'average_daily_sales': round(average_daily_sales, 2),
                'estimated_days_left': round(estimated_days_left, 1),
            })

    return render(
        request,
        'inventory/restock_suggestions.html',
        {
            'suggestions': suggestions,
        }
    )
@login_required
def activity_timeline(request):
    sales = Sale.objects.all().order_by('-sale_date')[:20]

    return render(
        request,
        'inventory/activity_timeline.html',
        {
            'sales': sales,
        }
    )