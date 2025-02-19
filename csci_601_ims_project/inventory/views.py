from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from .utils import role_required
from django.contrib.auth.decorators import login_required

# Create your views here.
from django.db.models import Q  # For searching
from django.contrib import messages
from .forms import ProductForm, TransactionForm
from .models import Transaction, Product, User


def home(request):
    return render(request, 'inventory/home.html')

@login_required
@role_required(['Admin', 'Manager'])  # Only Admins and Managers can modify product list
def product_list(request):
    products = Product.objects.all()  # Get all products from database
    return render(request, 'inventory/product_list.html', {'products': products})


# Add products   +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def add_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()   # Saves the new product to the database
            return redirect('product_list')   # Redirect to product list after saving
    else:
        form = ProductForm()
    
    return render(request, 'inventory/add_product.html', {'form': form})


# View to update/edit a product   ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def edit_product(request, product_id):
    """
    Fetches the product by ID, displays the existing data in a form, and allows the user to update it.
    """
    product = get_object_or_404(Product, pk=product_id) # Get product or return 404 if not found

    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)   # Pre-fill the form with existing product data
        if form.is_valid():
            form.save()     # Save the updated product
            return redirect('product_list')    # Redirect to product list after saving
    else:
        form = ProductForm(instance=product)    # Load existing product data into the form

    return render(request, 'inventory/edit_product.html', {'form': form, 'product': product})


# View to delete a product   +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def delete_product(request, product_id):
    """
    Fetches the product by ID and deletes it after user confirmation.
    """
    product = get_object_or_404(Product, pk=product_id)  # Get product or return 404 if not found

    if request.method == "POST":
        product.delete()  # Delete the product from the database
        return redirect('product_list')  # Redirect to product list after deletion

    return render(request, 'inventory/delete_product.html', {'product': product})


# View for transaction records  ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
@login_required
@role_required(['Admin', 'Manager'])  #  Only Admins and Managers can record transactions
def record_transaction(request):
    """
    Allows users to record a new transaction (Sale, Purchase, Return).
    Updates inventory stock accordingly.
    """

    if request.method == "POST":
        form = TransactionForm(request.POST)
        if form.is_valid():
            form.save()  # Triggers post_save signal to update stock
            return redirect('transaction_list')    # Redirect to transaction history
    else:
        form = TransactionForm()

    return render(request, 'inventory/record_transaction.html', {'form': form})


# View for transaction Lists  ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def transaction_list(request):
    """
    Displays a list of transactions with filtering and searching.
    """
    transactions = Transaction.objects.all().order_by('-transaction_date')

    # Get filter/search parameters from the request
    transaction_type = request.GET.get('transaction_type')
    product_name = request.GET.get('product_name')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Apply filters
    if transaction_type:
        transactions = transactions.filter(transaction_type=transaction_type)

    if product_name:
        transactions = transactions.filter(product__product_name__icontains=product_name)

    if start_date and end_date:
        transactions = transactions.filter(transaction_date__range=[start_date, end_date])

    return render(request, 'inventory/transaction_list.html', {
        'transactions': transactions,
        'transaction_types': Transaction.TRANSACTION_TYPES,  # Pass filter options
        'products': Product.objects.all(),  # Get all products for dropdown
    })



#  Create User Authentication Views   +++++++++++++++++++++++++++++++++++++++++++
def user_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect('dashboard')  # Redirect to dashboard
        else:
            messages.error(request, "Invalid username or password.") 

    return render(request, 'inventory/login.html')  



# View to create a Dashboard   +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
@login_required
@role_required(['Admin', 'Manager'])  #  Only Admins and Managers can access the dashboard
def dashboard(request):
    total_products = Product.objects.count()
    total_sales = Transaction.objects.filter(transaction_type="Sale").count()
    total_employees = User.objects.exclude(role='Customer').count()
    today_sales = Transaction.objects.filter(transaction_type="Sale").count()
    recent_transactions = Transaction.objects.all().order_by('-transaction_date')[:5]

    return render(request, 'inventory/dashboard.html', {
        'total_products': total_products,
        'total_sales': total_sales,
        'total_employees': total_employees,
        'today_sales': today_sales,
        'recent_transactions': recent_transactions,
    })

# def dashboard(request):
#     """
#     Fetches dashboard data including statistics, stock alerts, and recent transactions.
#     """
#     # total_users = User.objects.count()
#     total_employees = User.objects.exclude(role='Customer').count()
#     total_sales = Transaction.objects.filter(transaction_type="Sale").count()
#     today_sales = Transaction.objects.filter(transaction_type="Sale").count()
#     total_products = Product.objects.count()
#     low_stock_products = Product.objects.filter(stock__lt=5)
#     recent_transactions = Transaction.objects.all().order_by('-transaction_date')[:5]  # Last 5 transactions

#     return render(request, 'inventory/dashboard.html', {
#         # 'total_users': total_users,
#         'total_employees': total_employees,
#         'total_sales': total_sales,
#         'today_sales': today_sales,
#         'total_products': total_products,
#         'low_stock_products': low_stock_products,
#         'recent_transactions': recent_transactions,  # Pass transactions to template
#     })
#    +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('login')
 # User Authentication Views end   ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# Handle Unauthorized Access Gracefully
def unauthorized_access(request, exception):
    return render(request, 'inventory/403.html', status=403)


