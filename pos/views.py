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
from .forms import ProductCategoryForm,ProductForm
from .filters import *
from django.contrib.auth.mixins import LoginRequiredMixin,PermissionRequiredMixin

# Create your views here.
class CategoriesView(PermissionRequiredMixin,View):
    permission_required=['pos.view_category']
    template_name="pos/categories.html"
    def get(self,request):
        context={}
        action=request.GET.get("action",None)
        if action=="get-form":
            context['form']=ProductCategoryForm()
            return render(request, 'pos/partials/category-form.html',context)
        category_list = Category.objects.all()
        # category_list = {}
        context = {
            'page_title':'Category List',
            'list':category_list,
        }
        if request.htmx:
            self.template_name='pos/partials/categories-list.html'
        return render(request, self.template_name,context)
    def post(self,request):
        form=ProductCategoryForm(request.POST)
        context = {'form':form}
        if form.is_valid():
            form.save()
            return HttpResponse(status=204,headers={'HX-Trigger':'listChanged'})
        else:
            return render(request, 'pos/partials/category-form.html',context)

class CategoryView(LoginRequiredMixin,View):
    form_class=ProductCategoryForm
    def get(self,request,pk):
        category=Category.objects.get(pk=pk)
        context={'category':category}
        context['form']=self.form_class(instance=category)
        return render(request, 'pos/partials/category-form.html',context)
    def post(self,request,pk):
        category=Category.objects.get(pk=pk)
        form=self.form_class(request.POST,instance=category)
        context = {'form':form}
        if form.is_valid():
            form.save()
            return HttpResponse(status=204,headers={'HX-Trigger':'listChanged'})
        else:
            return render(request, 'pos/partials/category-form.html',context)
    def delete(self,request,pk):
        category=Category.objects.get(pk=pk).delete()
        return HttpResponse(status=204,headers={'HX-Trigger':'listChanged'})



class ProductsView(PermissionRequiredMixin,View):
    permission_required=['pos.view_product']
    form_class=ProductForm
    model_class=Product
    template_name='pos/products.html'
    def get(self,request):
        context={}
        action=request.GET.get("action",None)
        if action=="get-form":
            context['form']=self.form_class
            return render(request, 'pos/partials/product-form.html',context)
        product_list = Product.objects.all()
        context = {
            'page_title':'Product List',
            'list':product_list,
        }
        if request.htmx:
            self.template_name='pos/partials/products-list.html'
        return render(request, self.template_name,context)
    
    def post(self,request):
        form=self.form_class(request.POST,request.FILES)
        context = {'form':form}
        if form.is_valid():
            form.save()
            return HttpResponse(status=204,headers={'HX-Trigger':'listChanged'})
        else:
            return render(request, 'pos/partials/product-form.html',context)


class ProductView(LoginRequiredMixin,View):
    form_class=ProductForm
    model_class=Product
    def get(self,request,pk):
        product=self.model_class.objects.get(pk=pk)
        context={'product':product}
        context['form']=self.form_class(instance=product)
        return render(request, 'pos/partials/product-form.html',context)
    def post(self,request,pk):
        product=self.model_class.objects.get(pk=pk)
        form=self.form_class(request.POST,request.FILES,instance=product)
        context = {'form':form}
        if form.is_valid():
            form.save()
            return HttpResponse(status=204,headers={'HX-Trigger':'listChanged'})
        else:
            return render(request, 'pos/partials/product-form.html',context)
    def delete(self,request,pk):
        product=self.model_class.objects.get(pk=pk).delete()
        return HttpResponse(status=204,headers={'HX-Trigger':'listChanged'})

class SalesView(PermissionRequiredMixin,View):
    permission_required=['pos.view_sale']
    template_name="pos/sales.html"
    filter_class=SalesFilter
    def get(self,request):
        sales = Sale.objects.all()
        if not request.user.is_superuser:sales=sales.filter(created_by=request.user)
        sales=self.filter_class(request.GET,sales).qs
        context = {
            'page_title':'Sale Transactions',
            'list':sales,
            'filters':self.filter_class
        }
        if request.htmx:
            self.template_name='pos/partials/sales-list.html'
        return render(request, self.template_name,context)

class SaleView(LoginRequiredMixin,View):
    class_model=Sale
    
    def get(self,request,pk):
        pass
    def post(self,request,pk):
        return HttpResponse(status=204,headers={'HX-Trigger':'listChanged'})
    def delete(self,request,pk):
        sale=self.class_model.objects.filter(pk=pk)
        # sale.delete()
        return HttpResponse(status=204,headers={'HX-Trigger':'listChanged'})

  
def about(request):
    context = {
        'page_title':'About',
    }
    return render(request, 'pos/about.html',context)

class AddSale(PermissionRequiredMixin,View):
    permission_required=['pos.add_sale']
    def get(self,request):
        categories = Category.objects.filter(status = 1,product__isnull=False).distinct()
        products = Product.objects.filter(status = 1)
        product_json=list(products.values("id","name","price","track_stock","in_stock","unit_measure","barcode","color","low_stock_level"))
        context = {
            'page_title' : "Point of Sale",
            'products' : products,
            'categories':categories,
            'product_json' : json.dumps(product_json)
        }
        # return HttpResponse('')
        return render(request, 'pos/pos.html',context)
    def post(self,request):
        resp = {'status':'failed','msg':''}
        data = request.POST
        pref = datetime.now().year + datetime.now().year
        i = 1
        while True:
            code = '{:0>5}'.format(i)
            i += int(1)
            check = Sale.objects.filter(code = str(pref) + str(code)).all()
            if len(check) <= 0:
                break
        code = str(pref) + str(code)

        try:
            if len(data.getlist('product_id[]'))==0:
                resp['msg'] = "Cannot make a sale with empty products list"
                return HttpResponse(json.dumps(resp),content_type="application/json")
            sales = Sale(code=code, sub_total = data['sub_total'], tax = data['tax'], tax_amount = data['tax_amount'], grand_total = data['grand_total'], tendered_amount = data['tendered_amount'], amount_change = data['amount_change']).save()
            sale_id = Sale.objects.last().pk
            i = 0
            for prod in data.getlist('product_id[]'):
                product_id = prod 
                sale = Sale.objects.filter(id=sale_id).first()
                product = Product.objects.filter(id=product_id).first()
                qty = data.getlist('qty[]')[i] 
                price = data.getlist('price[]')[i] 
                total = float(qty) * float(price)
                print({'sale_id' : sale, 'product_id' : product, 'qty' : qty, 'price' : price, 'total' : total})
                SalesItem(sale = sale, product = product, qty = qty, price = price, total = total).save()
                i += int(1)
            resp['status'] = 'success'
            resp['sale_id'] = sale_id
            messages.success(request, "Sale Record has been saved.")
        except:
            resp['msg'] = "An error occured"
            print("Unexpected error:", sys.exc_info()[0])
        return HttpResponse(json.dumps(resp),content_type="application/json")



@login_required
def receipt(request):
    id = request.GET.get('id')
    transaction = Sale.objects.filter(id = id).first()
    ItemList = SalesItem.objects.filter(sale = transaction).all()
    context = {
        "transaction" : transaction,
        "salesItems" : ItemList
    }

    return render(request, 'pos/receipt.html',context)