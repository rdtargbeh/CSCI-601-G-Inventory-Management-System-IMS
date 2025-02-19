# Creates a form based on the Product model.
from django import forms

from .models import Product
from .models import Transaction

# Add Product Form
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_name', 'category', 'sku', 'price', 'stock', 'supplier', 'description']

# Add Transaction Form
class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['product', 'transaction_type', 'quantity', 'unit_price', 'source_warehouse', 'destination_warehouse']

    def clean(self):
        cleaned_data = super().clean()
        transaction_type = cleaned_data.get("transaction_type")

        # Ensure warehouses are selected for transfers
        if transaction_type == "Transfer":
            if not cleaned_data.get("source_warehouse") or not cleaned_data.get("destination_warehouse"):
                raise forms.ValidationError("Both source and destination warehouses must be specified for a transfer.")

        return cleaned_data
