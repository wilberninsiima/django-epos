from django.contrib import admin
from .models import Category, Product, Sale, SalesItem

# Register your models here.
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Sale)
admin.site.register(SalesItem)
# admin.site.register(Employees)