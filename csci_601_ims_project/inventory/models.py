from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser

# Create your models here.

# CREATE PRODUCTS MODEL OR ENTITY
class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=50, unique=True)
    category = models.CharField(max_length=50)
    sku = models.CharField(max_length=30, unique=True, blank=True, null=True)  # ✅ Allow blank SKU
    # sku = models.CharField(max_length=30, unique=True)
    barcode = models.CharField(max_length=50, unique=True, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    low_stock_threshold = models.IntegerField(default=5)
    supplier = models.ForeignKey('Supplier', on_delete=models.SET_NULL, null=True, blank=True)
    expiration_date = models.DateField(blank=True, null=True)
    image_url = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.product_name

# CREATE INVENTORY MODEL OR ENTITY
class Inventory(models.Model):
    inventory_id = models.AutoField(primary_key=True)
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    warehouse_location = models.CharField(max_length=100, default='Main Warehouse')
    batch_number = models.CharField(max_length=50, blank=True, null=True)
    last_stock_check = models.DateField(auto_now=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.product_name} - {self.quantity} in stock"
    


# CREATE TRANSACTION MODEL OR ENTITY
class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('Sale', 'Sale'),
        ('Purchase', 'Purchase'),
        ('Return', 'Return'),
        ('Transfer', 'Transfer'),
    ]

    transaction_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, editable=False)  # Auto-calculated
    transaction_by = models.ForeignKey('User', on_delete=models.SET_NULL, null=True)
    batch_number = models.CharField(max_length=50, blank=True, null=True)
    transaction_date = models.DateTimeField(auto_now_add=True)
    source_warehouse = models.CharField(max_length=100, blank=True, null=True)  # Where the product is coming from
    destination_warehouse = models.CharField(max_length=100, blank=True, null=True)  # Where the product is going

    def save(self, *args, **kwargs):
        """ Auto-calculate total cost and update inventory stock. """
        self.total_cost = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.transaction_type} - {self.product.product_name} - {self.quantity}"

# Signal to update stock when a transaction is created
@receiver(post_save, sender=Transaction)
def update_inventory(sender, instance, **kwargs):
    """
    Updates product stock based on the transaction type.
    - Sale: Decrease stock
    - Purchase: Increase stock
    - Return: Increase stock
    - Transfer: Moves stock from one warehouse to another
    """
    product = instance.product
    if instance.transaction_type == "Sale":
        product.stock -= instance.quantity  # Reduce stock on sale
    elif instance.transaction_type in ["Purchase", "Return"]:
        product.stock += instance.quantity  # Increase stock on purchase/return
    elif instance.transaction_type == "Transfer":
        # Transfers do not change total stock but should be recorded per warehouse
        print(f"Transferred {instance.quantity} of {product.product_name} from {instance.source_warehouse} to {instance.destination_warehouse}")

    product.save()


# CREATE USER MODEL OR ENTITY
class User(AbstractUser):  # Inherits from Django's built-in User model
    user_id = models.AutoField(primary_key=True)  # ✅ Explicitly define PK so Django does not add `id`

    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('Manager', 'Manager'),
        ('Staff', 'Staff'),
    ]
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='Staff')
    groups = models.ManyToManyField(
        'auth.Group', related_name='inventory_users', blank=True  # ✅ Fix clash
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission', related_name='inventory_user_permissions', blank=True  # ✅ Fix clash
    )
    
    password = models.CharField(max_length=128, default='pbkdf2_sha256$216000$randomsalt$hashedpassword')  # ✅ Default password
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"  # ✅ Display full name in admin

    


# CREATE SUPPLIER MODEL OR ENTITY
class Supplier(models.Model):
    supplier_id = models.AutoField(primary_key=True)
    supplier_name = models.CharField(max_length=50)
    contact_person = models.CharField(max_length=50, blank=True, null=True)
    phone_number = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    payment_terms = models.CharField(max_length=100, default='Net 30')
    supplier_rating = models.DecimalField(max_digits=2, decimal_places=1, default=3.0)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.supplier_name


# CREATE REPORTS MODEL OR ENTITY
class Report(models.Model):
    REPORT_TYPES = [
        ('Sales Report', 'Sales Report'),
        ('Stock Report', 'Stock Report'),
        ('Supplier Report', 'Supplier Report'),
    ]
    FORMAT_CHOICES = [
        ('CSV', 'CSV'),
        ('PDF', 'PDF'),
        ('Excel', 'Excel'),
    ]

    report_id = models.AutoField(primary_key=True)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES)
    data_range_start = models.DateField(blank=True, null=True)
    data_range_end = models.DateField(blank=True, null=True)
    generated_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.report_type} ({self.format}) - {self.generated_date}"


# CREATE REPORT_INVENTORY RELATIONSHIOP MODEL OR ENTITY
class ReportInventory(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE)


# CREATE REPORT_TRANSACTION RELATIONSHIOP MODEL OR ENTITY
class ReportTransaction(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)




