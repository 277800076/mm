#coding=UTF-8
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext

from business.models import Company,Log
from doc.models import Document

from utils.switchcase.sw import switch

from decorators import manage_required
from forms import *


def login(request):
    if request.method=='POST':
        f=LoginForm(request.POST)
        if f.is_valid():
            mb=f.cleaned_data['mobile']
            pd=f.cleaned_data['password']
            if mb=='13733820232' and pd=='3947638': 
                request.session['manage']='13733820232'
                return HttpResponseRedirect("/manage/")
            else:
                return HttpResponseRedirect("/manage/login/")
        else:
            return HttpResponseRedirect("/err/no_enough_information/")
    else:
        request.session['manage']=None
        f=LoginForm()
        return render_to_response('manage_login.html',{'f':f},RequestContext(request))


@manage_required
def manage(request):
    return render_to_response('manage.html',{'list':list},RequestContext(request))


@manage_required
def manage_company(request):
    list=Company.objects.all()
    return render_to_response('manage_company.html',{'list':list},RequestContext(request))

@manage_required
def manage_log(request):
    list=Log.objects.all()
    return render_to_response('manage_log.html',{'list':list},RequestContext(request))


