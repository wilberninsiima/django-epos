from django.shortcuts import reverse
from datetime import datetime
from django.db import models
from django.utils import timezone
from core.models import BaseModel

# Create your models here.

class Category(BaseModel):
    name = models.TextField()
    description = models.TextField(null=True,blank=True)
    color=models.CharField(null=True,blank=True,max_length=100)
    status = models.IntegerField(default=1,choices=[(1,"Active"),(0,"Inactive")]) 
    date_added = models.DateTimeField(default=timezone.now) 
    date_updated = models.DateTimeField(auto_now=True)

    def get_url(self):
        return reverse("category",kwargs={"pk":self.pk})

    def __str__(self):
        return self.name
    class  Meta:
        verbose_name_plural='Categories'

class Product(BaseModel):
    code = models.CharField(max_length=255)
    category = models.ForeignKey(Category,null=True,blank=True, on_delete=models.SET_NULL)
    name = models.TextField()
    unit_measure=models.CharField(null=True,blank=True,max_length=100)
    sku=models.CharField(null=True,blank=True,max_length=100)
    barcode=models.CharField(null=True,blank=True,max_length=100)
    description = models.TextField(null=True,blank=True)
    cost = models.FloatField(null=True,blank=True)
    price = models.FloatField(null=True,default=0,blank=True)
    track_stock=models.BooleanField(default=False)
    in_stock=models.FloatField(null=True,blank=True)
    low_stock_level = models.FloatField(null=True,blank=True,help_text="Notifies the store man when the stock level reaches this limit")
    color=models.CharField(null=True,blank=True,max_length=100)
    shape=models.CharField(null=True,blank=True,max_length=100)
    image=models.ImageField(null=True,blank=True,upload_to="media/products")
    status = models.IntegerField(default=1,choices=[(1,"Active"),(0,"Inactive")]) 
    date_added = models.DateTimeField(default=timezone.now) 
    date_updated = models.DateTimeField(auto_now=True) 

    def __str__(self):
        return self.code + " - " + self.name

    def get_url(self):
        return reverse("product",kwargs={"pk":self.pk})

class Sale(BaseModel):
    code = models.CharField(max_length=100)
    sub_total = models.FloatField(default=0)
    grand_total = models.FloatField(default=0)
    tax_amount = models.FloatField(default=0)
    tax = models.FloatField(default=0)
    tendered_amount = models.FloatField(default=0)
    amount_change = models.FloatField(default=0)
    date_added = models.DateTimeField(default=timezone.now) 
    date_updated = models.DateTimeField(auto_now=True) 

    def __str__(self):
        return self.code
    
    def get_url(self):
        return reverse("sale",kwargs={"pk":self.pk})
    
    def total_items(self):
        return SalesItem.objects.filter(sale=self).count()

class SalesItem(BaseModel):
    sale = models.ForeignKey(Sale,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    price = models.FloatField(default=0)
    qty = models.FloatField(default=0)
    total = models.FloatField(default=0)