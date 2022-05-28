from . import views
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path

urlpatterns = [
    path('categories', views.CategoriesView.as_view(), name="categories"),
    path('category/<int:pk>/', views.CategoryView.as_view(), name="category"),

    path('products', views.ProductsView.as_view(), name="products"),
    path('product/<int:pk>/', views.ProductView.as_view(), name="product"),

    path('', views.AddSale.as_view(), name="pos"),

    path('sales', views.SalesView.as_view(), name="sales"),
    path('sale/<int:pk>/', views.SaleView.as_view(), name="sale"),

    path('receipt', views.receipt, name="receipt-modal"),
]