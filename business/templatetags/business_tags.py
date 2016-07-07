# coding:utf-8
from django import template
from decimal import Decimal
import datetime

import urllib
register=template.Library()

#显示status值对应的文字
@register.filter(name='display_status')
def display_status(value, arg):
    return apply(eval('value.get_'+arg+'_display'), ())

@register.filter(name='display_verbose_name')
def display_verbose_name(value,arg):
    return value._meta.get_field(arg).verbose_name.title()

#改为负值
@register.filter(name='negative')
def negative(value):
    return -value

#把字符串编码为url
@register.filter(name='quote')
def encode_url(value):
    return urllib.quote(value)

#日期加减
@register.filter(name='addday')
def addday(value,arg):
    d=value+datetime.timedelta(days=arg)
    return d.strftime('%Y-%m-%d')

#日期生成月
#YYYY-MM
@register.filter(name='month')
def month(value):
    return value.strftime('%Y-%m')

#日期生成年
#YYYY
@register.filter(name='year')
def year(value):
    return value.strftime('%Y')