from django.views import View
from pickle import FALSE
from django.shortcuts import redirect, render,HttpResponse
from django.http import HttpResponse
from pos.models import Category, Product, Sale, SalesItem
from django.db.models import Count, Sum
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
import json, sys
from datetime import date, datetime
from django.contrib.auth.mixins import LoginRequiredMixin,PermissionRequiredMixin
from users.models import User
# Create your views here.
class HomeView(LoginRequiredMixin,View):
    def get(self,request):
        users=User.objects.filter(is_active=True) if request.user.has_perm('users.view_user') else []
        context = {
            'page_title':'Home',
            'users' : users,
        }
        return render(request, 'home.html',context)


class StatsView(LoginRequiredMixin,View):
    def get(self,request):
        context={}
        stats={}
        graphs={}
        now = datetime.now()
        current_year = now.strftime("%Y")
        current_month = now.strftime("%m")
        current_day = now.strftime("%d")
        
        user=request.GET.get("user",request.user if not request.user.has_perm('users.view_user') else None)
        date_selected=request.GET.get("date",date.today())
        if not date_selected:date_selected=date.today()
        categories = Category.objects.filter()
        products = Product.objects.all()
        if request.GET.get('date',None):
            products=products.filter(created_at__date=date_selected)
        stats['categories']={'value':categories.count(),'title':'Categories','icon':'list','desc':'Total Categories','card_class':'info-card--success'}
        stats['products']={'value':products.count(),'title':'Products','icon':'label','desc':'Total Products','card_class':'info-card--primary'}
        # sales=Sale.objects.filter(date_added__year=current_year,date_added__month = current_month,date_added__day = current_day).all()
        sales=Sale.objects.filter(date_added__date=date_selected).all()
        if user:
            sales=sales.filter(created_by=user)
        total_sales = sum(sales.values_list('grand_total',flat=True))

        # products=Product.objects.filter()
        productSales=[]
        for product in products:
            product_sales=sum(sales.filter(salesitem__product=product).values_list('grand_total',flat=True))
            productSales.append({"name":product.name,"total_sales":product_sales})
        
        productCategorySales=[]
        for cat in categories:
            product_sales=sum(sales.filter(salesitem__product__category=cat).values_list('grand_total',flat=True))
            productCategorySales.append({"name":cat.name,"total_sales":product_sales})
        

        graphs['product_sales']={"title":"Product Sales","key":"product_sales","type":"bar","class_width":"6","labels":{"label":"name","value":"total_sales"},"data":productSales}
        graphs['product_category_sales']={"title":"Sales Per Category","key":"product_category_sales","type":"bar","class_width":"6","labels":{"label":"name","value":"total_sales"},"data":productCategorySales}
        

        stats['transactions']={'value':sales.count(),'title':'Transactions','icon':'receipt','desc':'Today`s transactions','card_class':'info-card--info'}
        stats['sales']={'value':total_sales,'title':'Sales','icon':'attach_money','desc':'Today`s sales','card_class':'info-card--success'}
        context = {
            'categories' : categories,
            'products' : products,
            'transaction' : sales.count(),
            'total_sales' : total_sales,
            'stats':stats,
            'graphs':graphs,
        }
        return render(request, 'core/partials/stats.html',context)