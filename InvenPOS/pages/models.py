from django.db import models
from django.utils import timezone

class Product(models.Model):
    product_name = models.CharField(max_length=100)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    product_quantity = models.IntegerField(default=0)
    product_category = models.CharField(max_length=50)
    product_img = models.ImageField(upload_to='products/', blank=True, null=True)

    def __str__(self):
        return self.product_name

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    

class Supplier(models.Model):
    name = models.CharField(max_length=100)
    contact = models.CharField(max_length=20)
    email = models.EmailField()
    address = models.TextField()
    company = models.CharField(max_length=100, blank=True, null=True)  # ✅ Add this
    is_active = models.BooleanField(default=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    

class Restock(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    supplier = models.ForeignKey('Supplier', on_delete=models.SET_NULL, null=True, blank=True)
    quantity_added = models.PositiveIntegerField(default=0)
    date_restocked = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.product.product_name} - {self.quantity_added} added"