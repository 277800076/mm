#coding=UTF-8
import re
import random

#过滤保留号
#输入一个数字
#如果是坏号，会输出坏号
#如果是好号，会输出大于好号的最小坏号
def get_bad_number(n):
    regs=(
          #3-9位连续号,升降序
          r'(?:(?:0(?=1)|1(?=2)|2(?=3)|3(?=4)|4(?=5)|5(?=6)|6(?=7)|7(?=8)|8(?=9)){2,}|(?:9(?=8)|8(?=7)|7(?=6)|6(?=5)|5(?=4)|4(?=3)|3(?=2)|2(?=1)|1(?=0)){2,})\d',
          #3位及以上连续号
          r'[\d]*([\d])\1{2,}[\d]*',
          #aabb及变形
          r'([\d])\1{1,}[\d]*([\d])\2{1,}[\d]*'
          )
    matched=1
    while matched==1:
        rm=0
        for r in regs:
            s=re.match(r,str(n))
            if s:
                rm=1
        if rm==1:        
            matched=1
            n+=1
        else:
            matched=0
    return n



#参数是几位
#输出几位的字符串
#n最大50,大于50返回空
def get_random_number(n):
    if n>50:
        return ''
    else:
        result='%.50f' % random.random()
        result=result[2:n+2]
        return result