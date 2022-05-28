from django.contrib.auth.password_validation import validate_password
from django import forms
from django.conf import settings
from .models import *
from django.contrib.admin import widgets

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Div


class ProductCategoryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProductCategoryForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
    class Meta:
        model=Category
        fields=['name','description','color','status']
        widgets={
            'name':forms.TextInput(attrs={'class':'form-control'}),
            'description':forms.Textarea(attrs={'class':'form-control','rows':3}),
            'status':forms.Select(attrs={'class':'form-control'}),
            'color':forms.TextInput(attrs={'class':'form-control','type':'color'}),
        }

class ProductForm(forms.ModelForm):
    col1_fields=['name','code','category','cost','price','track_stock','in_stock','low_stock_level']
    col2_fields=['color','description','barcode','unit_measure','sku','status']
    col3_fields=['unit_measure','sku',]
    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                Div(*self.col1_fields, css_class='col-sm-6'),
                Div(*self.col2_fields, css_class='col-sm-6'),
                # Div(*self.col3_fields, css_class='col-sm-4'), 
                css_class='row'
            ),
        )
    class Meta:
        model=Product
        fields='__all__'
        exclude=['date_added']
        widgets={
            'name':forms.TextInput(attrs={'class':'form-control'}),
            'description':forms.Textarea(attrs={'class':'form-control','rows':2}),
            'status':forms.Select(attrs={'class':'form-control'}),
            'category':forms.Select(attrs={'class':'form-select form-select-sm'}),
            'color':forms.TextInput(attrs={'class':'form-control','type':'color'}),
        }
    def clean_in_stock(self):
        val=self.cleaned_data.get("in_stock",None)
        track_stock=self.cleaned_data.get("track_stock",None)
        if track_stock and not val:
            raise forms.ValidationError("Cannot submit empty stock when stock tracking is enabled")
        return val

    def clean_price(self):
        val=self.cleaned_data.get("price",None)
        if val and val<=0:
            raise forms.ValidationError("Cannot submit non positive valued prices")
        return val
