#coding=UTF-8
'''
Created on 2014-4-27

@author: 李璟潭
'''
from django.http import HttpResponseRedirect
from models import Role,Content

def login_required(fun):
    def ifun(request,*args, **kwargs):
        try: 
            u= request.session['user']
            return fun(request,*args, **kwargs)
        except:
            return HttpResponseRedirect("/") 
    return ifun

def permission_required(fun):
    def ifun(request,*args, **kwargs): 
        u= request.session['user']
        path=request.get_full_path()
        i=path.rfind('/')
        path=path[0:i+1]
        r=Role.objects.filter(user__id=u.id,permission__content__url=path)
        #这里不能用user=u，因为user的uuid
        if r.count()==0:
            return HttpResponseRedirect("/err/no_access/") 
        else:
            return fun(request,*args, **kwargs)
    return ifun
