#coding=UTF-8
from django import forms
from django.forms import TextInput


class DocumentForm(forms.Form):
    title=forms.CharField(label='标题',widget=forms.TextInput(attrs={'class':'txt','size':'60'}))
    keywords=forms.CharField(label='关键字',widget=forms.TextInput(attrs={'class':'txt'}))
    description=forms.CharField(label='摘要',widget=forms.TextInput(attrs={'class':'txt','size':'60'}))
    content=forms.CharField(label='内容',widget=forms.Textarea(attrs={'class':'txt_area','cols':'120','rows':'15'}))
