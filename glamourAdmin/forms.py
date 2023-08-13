from django import forms
from django.forms import inlineformset_factory
from glamourApp.models import Product, ProductImage, ProductSize, SubCategory, Category, DiscountCode


class CategoryForm(forms.ModelForm):
    name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    description = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Category
        fields = ['name', 'description']


class SubCategoryForm(forms.ModelForm):
    name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = SubCategory
        fields = ['name']


class SizeForm(forms.ModelForm):
    name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = ProductSize
        fields = ['name']


class CouponForm(forms.ModelForm):
    percentage = forms.FloatField(max_value=100)
    number_of_codes = forms.IntegerField(max_value=100)

    class Meta:
        model = DiscountCode
        fields = ['percentage']
