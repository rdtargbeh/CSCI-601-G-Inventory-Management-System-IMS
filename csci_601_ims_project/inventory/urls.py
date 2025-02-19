

from django.contrib import admin
from django.urls import path, include
from inventory.views import unauthorized_access  # ✅ Import the 403 error view

from . import views

urlpatterns = [
    # path('admin/', admin.site.urls),
    # path('', include('inventory.urls')),  # ✅ Include the app's URLs
    # path('', views.home, name='home'),  # Home Page
    path('products/', views.product_list, name='product_list'),  # Product List Page
    path('products/add/', views.add_product, name='add_product'),  # New URL for adding products
    path('products/edit/<int:product_id>/', views.edit_product, name='edit_product'),  # Edit product URL
    path('products/delete/<int:product_id>/', views.delete_product, name='delete_product'),  # Delete product URL
    path('transactions/add/', views.record_transaction, name='record_transaction'),
    path('transactions/', views.transaction_list, name='transaction_list'),  # Transaction history page
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
]


# handler403 = 'inventory.views.unauthorized_access'