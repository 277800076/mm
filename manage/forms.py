#coding=UTF-8
from django import forms
from django.forms import TextInput


class LoginForm(forms.Form):
    mobile=forms.CharField(label='手机',widget=forms.TextInput(attrs={'class':'login-textbox','placeholder':'手机'}))
    password=forms.CharField(label='密码',widget=forms.PasswordInput(attrs={'class':'login-textbox','placeholder':'密码','onkeydown':'onkey()'}))
