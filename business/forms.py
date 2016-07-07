#coding=UTF-8
from django import forms
from django.forms import ModelForm,TextInput
from models import *


class RegisterForm(forms.Form):
    company_name=forms.CharField(label='公司名称',widget=forms.TextInput(attrs={'class':'txt','size':'35'}))
    mobile=forms.CharField(label='手机',widget=forms.TextInput(attrs={'class':'txt','size':'35'}))
    password=forms.CharField(label='密码',widget=forms.PasswordInput(attrs={'class':'txt','size':'35'}))

class LoginForm(forms.Form):
    mobile=forms.CharField(label='手机',widget=forms.TextInput(attrs={'class':'login-textbox','placeholder':'手机'}))
    password=forms.CharField(label='密码',widget=forms.PasswordInput(attrs={'class':'login-textbox','placeholder':'密码','onkeydown':'onkey()'}))
    
class SearchForm(forms.Form):
    key_words=forms.CharField(widget=forms.TextInput(attrs={'class':'txt_search','autocomplete':'off'}))

class UnitForm(forms.Form):
    unit_name=forms.CharField(label='客户名称',widget=forms.TextInput(attrs={'class':'txt'}))
    mobile=forms.CharField(label='手机',required=False,widget=forms.TextInput(attrs={'class':'txt'}))

class CardForm(forms.Form):
    card_type=forms.CharField(label='卡类型',widget=forms.TextInput())
    cardno=forms.CharField(label='卡号',widget=forms.TextInput(attrs={'class':'txt'}))

class ProductForm(forms.Form):
    product_name=forms.CharField(label='商品名称',widget=forms.TextInput(attrs={'class':'txt'}))

class BranchForm(forms.Form):
    branch_name=forms.CharField(label='分店名称',widget=forms.TextInput(attrs={'class':'txt'}))
    
class UserForm(forms.Form):
    real_name= forms.CharField(label='职员姓名',widget=forms.TextInput(attrs={'class':'txt'}))
    branch_id=forms.CharField(label='分店id',widget=forms.TextInput(attrs={'class':'txt'}))
    branch_name=forms.CharField(label='分店',widget=forms.TextInput(attrs={'class':'txt'}))
    mobile = forms.CharField(label='手机',widget=forms.TextInput(attrs={'class':'txt'}))
    password = forms.CharField(label='密码',required=False,widget=forms.PasswordInput(attrs={'class':'txt'}))
    roles = forms.ModelMultipleChoiceField(label='角色',widget=forms.CheckboxSelectMultiple(),queryset=Role.objects.all())  

class SettingForm(forms.Form):
    CHOICES=[('1','充值卡'),
             ('2','计次卡'),
             ('3','混合模式')]
    card_type = forms.ChoiceField(label='卡类型',choices=CHOICES, widget=forms.RadioSelect())
    custom_price=forms.BooleanField(label='开启分店自定义商品价格',required=False)


class BillForm(forms.Form):
    card_id=forms.CharField(label='id',widget=forms.TextInput(attrs={'class':'txt'}))
    cardno=forms.CharField(label='卡号',widget=forms.TextInput(attrs={'class':'txt'}))

class RechargeValueForm(BillForm):
    money=forms.CharField(label='收款',widget=forms.TextInput(attrs={'class':'txt'}))
    amount=forms.DecimalField(label='充值',widget=forms.TextInput(attrs={'class':'txt'}))

class RechargeTimesForm(BillForm):
    money=forms.CharField(label='收款',widget=forms.TextInput(attrs={'class':'txt'}))
    times=forms.IntegerField(label='次数',widget=forms.TextInput(attrs={'class':'txt'}))

class SaleValueForm(BillForm):
    pass

class SaleTimesForm(BillForm):
    times=forms.IntegerField(label='次数',widget=forms.TextInput(attrs={'class':'txt'}))

    
class PasswordForm(forms.Form):
    oldpassword=forms.CharField(label='旧口令',widget=forms.PasswordInput(attrs={'class':'txt'}))
    password1 = forms.CharField(label='新口令',widget=forms.PasswordInput(attrs={'class':'txt'}))
    password2 = forms.CharField(label='确认新口令',widget=forms.PasswordInput(attrs={'class':'txt'}))


