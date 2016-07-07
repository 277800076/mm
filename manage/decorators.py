#coding=UTF-8
'''
Created on 2014-10-26

@author: 李璟潭
'''
from django.http import HttpResponseRedirect

def manage_required(fun):
    def ifun(request,*args, **kwargs):
        try: 
            m= request.session['manage']
            if m=='13733820232':
                return fun(request,*args, **kwargs)
            else:
                return HttpResponseRedirect("/manage/login/") 
        except:
            return HttpResponseRedirect("/manage/login/") 
    return ifun

