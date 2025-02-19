from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

# Register your models here.

from .models import Product, Inventory, Transaction, User, Supplier, Report

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'category', 'price', 'stock', 'supplier', 'date_created')
    search_fields = ('product_name', 'category', 'sku')
    list_filter = ('category', 'supplier')

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'warehouse_location', 'last_stock_check')
    search_fields = ('product__product_name', 'warehouse_location')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_type', 'product', 'quantity', 'transaction_date', 'transaction_by')
    list_filter = ('transaction_type', 'transaction_date')

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('supplier_name', 'contact_person', 'phone_number', 'email')
    search_fields = ('supplier_name', 'phone_number')

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('report_type', 'generated_by', 'format', 'generated_date')
    list_filter = ('report_type', 'format', 'generated_date')

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email', 'role', 'is_staff', 'is_active')  # ✅ Show first & last name
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')  # ✅ Make first & last name searchable
    ordering = ('username',)

    # ✅ Avoid duplicate fields by modifying only 'fieldsets' and not duplicating default fields
    fieldsets = (
        ('User Information', {'fields': ('username', 'password')}),
        ('Personal Information', {'fields': ('first_name', 'last_name', 'email', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )

admin.site.register(User, CustomUserAdmin)  # ✅ Register the updated admin panel



# class CustomUserAdmin(UserAdmin):
#     list_display = ('username', 'first_name', 'last_name', 'email', 'role', 'is_staff', 'is_active')  # ✅ Show first & last name
#     list_filter = ('role', 'is_staff', 'is_active')
#     search_fields = ('username', 'email', 'first_name', 'last_name')  # ✅ Make first & last name searchable
#     ordering = ('username',)
#     # ordering = ('date_joined',)
#     fieldsets = UserAdmin.fieldsets + (  # ✅ Add first_name & last_name to edit form
#         ('Personal Information', {'fields': ('first_name', 'last_name', 'role')}),
#     )


# admin.site.register(User, CustomUserAdmin)

# @admin.register(User)
# class UserAdmin(admin.ModelAdmin):
#     list_display = ('username', 'email', 'role', 'date_joined')
#     search_fields = ('username', 'email')
#     list_filter = ('role',)