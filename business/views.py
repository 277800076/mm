#coding=UTF-8
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.template import RequestContext
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from datetime import tzinfo
import datetime,time
import re
import hashlib

from models import *
from forms import *


from decimal import Decimal
from django.core.mail import send_mail
from django.utils import simplejson
from django.db.models import Sum
from django.db.models import Q
from django.db import connection
from django.template.defaultfilters import floatformat
from decorators import login_required
from decorators import permission_required
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.db.models.aggregates import Count, Sum

from utils.switchcase.sw import switch
from utils.toolkit.number import get_bad_number,get_random_number

from alipay.alipay import *


def index(request):
    request.session['user']=None
    return render_to_response ('index.html',{}, RequestContext(request))

#@transaction.commit_manually 

def register(request):
    if request.method=='POST':
        f=RegisterForm(request.POST)
        if f.is_valid():
            #try:
            cn=f.cleaned_data['company_name']
            mb=f.cleaned_data['mobile']
            pw=f.cleaned_data['password']

            bn='总部'
            rn='管理员'
            
            us=User.objects.filter(mobile=mb)
            if us.count()>0:
                return HttpResponseRedirect("/err/mobile_existed/")
            
            
            t=datetime.datetime(2020,12,31,23,59,59)
            #from django.utils import timezone
            #普通时间替换为UTC时间
            t=t.replace(tzinfo=timezone.UTC())
            
            s=Service.objects.get(id='1')
            
            c=Company(company_name=cn,time_expired=t,service=s)
            c.save()

            
            b=Branch(company=c,branch_name=bn,is_base=True)
            b.save()
            
            #获得管理员和出纳的role
            r1=Role.objects.get(id=1)
            r2=Role.objects.get(id=2)
            
            u=User(company=c,branch=b,mobile=mb,password=hashlib.sha1(pw).hexdigest(),real_name=rn,is_admin=True)
            u.save()
            u.role.add(r1)
            u.role.add(r2)
            
            #以下为总部现金科目、主营业务科目添加唯一子科目
            s1001=Subject.objects.get(id='1001')
            sc=SubjectBranch(branch=b,subject=s1001,amount=0)
            sc.save()

            request.session['c']=c
            return HttpResponseRedirect("/register_ok")
#             except:
#                 return HttpResponseRedirect("/err/internal_error/")
        else:
            return HttpResponseRedirect("/err/no_enough_information")
    else:
        f=RegisterForm()
        f.fields['company_name'].widget.attrs['validate'] = 'chinese'
        f.fields['company_name'].widget.attrs['min'] = '4'
        f.fields['company_name'].widget.attrs['max'] = '30'
        f.fields['mobile'].widget.attrs['validate'] = 'mobile'
        f.fields['mobile'].widget.attrs['min'] = '11'
        f.fields['mobile'].widget.attrs['max'] = '11'
        f.fields['password'].widget.attrs['validate'] = 'password'
        f.fields['password'].widget.attrs['min'] = '6'
        f.fields['password'].widget.attrs['max'] = '20'
        return render_to_response('register.html',{'f':f},RequestContext(request))

def register_ok(request):
    return render_to_response('register_ok.html',{},RequestContext(request))

def win_login(request):
    f=LoginForm()
    return render_to_response('win_login.html',{'f':f},RequestContext(request))

def login(request):
    request.session['user']=None
    f=LoginForm()
    return render_to_response('login.html',{'f':f},RequestContext(request))

@csrf_exempt
def auth(request):
    response=HttpResponse()
    response['Content-Type']="text/javascript"
    mb=request.POST.get('txtMobile')
    pw=request.POST.get('txtPassword')
    if mb and pw:
        try:
            us=User.objects.filter(mobile=mb,password=hashlib.sha1(pw).hexdigest())
            if us.count()==1:
                if us[0].company.time_expired>timezone.now():
                    ret=1
                    request.session['user']=us[0]
                else:
                    ret=5 #已过期
            else:
                ret=2   #密码不对
        except:
            ret=4       #内部错误
    else:
        ret=3           #用户名或密码缺少
    response.write(ret)
    return response

@login_required
@permission_required
def main(request):
    u=request.session['user']
    a=App.objects.filter(content_group__role__user__id=u.id).distinct()
    return render_to_response ('main.html',{'a':a}, RequestContext(request))

def help(request):
    return render_to_response('public_help.html',{},RequestContext(request))

def version(request):
    s1=Service.objects.get(id=1)
    s2=Service.objects.get(id=2)
    return render_to_response('public_version.html',{'s1':s1,'s2':s2},RequestContext(request))

@login_required
def buy(request):
    u=request.session['user']
    if request.method=='POST':
        pid=request.POST.get('product_id')
        bkid=request.POST.get('bank_id')
        g,bkid=bkid.split('|')
        
        try:
            p=cProduct.objects.get(id=pid)
            b=cBank.objects.get(id=bkid,gateway=g)
        except ObjectDoesNotExist:
            return HttpResponseRedirect("/err/no_object")

        try:
            id=datetime.datetime.now().strftime('%Y%m%d-%H%M%S-')+get_random_number(6)
            bill=cBill(id=id,company=u.company,cproduct=p,cbank=b,amount=p.price,status=1)
            bill.save()
        except:
            return HttpResponseRedirect("/err/record_already_exists/")

        return HttpResponseRedirect("/public/confirm/"+id)
    else:
        try:
            list=cBank.objects.filter(is_display=True)
            return render_to_response('public_buy.html',{'list':list},RequestContext(request))
        except ObjectDoesNotExist:
            return HttpResponseRedirect("/err/no_object")        

@login_required
def confirm(request,cbid):
    u=request.session['user']
    try:
        cb=cBill.objects.get(id=cbid,company=u.company)
        return render_to_response('public_confirm.html',{'cb':cb},RequestContext(request))
    except ObjectDoesNotExist:
        return HttpResponseRedirect("/err/no_object")

def pay(request):
    cbid=request.POST.get('id')
    try:
        cb=cBill.objects.get(id=cbid)
    except ObjectDoesNotExist:
        return HttpResponseRedirect("/err/no_object")
    
    #如果网关是支付宝
    if cb.cbank.gateway=='alipay':
            tn=cb.id
            subject=cb.cproduct.product_name+'_'+cb.company.company_name
            body=cb.cproduct.product_name+'_'+cb.company.company_name
            bank=cb.cbank.id
            tf='%.2f' % cb.amount
            url=create_direct_pay_by_user (tn,subject,body,bank,tf)

    #如果网关是财付通
    elif cb.cbank.gateway=='tenpay':
        pass
    
    #去支付页面
    return HttpResponseRedirect (url)

#alipay异步通知

@csrf_exempt
def alipay_notify_url (request):
    if request.method == 'POST':
        if notify_verify (request.POST):
            #商户网站订单号
            tn = request.POST.get('out_trade_no')
            #支付宝单号
            trade_no=request.POST.get('trade_no')
            #返回支付状态
            trade_status = request.POST.get('trade_status')
            cb = cBill.objects.get(pk=tn)
            
            if trade_status == 'TRADE_SUCCESS':
                cb.exe()
                log=Log(operation='notify1_'+trade_status+'_'+trade_no)
                log.save()
                return HttpResponse("success")
            else:
                #写入日志
                log=Log(operation='notify2_'+trade_status+'_'+trade_no)
                log.save()
                return HttpResponse ("success")
        else:
            #黑客攻击
            log=Log(operation='hack_notify_'+trade_status+'_'+trade_no+'_'+'out_trade_no')
            log.save()
    return HttpResponse ("fail")

#同步通知

def alipay_return_url (request):
    if notify_verify (request.GET):
        tn = request.GET.get('out_trade_no')
        trade_no = request.GET.get('trade_no')
        trade_status = request.GET.get('trade_status')
          
        cb = cBill.objects.get(pk=tn)
        log=Log(operation='return_'+trade_status+'_'+trade_no)
        log.save()
        return HttpResponseRedirect ("/public/verify/"+tn)
    else:
        #错误或者黑客攻击
        log=Log(operation='err_return_'+trade_status+'_'+trade_no)
        log.save()
        return HttpResponseRedirect ("/")


#外部跳转回来的链接session可能丢失，无法再进入系统。
#客户可能通过chengsoft.com操作，但是支付宝只返回www.chengsoft.com，如果域名不同，session丢失。
def verify(request,cbid):
    try:
        cb=cBill.objects.get(id=cbid)
        #如果订单时间距现在超过1天，跳转到错误页面！
        #避免网站信息流失
        
        return render_to_response('public_verify.html',{'cb':cb},RequestContext(request))
    except ObjectDoesNotExist:
        return HttpResponseRedirect("/err/no_object")
    
@login_required
def company_view(request):
    u=request.session['user']
    list=cBill.objects.filter(company=u.company,status=10)
    return render_to_response('setting_company_view.html',{'list':list},RequestContext(request))

@login_required
@permission_required
def branch(request):
    u=request.session['user']
    list=Branch.objects.filter(company=u.company)
    return render_to_response('setting_branch.html',{'list':list},RequestContext(request))

@login_required
@permission_required
def branch_new(request):
    u=request.session['user']
    if request.method=='POST':
        f=BranchForm(request.POST)
        if f.is_valid():
            if u.company.service.max_branch==Branch.objects.filter(company=u.company).count():
                return HttpResponseRedirect("/dlg/no_more_branch/")
            
            bn=f.cleaned_data['branch_name']
            try:
                s1001=Subject.objects.get(id='1001')
                b=Branch(company=u.company,branch_name=bn)
                b.save()

                sc=SubjectBranch(branch=b,subject=s1001,amount=0)
                sc.save()

            except:
                return HttpResponseRedirect("/err/record_already_exists/")

            return HttpResponseRedirect("/setting/branch/")
        else:
            return HttpResponseRedirect("/err/no_enough_information")
    else:
        if u.company.service.max_branch==Branch.objects.filter(company=u.company).count():
            return HttpResponseRedirect("/dlg/no_more_branch/")
        else:
            f=BranchForm()
            f.fields['branch_name'].widget.attrs['validate'] = "not_null"
            f.fields['branch_name'].widget.attrs['min'] = "2"
            f.fields['branch_name'].widget.attrs['max'] = "20"
            return render_to_response('setting_branch_new.html',{'f':f},RequestContext(request))

@login_required
@permission_required
def branch_edit(request,branch_id):
    u=request.session['user']
    try:
        b=Branch.objects.get(id=branch_id)
    except ObjectDoesNotExist:
        return HttpResponseRedirect("/err/no_object")
    if request.method=='POST':
        f=BranchForm(request.POST)
        if f.is_valid():
            bn=f.cleaned_data['branch_name']
            
            b.branch_name=bn

            try:
                b.save()
            except:
                return HttpResponseRedirect("/err/record_already_exists/")

            return HttpResponseRedirect("/setting/branch/")
        else:
            return HttpResponseRedirect("/err/no_enough_information/")
    else:
        f=BranchForm({
            'branch_name':b.branch_name
            })
        f.fields['branch_name'].widget.attrs['validate'] = "not_null"
        f.fields['branch_name'].widget.attrs['min'] = "2"
        f.fields['branch_name'].widget.attrs['max'] = "50"

        return render_to_response('setting_branch_edit.html',{'f':f,'b':b},RequestContext(request))

@login_required
@permission_required
def branch_delete(request,):
    u=request.session['user']
    response=HttpResponse()
    response['Content-Type']="text/javascript"
    ids=request.POST.get('ids')
    ret=0
    if ids:
        items=ids.split(',')
        try:
            Branch.objects.filter(id__in=items).filter(company=u.company).exclude(is_base=True).delete()
            ret=1 #删除成功
        except:
            ret=3 #已经不能删除
    else:
        ret=2 #没有选中
    response.write(ret)
    return response 

@login_required
@permission_required
def branch_select(request):
    u=request.session['user']
    
    #ids是把id值传送到母窗口控件的ID，id_selector
    ids=request.GET.get('ids')
    #ns是把name值传送到母窗口控件的ID,name_selector
    ns=request.GET.get('ns')
    
    
    if request.method=='POST':
        f=SearchForm(request.POST)
        if f.is_valid():
            k=f.cleaned_data['key_words']
            list=Branch.objects.filter(company=u.company).filter(branch_name__icontains=k)
        else:
            return HttpResponseRedirect("/err/no_enough_information")
    else:
        f=SearchForm()
        list=Branch.objects.filter(company=u.company)
    return render_to_response('setting_branch_select.html',{'f':f,'list':list,'ids':ids,'ns':ns},RequestContext(request))


@login_required
@permission_required
def user(request):
    u=request.session['user']
    list=User.objects.filter(company=u.company)
    return render_to_response('setting_user.html',{'list':list},RequestContext(request))

#@login_required
#@permission_required

def user_new(request):
    u=request.session['user']
    if request.method=='POST':
        f=UserForm(request.POST)
        if f.is_valid():
            b_id=f.cleaned_data['branch_id']
            rn=f.cleaned_data['real_name']
            mb=f.cleaned_data['mobile']
            pw=f.cleaned_data['password']
            rs=f.cleaned_data['roles']
            
            b=Branch.objects.get(id=b_id)

            user=User(company=u.company,branch=b,mobile=mb,password=hashlib.sha1(pw).hexdigest(),real_name=rn)
            try:
                user.save()
                for i in rs:
                    user.role.add(i)
            except:
                return HttpResponseRedirect("/err/record_already_exists/")

            return HttpResponseRedirect("/setting/user/")
        else:
            return HttpResponseRedirect("/err/no_enough_information")
    else:
        f=UserForm()
        f.fields['real_name'].widget.attrs['validate'] = "chinese"
        f.fields['real_name'].widget.attrs['min'] = "2"
        f.fields['real_name'].widget.attrs['max'] = "5"
        f.fields['branch_name'].widget.attrs['readonly'] = True
        f.fields['branch_name'].widget.attrs['class'] = 'txt bg-ll-blue'
        f.fields['branch_name'].widget.attrs['validate'] = "not_null"        
        f.fields['mobile'].widget.attrs['validate'] = "mobile"
        f.fields['password'].widget.attrs['validate'] = "password"
        f.fields['password'].widget.attrs['min'] = "6"
        f.fields['password'].widget.attrs['max'] = "20"

        return render_to_response('setting_user_new.html',{'f':f},RequestContext(request))

@login_required
@permission_required
def user_edit(request,user_id):
    u=request.session['user']
    try:
        user=User.objects.get(id=user_id)
    except ObjectDoesNotExist:
        return HttpResponseRedirect("/err/no_object")
    if request.method=='POST':
        f=UserForm(request.POST)
        if f.is_valid():
            rn=f.cleaned_data['real_name']
            b_id=f.cleaned_data['branch_id']
            mb=f.cleaned_data['mobile']
            pw=f.cleaned_data['password']
            rs=f.cleaned_data['roles']
            
            b=Branch.objects.get(id=b_id)
            
            user.real_name=rn
            user.branch=b
            user.mobile=mb
            if len(pw)>0:
                user.password=hashlib.sha1(pw).hexdigest()

            try:
                user.save()
                user.role.clear()
                for i in rs:
                    user.role.add(i)
            except:
                return HttpResponseRedirect("/err/record_already_exists/")

            return HttpResponseRedirect("/setting/user/")
        else:
            return HttpResponseRedirect("/err/no_enough_information/")
    else:
        f=UserForm({
            'real_name':user.real_name,
            'branch_id':user.branch.id,
            'branch_name':user.branch.branch_name,
            'mobile':user.mobile,
            'password':user.password,
            'roles':user.role.all(),
            })
        f.fields['real_name'].widget.attrs['validate'] = "chinese"
        f.fields['real_name'].widget.attrs['min'] = "2"
        f.fields['real_name'].widget.attrs['max'] = "5"
        f.fields['branch_name'].widget.attrs['readonly'] = True
        f.fields['branch_name'].widget.attrs['class'] = 'txt bg-ll-blue'
        f.fields['branch_name'].widget.attrs['validate'] = "not_null" 
        f.fields['mobile'].widget.attrs['validate'] = "mobile"
        f.fields['mobile'].widget.attrs['min'] = "11"
        f.fields['mobile'].widget.attrs['max'] = "11"
        f.fields['password'].widget.attrs['validate'] = "password"
        f.fields['password'].widget.attrs['empty'] = "yes"
        f.fields['password'].widget.attrs['min'] = "6"
        f.fields['password'].widget.attrs['max'] = "20"

        return render_to_response('setting_user_edit.html',{'f':f,'user':user},RequestContext(request))

@login_required
@permission_required
def user_delete(request,):
    u=request.session['user']
    response=HttpResponse()
    response['Content-Type']="text/javascript"
    ids=request.POST.get('ids')
    ret=0
    if ids:
        try:
            items=ids.split(',')
            User.objects.filter(id__in=items).filter(company=u.company).exclude(is_admin=True).delete()
            ret=1 #删除成功
        except:
            ret=3 #不能删除
    else:
        ret=2 #没有选中
    response.write(ret)
    return response

@login_required
@permission_required
def product(request):
    u=request.session['user']
    list=Product.objects.filter(company=u.company)
    return render_to_response('setting_product.html',{'list':list},RequestContext(request))

@login_required
@permission_required
def product_new(request):
    u=request.session['user']
    if request.method=='POST':
        f=ProductForm(request.POST)
        if f.is_valid():
            pn=f.cleaned_data['product_name']

            p=Product(company=u.company,product_name=pn)
            try:
                p.save()
            except:
                return HttpResponseRedirect("/err/record_already_exists/")

            return HttpResponseRedirect("/setting/product/")
        else:
            return HttpResponseRedirect("/err/no_enough_information")
    else:
        f=ProductForm()
        f.fields['product_name'].widget.attrs['validate'] = "not_null"
        f.fields['product_name'].widget.attrs['min'] = "2"
        f.fields['product_name'].widget.attrs['max'] = "50"

        return render_to_response('setting_product_new.html',{'f':f},RequestContext(request))

@login_required
@permission_required
def product_edit(request,product_id):
    u=request.session['user']
    try:
        p=Product.objects.get(id=product_id)
    except ObjectDoesNotExist:
        return HttpResponseRedirect("/err/no_object")
    if request.method=='POST':
        f=ProductForm(request.POST)
        if f.is_valid():
            pn=f.cleaned_data['product_name']
            
            p.product_name=pn

            try:
                p.save()
            except:
                return HttpResponseRedirect("/err/record_already_exists/")

            return HttpResponseRedirect("/setting/product/")
        else:
            return HttpResponseRedirect("/err/no_enough_information/")
    else:
        f=ProductForm({
            'product_name':p.product_name
            })
        f.fields['product_name'].widget.attrs['validate'] = "not_null"
        f.fields['product_name'].widget.attrs['min'] = "2"
        f.fields['product_name'].widget.attrs['max'] = "50"

        return render_to_response('setting_product_edit.html',{'f':f,'p':p},RequestContext(request))

@login_required
@permission_required
def product_delete(request,):
    u=request.session['user']
    response=HttpResponse()
    response['Content-Type']="text/javascript"
    ids=request.POST.get('ids')
    ret=0
    if ids:
        try:
            items=ids.split(',')
            Product.objects.filter(id__in=items).filter(company=u.company).delete()
            ret=1 #成功
        except:
            ret=3 #产品已使用
    else:
        ret=2 #没有选中
    response.write(ret)
    return response 

#@login_required
#@permission_required
def setup(request):
    u=request.session['user']
    try:
        cs=CompanySetting.objects.get(company=u.company)
    except ObjectDoesNotExist:
        return HttpResponseRedirect("/err/no_object")
    if request.method=='POST':
        f=SettingForm(request.POST)
        if f.is_valid():
            ct=f.cleaned_data['card_type']
            #cp=f.cleaned_data['custom_price']

            cs.card_type=ct
            #cs.custom_price=cp

            try:
                cs.save()
            except:
                return HttpResponseRedirect("/err/record_already_exists/")

            return HttpResponseRedirect("/public/main/")
        else:
            return HttpResponseRedirect("/err/no_enough_information")
    else:
        f=SettingForm({
            'card_type':cs.card_type,
            #'custom_price':cs.custom_price,
            })
        return render_to_response('setting_setup.html',{'f':f},RequestContext(request))


@login_required
@permission_required
def unit(request):
    u=request.session['user']
    list=Unit.objects.filter(company=u.company)
    if request.method=='POST':
        f=SearchForm(request.POST)
        if f.is_valid():
            uid,un,mb='','',''
            k=f.cleaned_data['key_words']

            r1=re.findall(r'^\d{3}-\d{3}$',k)
            r2=re.findall(u'^[\u4E00-\u9FA5\uf900-\ufa2d]+$',k)
            r3=re.findall(r'^\d{11}$',k)

            if r1:
                uid=r1[0]
                list=Unit.objects.filter(company=u.company).filter(unit_id=uid)
            elif r2:
                un=r2[0]
                list=Unit.objects.filter(company=u.company).filter(unit_name__icontains=un)
            elif r3:
                mb=r3[0]
                list=Unit.objects.filter(company=u.company).filter(mobile=mb)
            else:
                list=Unit.objects.filter(company=u.company).filter(card__cardno__icontains=k)
    else:
        f=SearchForm()
        f.fields['key_words'].widget.attrs['placeholder'] = "客户编号、姓名、手机号、卡号"
    return render_to_response('business_unit.html',{'f':f,'list':list},RequestContext(request))

#@login_required
#@permission_required

def unit_new(request):
    u=request.session['user']
    if request.method=='POST':
        uf=UnitForm(request.POST)
        cf=CardForm(request.POST)
        if uf.is_valid() and cf.is_valid():
            if u.company.service.max_unit==Unit.objects.filter(company=u.company).count():
                return HttpResponseRedirect("/dlg/no_more_unit/")
            
            un=uf.cleaned_data['unit_name']
            mb=uf.cleaned_data['mobile']
            ct=cf.cleaned_data['card_type']
            cn=cf.cleaned_data['cardno']
            pid=request.POST.get('product_id')
            
            try:
                unit=Unit(company=u.company,unit_name=un,mobile=mb)
                unit.save()
                
                if ct=='1':
                    cv=CardValue(unit=unit,cardno=cn,amount=0)
                    cv.save()
                elif ct=='2':
                    p=Product.objects.get(id=pid)
                    ct=CardTimes(unit=unit,cardno=cn,product=p,times=0)
                    ct.save()
            except:
                return HttpResponseRedirect("/err/record_already_exists/")

            return HttpResponseRedirect("/business/unit/")
        else:
            return HttpResponseRedirect("/err/no_enough_information")
    else:
        if u.company.service.max_unit==Unit.objects.filter(company=u.company).count():
            return HttpResponseRedirect("/dlg/no_more_unit/")
        else:
            uf=UnitForm()
            cf=CardForm()
            uf.fields['unit_name'].widget.attrs['validate'] = "not_null"
            uf.fields['unit_name'].widget.attrs['min'] = "2"
            uf.fields['unit_name'].widget.attrs['max'] = "10"
            uf.fields['mobile'].widget.attrs['validate'] = "mobile"
            uf.fields['mobile'].widget.attrs['empty'] = "yes"
            cf.fields['cardno'].widget.attrs['validate'] = "not_null"
            cf.fields['cardno'].widget.attrs['min'] = "3"
            cf.fields['cardno'].widget.attrs['max'] = "16"
            return render_to_response('business_unit_new.html',{'uf':uf,'cf':cf},RequestContext(request))

#@login_required
#@permission_required
def unit_edit(request,unit_id):
    u=request.session['user']
    try:
        unit=Unit.objects.get(id=unit_id)
    except ObjectDoesNotExist:
        return HttpResponseRedirect("/err/no_object")
    if request.method=='POST':
        f=UnitForm(request.POST)
        if f.is_valid():
            un=f.cleaned_data['unit_name']
            mb=f.cleaned_data['mobile']
            
            unit.unit_name=un
            unit.mobile=mb

            
            try:
                unit.save()
            except:
                return HttpResponseRedirect("/err/record_already_exists/")

            return HttpResponseRedirect("/business/unit/")
        else:
            return HttpResponseRedirect("/err/no_enough_information/")
    else:
        f=UnitForm({
            'unit_name':unit.unit_name,
            'mobile':unit.mobile,
            })

        f.fields['unit_name'].widget.attrs['validate'] = "not_null"
        f.fields['unit_name'].widget.attrs['min'] = "2"
        f.fields['unit_name'].widget.attrs['max'] = "10"
        f.fields['mobile'].widget.attrs['validate'] = "mobile"
        f.fields['mobile'].widget.attrs['empty'] = "yes"
        return render_to_response('business_unit_edit.html',{'f':f,'unit':unit},RequestContext(request))

@login_required
@permission_required
def unit_view(request,unit_id):
    u=request.session['user']
    try:
        #加入公司判断，不让看别的公司客户
        unit=Unit.objects.get(company=u.company,id=unit_id)
        cvs=CardValue.objects.filter(unit=unit)
        cts=CardTimes.objects.filter(unit=unit)
        return render_to_response('business_unit_view.html',{'unit':unit,'cvs':cvs,'cts':cts},RequestContext(request))
    except ObjectDoesNotExist:
        return HttpResponseRedirect("/err/no_object")

@login_required        
def card_value_view(request,card_id):
    u=request.session['user']
    try:
        #加入公司判断，不让看别的公司卡片
        cv=CardValue.objects.get(unit__company=u.company,id=card_id)
        cvcs=CardValueChange.objects.filter(card=cv)[0:10]
        return render_to_response('business_card_value_view.html',{'cv':cv,'cvcs':cvcs},RequestContext(request))
    except ObjectDoesNotExist:
        return HttpResponseRedirect("/err/no_object")

@login_required    
def card_times_view(request,card_id):
    u=request.session['user']
    try:
        #加入公司判断，不让看别的公司卡片
        ct=CardTimes.objects.get(unit__company=u.company,id=card_id)
        ctcs=CardTimesChange.objects.filter(card=ct)[0:10]
        return render_to_response('business_card_times_view.html',{'ct':ct,'ctcs':ctcs},RequestContext(request))
    except ObjectDoesNotExist:
        return HttpResponseRedirect("/err/no_object")

@login_required
@permission_required
def unit_delete(request,):
    u=request.session['user']
    response=HttpResponse()
    response['Content-Type']="text/javascript"
    ids=request.POST.get('ids')
    ret=0
    if ids:
        try:
            items=ids.split(',')
            Unit.objects.filter(id__in=items).filter(company=u.company).delete()
            ret=1
        except:
            ret=3 #已经产生交易
    else:
        ret=2 #没有选中项目
    response.write(ret)
    return response


@login_required
def bill_delete(request,):
    u=request.session['user']
    response=HttpResponse()
    response['Content-Type']="text/javascript"
    ids=request.POST.get('ids')
    ret=0
    if ids:
        items=ids.split(',')
        Bill.objects.filter(id__in=items).filter(branch=u.branch).exclude(status=10).delete()
        ret=1
    else:
        ret=2
    response.write(ret)
    return response

#@login_required
#@permission_required

@login_required
def bill_recharge(request):
    u=request.session['user']
    cs=CompanySetting.objects.get(company=u.company)
    if cs.card_type==1:
        return HttpResponseRedirect("/bill/recharge/value/new/")
    elif cs.card_type==2:
        return HttpResponseRedirect("/bill/recharge/times/new/")
    else:
        return render_to_response('bill_recharge.html',{},RequestContext(request))

@login_required    
def bill_sale(request):
    u=request.session['user']
    cs=CompanySetting.objects.get(company=u.company)
    if cs.card_type==1:
        return HttpResponseRedirect("/bill/sale/value/new/")
    elif cs.card_type==2:
        return HttpResponseRedirect("/bill/sale/times/new/")
    else:
        return render_to_response('bill_sale.html',{},RequestContext(request))

@login_required
def bill_recharge_value(request):
    u=request.session['user']
    list=BillRechargeValue.objects.filter(branch=u.branch)

    if request.method=='POST':
        f=SearchForm(request.POST)
        if f.is_valid():
            bid,un,dt='','',''
            y,m,d=1970,1,1
            k=f.cleaned_data['key_words']

            r1=re.findall(r'^\d{4}-\d{4}$',k)
            r2=re.findall(u'^[\u4E00-\u9FA5\uf900-\ufa2d]+$',k)
            r3=re.match(r'^(?:(?!0000)[0-9]{4}([-/.])(?:(?:0?[1-9]|1[0-2])\1(?:0?[1-9]|1[0-9]|2[0-8])|(?:0?[13-9]|1[0-2])\1(?:29|30)|(?:0?[13578]|1[02])\1(?:31))|(?:[0-9]{2}(?:0[48]|[2468][048]|[13579][26])|(?:0[48]|[2468][048]|[13579][26])00)([-/.])0?2\2(?:29))$',k)

            if r1:
                bid=r1[0]
                list=BillRechargeValue.objects.filter(branch=u.branch).filter(bill_id__icontains=bid)
            elif r2:
                un=r2[0]
                list=BillRechargeValue.objects.filter(branch=u.branch).filter(cardvalue__unit__unit_name__icontains=un)
            elif r3:
                dt=r3.group()
                tfs='%Y'+dt[4:5]+'%m'+dt[4:5]+'%d'
                t=time.strptime(dt,tfs)
                y,m,d=t[0:3]
                list=BillRechargeValue.objects.filter(branch=u.branch).filter(time_gen__startswith=datetime.date(y,m,d))
        else:
            pass
    else:
        f=SearchForm()
        f.fields['key_words'].widget.attrs['placeholder'] = "单据编号、姓名、日期"
    return render_to_response('bill_recharge_value.html',{'f':f,'list':list},RequestContext(request))

@login_required
def bill_recharge_value_new(request):
    u=request.session['user']
    if request.method=='POST':
        f=RechargeValueForm(request.POST)
        if f.is_valid():
            cid=f.cleaned_data['card_id']
            m = f.cleaned_data['money']
            a = f.cleaned_data['amount']

            
            try:
                cv=CardValue.objects.get(id=cid)
                if cv.unit.company<>u.company:
                    return HttpResponseRedirect("/err/no_object")
            except:
                return HttpResponseRedirect("/err/no_object")
            
            try:
                b=BillRechargeValue(branch=u.branch,cardvalue=cv,money=m,amount=a,status=1)
                b.save()
                return HttpResponseRedirect("/bill/recharge/value/")
            except:
                return HttpResponseRedirect("/err/no_object")
                
        else:
            return HttpResponseRedirect("/err/no_enough_information")

    else:
        f=RechargeValueForm()
        f.fields['cardno'].widget.attrs['readonly'] = True
        f.fields['cardno'].widget.attrs['class'] = 'txt bg-ll-blue'
        f.fields['cardno'].widget.attrs['validate'] = "not_null"
        return render_to_response('bill_recharge_value_new.html',{'f':f},RequestContext(request))

@login_required
#@permission_required
#@transaction.commit_manually 
def bill_recharge_value_edit(request,bill_id):
    u=request.session['user']
    try:
        b=BillRechargeValue.objects.get(branch=u.branch,id=bill_id)
        if b.status<>1:
            return HttpResponseRedirect("/err/no_object")
    except ObjectDoesNotExist:
        return HttpResponseRedirect("/err/no_object")

    if request.method=='POST':
        f=RechargeValueForm(request.POST)
        if f.is_valid():
            cid=f.cleaned_data['card_id']
            m = f.cleaned_data['money']
            a = f.cleaned_data['amount']
            
            try:
                cv=CardValue.objects.get(id=cid)
                if cv.unit.company<>u.company:
                    return HttpResponseRedirect("/err/no_object")
            except:
                return HttpResponseRedirect("/err/no_object")
            
            try:
                
                b.cardvalue=cv
                b.money=m
                b.amount=a
                b.save()
                return HttpResponseRedirect("/bill/recharge/value/")
            except:
                #transaction.rollback()            
                return HttpResponseRedirect("/err/no_object")

        else:
            return HttpResponseRedirect("/err/no_enough_information")
    else:
        f=RechargeValueForm({
            'card_id':str(b.cardvalue.id),
            'cardno':b.cardvalue.cardno,
            'money':b.money.quantize(Decimal('0.01')),
            'amount':b.amount.quantize(Decimal('0.01'))
            })
        f.fields['cardno'].widget.attrs['readonly'] = True
        f.fields['cardno'].widget.attrs['class'] = 'txt bg-ll-blue'
        f.fields['cardno'].widget.attrs['validate'] = "not_null"
        f.fields['money'].widget.attrs['validate'] = "money"
        f.fields['amount'].widget.attrs['validate'] = "money"
        return render_to_response('bill_recharge_value_edit.html',{'f':f,'b':b},RequestContext(request))

@login_required
def bill_recharge_times(request):
    u=request.session['user']
    list=BillRechargeTimes.objects.filter(branch=u.branch)

    if request.method=='POST':
        f=SearchForm(request.POST)
        if f.is_valid():
            bid,un,dt='','',''
            y,m,d=1970,1,1
            k=f.cleaned_data['key_words']

            r1=re.findall(r'^\d{4}-\d{4}$',k)
            r2=re.findall(u'^[\u4E00-\u9FA5\uf900-\ufa2d]+$',k)
            r3=re.match(r'^(?:(?!0000)[0-9]{4}([-/.])(?:(?:0?[1-9]|1[0-2])\1(?:0?[1-9]|1[0-9]|2[0-8])|(?:0?[13-9]|1[0-2])\1(?:29|30)|(?:0?[13578]|1[02])\1(?:31))|(?:[0-9]{2}(?:0[48]|[2468][048]|[13579][26])|(?:0[48]|[2468][048]|[13579][26])00)([-/.])0?2\2(?:29))$',k)

            if r1:
                bid=r1[0]
                list=BillRechargeTimes.objects.filter(branch=u.branch).filter(bill_id__icontains=bid)
            elif r2:
                un=r2[0]
                list=BillRechargeTimes.objects.filter(branch=u.branch).filter(cardvalue__unit__unit_name__icontains=un)
            elif r3:
                dt=r3.group()
                tfs='%Y'+dt[4:5]+'%m'+dt[4:5]+'%d'
                t=time.strptime(dt,tfs)
                y,m,d=t[0:3]
                list=BillRechargeTimes.objects.filter(branch=u.branch).filter(time_gen__startswith=datetime.date(y,m,d))
        else:
            pass
    else:
        f=SearchForm()
        f.fields['key_words'].widget.attrs['placeholder'] = "单据编号、姓名、日期"
    return render_to_response('bill_recharge_times.html',{'f':f,'list':list},RequestContext(request))

#@login_required
#@permission_required
#@transaction.commit_manually 

@login_required
def bill_recharge_times_new(request):
    u=request.session['user']
    if request.method=='POST':
        f=RechargeTimesForm(request.POST)
        if f.is_valid():
            cid=f.cleaned_data['card_id']
            m = f.cleaned_data['money']
            t = f.cleaned_data['times']

            
            try:
                ct=CardTimes.objects.get(id=cid)
                if ct.unit.company<>u.company:
                    return HttpResponseRedirect("/err/no_object")
            except:
                return HttpResponseRedirect("/err/no_object")
            
            try:
                b=BillRechargeTimes(branch=u.branch,cardtimes=ct,money=m,times=t,status=1)
                b.save()
                return HttpResponseRedirect("/bill/recharge/times/")
            except:
                return HttpResponseRedirect("/err/no_object")
                
        else:
            return HttpResponseRedirect("/err/no_enough_information")

    else:
        f=RechargeTimesForm()
        f.fields['cardno'].widget.attrs['readonly'] = True
        f.fields['cardno'].widget.attrs['class'] = 'txt bg-ll-blue'
        f.fields['cardno'].widget.attrs['validate'] = "not_null"
        return render_to_response('bill_recharge_times_new.html',{'f':f},RequestContext(request))

@login_required
def bill_recharge_times_edit(request,bill_id):
    u=request.session['user']
    try:
        b=BillRechargeTimes.objects.get(branch=u.branch,id=bill_id)
        if b.status<>1:
            return HttpResponseRedirect("/err/no_object")
    except ObjectDoesNotExist:
        return HttpResponseRedirect("/err/no_object")

    if request.method=='POST':
        f=RechargeTimesForm(request.POST)
        if f.is_valid():
            cid=f.cleaned_data['card_id']
            m = f.cleaned_data['money']
            t = f.cleaned_data['times']
            
            try:
                ct=CardTimes.objects.get(id=cid)
                if ct.unit.company<>u.company:
                    return HttpResponseRedirect("/err/no_object")
            except:
                return HttpResponseRedirect("/err/no_object")
            
            try:
                
                b.cardtimes=ct
                b.money=m
                b.times=t
                b.save()
                return HttpResponseRedirect("/bill/recharge/times/")
            except:
                #transaction.rollback()            
                return HttpResponseRedirect("/err/no_object")

        else:
            return HttpResponseRedirect("/err/no_enough_information")
    else:
        f=RechargeTimesForm({
            'card_id':str(b.cardtimes.id),
            'cardno':b.cardtimes.cardno,
            'money':b.money.quantize(Decimal('0.01')),
            'times':b.times
            })
        f.fields['cardno'].widget.attrs['readonly'] = True
        f.fields['cardno'].widget.attrs['class'] = 'txt bg-ll-blue'
        f.fields['cardno'].widget.attrs['validate'] = "not_null"
        f.fields['money'].widget.attrs['validate'] = "money"
        f.fields['times'].widget.attrs['validate'] = "number"
        return render_to_response('bill_recharge_times_edit.html',{'f':f,'b':b},RequestContext(request))

@login_required
#@permission_required
def bill_sale_value(request):
    u=request.session['user']
    list=BillSaleValue.objects.filter(branch=u.branch)

    if request.method=='POST':
        f=SearchForm(request.POST)
        if f.is_valid():
            bid,un,dt='','',''
            y,m,d=1970,1,1
            k=f.cleaned_data['key_words']

            r1=re.findall(r'^\d{4}-\d{4}$',k)
            r2=re.findall(u'^[\u4E00-\u9FA5\uf900-\ufa2d]+$',k)
            r3=re.match(r'^(?:(?!0000)[0-9]{4}([-/.])(?:(?:0?[1-9]|1[0-2])\1(?:0?[1-9]|1[0-9]|2[0-8])|(?:0?[13-9]|1[0-2])\1(?:29|30)|(?:0?[13578]|1[02])\1(?:31))|(?:[0-9]{2}(?:0[48]|[2468][048]|[13579][26])|(?:0[48]|[2468][048]|[13579][26])00)([-/.])0?2\2(?:29))$',k)

            if r1:
                bid=r1[0]
                list=BillSaleValue.objects.filter(branch=u.branch).filter(bill_id__icontains=bid)
            elif r2:
                un=r2[0]
                list=BillSaleValue.objects.filter(branch=u.branch).filter(unit__unit_name__icontains=un)
            elif r3:
                dt=r3.group()
                tfs='%Y'+dt[4:5]+'%m'+dt[4:5]+'%d'
                t=time.strptime(dt,tfs)
                y,m,d=t[0:3]
                list=BillSaleValue.objects.filter(branch=u.branch).filter(time_gen__startswith=datetime.date(y,m,d))
        else:
            pass
    else:
        f=SearchForm()
        f.fields['key_words'].widget.attrs['placeholder'] = "单据编号、姓名、日期"
    return render_to_response('bill_sale_value.html',{'f':f,'list':list},RequestContext(request))

#@permission_required
#@transaction.commit_manually #放到别的装饰符后面

@login_required
def bill_sale_value_new(request):
    u=request.session['user']
    if request.method=='POST':
        f=SaleValueForm(request.POST)
        if f.is_valid():
            cid=f.cleaned_data['card_id']
            
            try:
                cv=CardValue.objects.get(id=cid)
                if cv.unit.company<>u.company:
                    return HttpResponseRedirect("/err/no_object")
                 
                pids = request.POST.getlist('product_id')
                qs=request.POST.getlist('quantity')
                ps=request.POST.getlist('price')
                a=0
                for index in range(len(pids)):
                    a+=Decimal(qs[index])*Decimal(ps[index])
    
                b=BillSaleValue(branch=u.branch,amount=a,cardvalue=cv,status=1)
                b.save()
                
                #商品
                for index in range(len(pids)):
                    bip=BillItemProduct(bill=b,product=Product.objects.get(id=pids[index]),quantity=qs[index],price=ps[index])
                    bip.save()
                return HttpResponseRedirect("/bill/sale/value/")                
            except:
                #transaction.rollback()
                return HttpResponseRedirect("/err/no_object")

        else:
            return HttpResponseRedirect("/err/no_enough_information")

    else:
        f=SaleValueForm()
        f.fields['cardno'].widget.attrs['readonly'] = True
        f.fields['cardno'].widget.attrs['class'] = 'txt bg-ll-blue'
        f.fields['cardno'].widget.attrs['validate'] = "not_null"
        return render_to_response('bill_sale_value_new.html',{'f':f},RequestContext(request))

@login_required
#@permission_required
#@transaction.commit_manually
def bill_sale_value_edit(request,bill_id):
    u=request.session['user']
    try:
        b=BillSaleValue.objects.get(branch=u.branch,id=bill_id)
        if b.status<>1:
            return HttpResponseRedirect("/err/no_object")
    except ObjectDoesNotExist:
        return HttpResponseRedirect("/err/no_object")

    if request.method=='POST':
        f=SaleValueForm(request.POST)
        if f.is_valid():
            cid=f.cleaned_data['card_id']
            try:
                cv=CardValue.objects.get(id=cid)

                pids = request.POST.getlist('product_id')
                qs=request.POST.getlist('quantity')
                ps=request.POST.getlist('price')
                a=0
                for index in range(len(pids)):
                    a+=Decimal(qs[index])*Decimal(ps[index])

                b.cardvalue=cv
                b.amount=a
                b.save()
                
                #商品
                BillItemProduct.objects.filter(bill=b).delete()
            
                for index in range(len(pids)):
                    bip=BillItemProduct(bill=b,product=Product.objects.get(id=pids[index]),quantity=qs[index],price=ps[index])
                    bip.save()
                return HttpResponseRedirect("/bill/sale/value/")    
                
            except:
                #transaction.rollback()
                return HttpResponseRedirect("/err/no_object")


        else:
            return HttpResponseRedirect("/err/no_enough_information")
    else:
        try:
            list=BillItemProduct.objects.filter(bill=b)
        except ObjectDoesNotExist:
            return HttpResponseRedirect("/err/no_object")
        f=SaleValueForm({
            'card_id':str(b.cardvalue.id),
            'cardno':b.cardvalue.cardno,
            })
        f.fields['cardno'].widget.attrs['readonly'] = True
        f.fields['cardno'].widget.attrs['class'] = 'txt bg-ll-blue'
        f.fields['cardno'].widget.attrs['validate'] = "not_null"
        return render_to_response('bill_sale_value_edit.html',{'f':f,'b':b,'list':list},RequestContext(request))

@login_required
def bill_sale_value_view(request,bill_id):
    u=request.session['user']
    try:
        b=BillSaleValue.objects.get(branch__company=u.company,id=bill_id)
        list=BillItemProduct.objects.filter(bill=b)
    except ObjectDoesNotExist:
        return HttpResponseRedirect("/err/no_object")
    finally:
        return render_to_response('bill_sale_value_view.html',{'b':b,'list':list},RequestContext(request))

@login_required
def bill_sale_times(request):
    u=request.session['user']
    list=BillSaleTimes.objects.filter(branch=u.branch)

    if request.method=='POST':
        f=SearchForm(request.POST)
        if f.is_valid():
            bid,un,dt='','',''
            y,m,d=1970,1,1
            k=f.cleaned_data['key_words']

            r1=re.findall(r'^\d{4}-\d{4}$',k)
            r2=re.findall(u'^[\u4E00-\u9FA5\uf900-\ufa2d]+$',k)
            r3=re.match(r'^(?:(?!0000)[0-9]{4}([-/.])(?:(?:0?[1-9]|1[0-2])\1(?:0?[1-9]|1[0-9]|2[0-8])|(?:0?[13-9]|1[0-2])\1(?:29|30)|(?:0?[13578]|1[02])\1(?:31))|(?:[0-9]{2}(?:0[48]|[2468][048]|[13579][26])|(?:0[48]|[2468][048]|[13579][26])00)([-/.])0?2\2(?:29))$',k)

            if r1:
                bid=r1[0]
                list=BillSaleTimes.objects.filter(branch=u.branch).filter(bill_id__icontains=bid)
            elif r2:
                un=r2[0]
                list=BillSaleTimes.objects.filter(branch=u.branch).filter(unit__unit_name__icontains=un)
            elif r3:
                dt=r3.group()
                tfs='%Y'+dt[4:5]+'%m'+dt[4:5]+'%d'
                t=time.strptime(dt,tfs)
                y,m,d=t[0:3]
                list=BillSaleTimes.objects.filter(branch=u.branch).filter(time_gen__startswith=datetime.date(y,m,d))
        else:
            pass
    else:
        f=SearchForm()
        f.fields['key_words'].widget.attrs['placeholder'] = "单据编号、姓名、日期"
    return render_to_response('bill_sale_times.html',{'f':f,'list':list},RequestContext(request))

#@login_required
#@permission_required
#@transaction.commit_manually #放到别的装饰符后面

@login_required
def bill_sale_times_new(request):
    u=request.session['user']
    if request.method=='POST':
        f=SaleTimesForm(request.POST)
        if f.is_valid():
            cid=f.cleaned_data['card_id']
            t=f.cleaned_data['times']
            try:
                ct=CardTimes.objects.get(id=cid)
                if ct.unit.company<>u.company:
                    return HttpResponseRedirect("/err/no_object")
                 
                pids = request.POST.getlist('product_id')
                qs=request.POST.getlist('quantity')

    
                b=BillSaleTimes(branch=u.branch,cardtimes=ct,times=t,status=1)
                b.save()

                return HttpResponseRedirect("/bill/sale/times/")                
            except:
                #transaction.rollback()
                return HttpResponseRedirect("/err/no_object")

        else:
            return HttpResponseRedirect("/err/no_enough_information")

    else:
        f=SaleTimesForm()
        f.fields['cardno'].widget.attrs['readonly'] = True
        f.fields['cardno'].widget.attrs['class'] = 'txt bg-ll-blue'
        f.fields['cardno'].widget.attrs['validate'] = "not_null"
        return render_to_response('bill_sale_times_new.html',{'f':f},RequestContext(request))

@login_required
#@permission_required
#@transaction.commit_manually
def bill_sale_times_edit(request,bill_id):
    u=request.session['user']
    try:
        b=BillSaleTimes.objects.get(branch=u.branch,id=bill_id)
        if b.status<>1:
            return HttpResponseRedirect("/err/no_object")
    except ObjectDoesNotExist:
        return HttpResponseRedirect("/err/no_object")

    if request.method=='POST':
        f=SaleTimesForm(request.POST)
        if f.is_valid():
            cid=f.cleaned_data['card_id']
            t=f.cleaned_data['times']
            try:
                ct=CardTimes.objects.get(id=cid)

                b.cardtimes=ct
                b.times=t
                b.save()

                return HttpResponseRedirect("/bill/sale/times/")    
                
            except:
                #transaction.rollback()
                return HttpResponseRedirect("/err/no_object")


        else:
            return HttpResponseRedirect("/err/no_enough_information")
    else:
        try:
            list=BillItemProduct.objects.filter(bill=b)
        except ObjectDoesNotExist:
            return HttpResponseRedirect("/err/no_object")
        f=SaleTimesForm({
            'card_id':str(b.cardtimes.id),
            'cardno':b.cardtimes.cardno,
            'times':b.times
            })
        f.fields['cardno'].widget.attrs['readonly'] = True
        f.fields['cardno'].widget.attrs['class'] = 'txt bg-ll-blue'
        f.fields['cardno'].widget.attrs['validate'] = "not_null"
        return render_to_response('bill_sale_times_edit.html',{'f':f,'b':b,'list':list},RequestContext(request))

#@login_required
#ret:1成功,2无此单据,3状态不符,4非本店单据
def bill_exe(request):
    u=request.session['user']
    response=HttpResponse()
    response['Content-Type']="text/javascript"
    bid=request.POST.get('id')
    tp=request.POST.get('type')
    ret=0
    if bid:
        try:
            b=Bill.objects.get(id=bid)

            #其它公司的单据不能执行
            if b.branch==u.branch:
                cursor = connection.cursor()
                for case in switch(tp):
                    if case('recharge_value'):
                        cursor.callproc("sp_recharge_value", [str(b.id),ret])
                        cursor.execute('select @_sp_recharge_value_1;')
                        data=cursor.fetchall()
                        if data:
                            for i in data:
                                ret=i[0]
                        break
                    if case('recharge_times'):
                        cursor.callproc("sp_recharge_times", [str(b.id),ret])
                        cursor.execute('select @_sp_recharge_times_1;')
                        data=cursor.fetchall()
                        if data:
                            for i in data:
                                ret=i[0]
                        break
                    if case('sale_value'):
                        cursor.callproc("sp_sale_value", [str(b.id),ret])
                        cursor.execute('select @_sp_sale_value_1;')
                        data=cursor.fetchall()
                        if data:
                            for i in data:
                                ret=i[0]
                        break
                    if case('sale_times'):
                        cursor.callproc("sp_sale_times", [str(b.id),ret])
                        cursor.execute('select @_sp_sale_times_1;')
                        data=cursor.fetchall()
                        if data:
                            for i in data:
                                ret=i[0]
                        break
                cursor.close()
            else:
                #不是本店单据
                ret=4
        except ObjectDoesNotExist:
            #无此单据
            ret=2
    else:
        #无单据号
        ret=2
    print ret
    response.write(ret)
    return response

@login_required
@permission_required
def report(request):
    t=str(datetime.date.today())
    return HttpResponseRedirect("/public/report/day/"+t)

@login_required
@permission_required
def report_day(request,day):
    u=request.session['user']
    s1001=Subject.objects.get(id='1001')
    s2205=Subject.objects.get(id='2205')
    s6001=Subject.objects.get(id='6001')
    #ia:imcome amount,ra:recharge amount,sa:sale amount
    ia=0
    ra=0
    sa=0
    
    #按日查询，未来数据量大，把这两天的数据单独存放，以供查询
    #因此只提供最近两日的按日查询
    
    
    #ts:TimeStart
    #te:TimeEnd
    #tfs:TimeFormatString
    tfs='%Y-%m-%d'
    t=time.strptime(day,tfs)
    y,m,d=t[0:3]
    
    day=datetime.datetime(y,m,d).date()
    td=datetime.datetime.now().date()
    ytd=td+datetime.timedelta(days=-1)

    if day==td:
        flag=1
    elif day==ytd:
        flag=0
    else:
        return HttpResponseRedirect("/public/report/")

    d1=day+datetime.timedelta(days=1)
    ts=day.strftime(tfs)
    te=d1.strftime(tfs)
    
    cur=connection.cursor()
    cur.callproc('sp_amount',[u.branch.id,'1001',ts,te,ia])
    cur.execute('select @_sp_amount_4;')
    data=cur.fetchall()
    if data:
        for i in data:
            ia=i[0]
    cur.callproc('sp_amount',[u.branch.id,'6001',ts,te,sa])
    cur.execute('select @_sp_amount_4;')
    data=cur.fetchall()
    if data:
        for i in data:
            sa=i[0]
    cur.callproc('sp_amount_group_hour',[u.branch.id,'1001',ts,te])
    l=cur.fetchall()
    list1=[[i+1,0] for i in range(0,24)]
    for i in l:
        list1.remove([i[0]+1,0])
        list1.insert(i[0],[i[0]+1,i[1]])
    cur.close()
        
    cur=connection.cursor() #必须新建
    cur.callproc('sp_amount_group_hour',[u.branch.id,'6001',ts,te])
    l=cur.fetchall()
    list2=[[i+1,0] for i in range(0,24)]
    #数据库将8-9点的数据统计在8点，此处将数据写入9点
    for i in l:
        list2.remove([i[0]+1,0])
        list2.insert(i[0],[i[0]+1,i[1]])    
    
    cur.close()
    connection.close()
    return render_to_response('business_report_day.html',{'td':td,'flag':flag,'ia':ia,'sa':sa,'list1':list1,'list2':list2},RequestContext(request))
    
@login_required
@permission_required
def report_month(request,month):
    u=request.session['user']
    s1001=Subject.objects.get(id='1001')
    s6001=Subject.objects.get(id='6001')
    #ia:imcome amount,sa:sale amount
    ia=0
    sa=0
    
    #month查询将来为月数据另外建表，因此允许查询任何月
    
    #ts:TimeStart
    #te:TimeEnd
    #tfs:TimeFormatString
    tfs='%Y-%m-%d'
    t=time.strptime(month,'%Y-%m')
    y,m=t[0:2]
    d=1
    
    #当月1日
    d0=datetime.datetime(y,m,d).date()
    
    #今天
    td=datetime.datetime.now().date()

    #y,m,d重新赋值
    if m==12:
        m=1
        y+=1
    else:
        m+=1
    
    #下月1日
    d1=datetime.datetime(y,m,d).date()
    ts=d0.strftime(tfs)
    te=d1.strftime(tfs)
    
    cur=connection.cursor()
    cur.callproc('sp_amount',[u.branch.id,'1001',ts,te,ia])
    cur.execute('select @_sp_amount_4;')
    data=cur.fetchall()
    if data:
        for i in data:
            ia=i[0]
    cur.callproc('sp_amount_group_day',[u.branch.id,'1001',ts,te])
    l=cur.fetchall()
    
    
    delta=d1-d0
    days=delta.days
    
    list1=[[i,0] for i in range(1,days+1)]
    for i in l:
        list1.remove([i[0],0])
        list1.insert(i[0]-1,[i[0],i[1]])
    cur.close()
        
    cur=connection.cursor()
    cur.callproc('sp_amount_group_day',[u.branch.id,'6001',ts,te])
    l=cur.fetchall()
    list2=[[i,0] for i in range(1,days+1)]
    for i in l:
        list2.remove([i[0],0])
        list2.insert(i[0]-1,[i[0],i[1]])    
    
    cur.close()
    connection.close()
    return render_to_response('business_report_month.html',{'td':td,'ia':ia,'sa':sa,'list1':list1,'list2':list2},RequestContext(request))
    
@login_required
@permission_required
def report_year(request,year):
    u=request.session['user']
    s1001=Subject.objects.get(id='1001')
    s6001=Subject.objects.get(id='6001')
    #ia:imcome amount,sa:sale amount
    ia=0
    sa=0
    
    #month查询将来为月数据另外建表，因此允许查询任何月
    
    #ts:TimeStart
    #te:TimeEnd
    #tfs:TimeFormatString

 
    y=int(year)
    m=1
    d=1
    
    #当年1日
    d0=datetime.datetime(y,m,d).date()
    
    #今天
    td=datetime.datetime.now().date()

    #y,m,d重新赋值
    y+=1
    
    #明年1月1日
    d1=datetime.datetime(y,m,d).date()
    tfs='%Y-%m-%d'
    ts=d0.strftime(tfs)
    te=d1.strftime(tfs)
    
    cur=connection.cursor()
    cur.callproc('sp_amount',[u.branch.id,'1001',ts,te,ia])
    cur.execute('select @_sp_amount_4;')
    data=cur.fetchall()
    if data:
        for i in data:
            ia=i[0]
    cur.callproc('sp_amount',[u.branch.id,'6001',ts,te,sa])
    cur.execute('select @_sp_amount_4;')
    data=cur.fetchall()
    if data:
        for i in data:
            sa=i[0]
    cur.callproc('sp_amount_group_month',[u.branch.id,'1001',ts,te])
    l=cur.fetchall()
    list1=[[i,0] for i in range(1,13)]
    for i in l:
        list1.remove([i[0],0])
        list1.insert(i[0]-1,[i[0],i[1]])
    cur.close()
        
    cur=connection.cursor()
    cur.callproc('sp_amount_group_month',[u.branch.id,'6001',ts,te])
    l=cur.fetchall()
    list2=[[i,0] for i in range(1,13)]
    for i in l:
        list2.remove([i[0],0])
        list2.insert(i[0]-1,[i[0],i[1]])    
    
    cur.close()
    connection.close()
    return render_to_response('business_report_year.html',{'td':td,'ia':ia,'sa':sa,'list1':list1,'list2':list2},RequestContext(request))

@login_required
@permission_required
def password(request):
    u=request.session['user']
    if request.method=='POST':
        f=PasswordForm(request.POST)
        if f.is_valid():
            opw=f.cleaned_data['oldpassword']
            pw1=f.cleaned_data['password1']
            pw2=f.cleaned_data['password2']
            
            if u.password==hashlib.sha1(opw).hexdigest():
                if pw1==pw2:
                    u.password=hashlib.sha1(pw2).hexdigest()
                    u.save()
                    request.session['user']=u
                    return HttpResponseRedirect("/msg/passwd_change_ok/")
                else:
                    return HttpResponseRedirect("/err/newpasswd_no_match")
            else:
                return HttpResponseRedirect("/err/oldpasswd_no_match")
        else:
            return HttpResponseRedirect("/err/no_enough_information")

    else:
        f=PasswordForm()
        f.fields['oldpassword'].widget.attrs['validate'] = 'password'
        f.fields['oldpassword'].widget.attrs['min'] = '6'
        f.fields['oldpassword'].widget.attrs['max'] = '20'
        f.fields['password1'].widget.attrs['validate'] = 'password'
        f.fields['password1'].widget.attrs['min'] = '6'
        f.fields['password1'].widget.attrs['max'] = '20'
        f.fields['password2'].widget.attrs['validate'] = 'password'
        f.fields['password2'].widget.attrs['min'] = '6'
        f.fields['password2'].widget.attrs['max'] = '20'
        return render_to_response('public_password.html',{'f':f},RequestContext(request))

@login_required
def unit_select(request):
    u=request.session['user']

    #ids是把id值传送到母窗口控件的ID，id_selector
    ids=request.GET.get('ids')
    #ns是把name值传送到母窗口控件的ID,name_selector
    ns=request.GET.get('ns')


    list=Unit.objects.filter(company=u.company)
    if request.method=='POST':
        f=SearchForm(request.POST)
        if f.is_valid():
            k=f.cleaned_data['key_words']
            list=Unit.objects.filter(company=u.company).filter(Q(mobile__icontains=k)|Q(unit_name__icontains=k))
        else:
            pass
    else:
        f=SearchForm()
    return render_to_response('win_select_unit.html',{'f':f,'list':list,'ids':ids,'ns':ns},RequestContext(request))


#@login_required

@login_required
def card_select(request):
    u=request.session['user']

    #ids是把id值传送到母窗口控件的ID，id_selector
    ids=request.GET.get('ids')
    #ns是把name值传送到母窗口控件的ID,name_selector
    ns=request.GET.get('ns')
    #ns是把name值传送到母窗口控件的ID,name_selector
    ts=request.GET.get('ts')

    list=Card.objects.filter(unit__company=u.company)
    if request.method=='POST':
        f=SearchForm(request.POST)
        if f.is_valid():
            k=f.cleaned_data['key_words']
            list=Card.objects.filter(unit__company=u.company).filter(Q(cardno__icontains=k)|Q(unit__unit_name__icontains=k))
        else:
            pass
    else:
        f=SearchForm()
    return render_to_response('win_select_card.html',{'f':f,'list':list,'ids':ids,'ns':ns,'ts':ts},RequestContext(request))
   

#@login_required

@login_required
def card_value_select(request):
    u=request.session['user']

    #ids是把id值传送到母窗口控件的ID，id_selector
    ids=request.GET.get('ids')
    #ns是把name值传送到母窗口控件的ID,name_selector
    ns=request.GET.get('ns')

    list=CardValue.objects.filter(unit__company=u.company)
    if request.method=='POST':
        f=SearchForm(request.POST)
        if f.is_valid():
            k=f.cleaned_data['key_words']
            list=CardValue.objects.filter(unit__company=u.company).filter(Q(cardno__icontains=k)|Q(unit__unit_name__icontains=k))
        else:
            pass
    else:
        f=SearchForm()
    return render_to_response('win_select_card_value.html',{'f':f,'list':list,'ids':ids,'ns':ns},RequestContext(request))

@login_required   
def card_times_select(request):
    u=request.session['user']

    #ids是把id值传送到母窗口控件的ID，id_selector
    ids=request.GET.get('ids')
    #ns是把name值传送到母窗口控件的ID,name_selector
    ns=request.GET.get('ns')

    list=CardTimes.objects.filter(unit__company=u.company)
    if request.method=='POST':
        f=SearchForm(request.POST)
        if f.is_valid():
            k=f.cleaned_data['key_words']
            list=CardTimes.objects.filter(unit__company=u.company).filter(Q(cardno__icontains=k)|Q(unit__unit_name__icontains=k))
        else:
            pass
    else:
        f=SearchForm()
    return render_to_response('win_select_card_times.html',{'f':f,'list':list,'ids':ids,'ns':ns},RequestContext(request))

@login_required
def select_product(request):
    u=request.session['user']
    
    #ids是把id值传送到母窗口控件的ID，id_selector
    ids=request.GET.get('ids')
    #ns是把name值传送到母窗口控件的ID,name_selector
    ns=request.GET.get('ns')
    
    ps=Product.objects.filter(company=u.company)
    if request.method=='POST':
        f=SearchForm(request.POST)
        if f.is_valid():
            k=f.cleaned_data['key_words']
            ps=Product.objects.filter(company=u.company).filter(product_name__icontains=k)
        else:
            pass
    else:
        f=SearchForm()
    return render_to_response('win_select_product.html',{'f':f,'ps':ps,'ids':ids,'ns':ns},RequestContext(request))

@login_required
def new_product(request):
    u=request.session['user']
    
    #ids是把id值传送到母窗口控件的ID，id_selector
    ids=request.GET.get('ids')
    #ns是把name值传送到母窗口控件的ID,name_selector
    ns=request.GET.get('ns')
    
    if request.method=='POST':
        pn=request.POST.get('product_name')
        if pn:
            p=Product(company=u.company,product_name=pn)
            p.save()
            #json暂不支持uuid格式的序列化
            json={'id':str(p.id),'product_name':p.product_name}
            return HttpResponse(simplejson.dumps(json,ensure_ascii = False))
    else:
        f=ProductForm()
        return render_to_response('win_new_product.html',{'f':f,'ids':ids,'ns':ns},RequestContext(request))
    
def err(request,err_id):
    for case in switch(err_id):
        if case(1):
            t='错误-没有权限!'
            i='对不起，您没有权限！'
            break
        if case(2):
            t='错误-对象不存在!'
            i='对不起，对象不存在！'
            break
        if case(3):
            t='错误-还没有程序！'
            i='对不起，还没有为这个对象编写程序！'
            break
        if case(4):
            t='错误-数据不正确！'
            i='对不起，数据不正确，请返回重填数据！'
            break
        if case(5):
            t='错误-信息不完整!'
            i='对不起，信息不完整，请返回补充数据！'
            break
        if case(6):
            t='错误-关键信息重复!'
            i='对不起，关键信息重复！请返回修改数据！'
            break
        if case(7):
            t='错误-原口令不正确!'
            i='对不起，原口令不正确！请返回重新填写！'
            break
        if case(8):
            t='错误-新口令不一致!'
            i='对不起，新口令不一致！请重新填写！'
            break
        if case(9):
            t='错误-手机号已存在!'
            i='对不起，手机号已存在！请重新填写！'
            break
        if case(10):
            t='错误-内部错误!'
            i='对不起，内部错误！'
            break
        if case(11):
            t='错误-软件授权已过期!'
            i='对不起，软件授权已过期！'
            break
    return render_to_response('sys_err.html',{'t':t,'i':i}, RequestContext(request))

#消息页面

def msg(request,msg_id):
    for case in switch(msg_id):
        if case(1):
            t='信息-口令更改成功!'
            i='口令更改成功！3秒钟后回主页。'
            break
    return render_to_response('sys_msg.html',{'t':t,'i':i}, RequestContext(request))

#选择对话页面

def dlg(request,dlg_id):
    for case in switch(dlg_id):
        if case(1):
            t='信息-不能再增加店铺!'
            i='店铺数已达上限，请返回，或者购买升级！'
            break
        if case(2):
            t='信息-不能再增加客户!'
            i='客户数已达上限，请返回，或者购买升级！'
            break
    return render_to_response('sys_dlg.html',{'t':t,'i':i}, RequestContext(request))

def cbill_new(request):
    u=request.session['user']
    if request.method=='POST':
        pid=f.cleaned_data['product_id']
        bid=f.cleaned_data['bank_id']
        
        try:
            cp=cProduct.objects.get(id=pid)
        except ObjectDoesNotExist:
            return HttpResponseRedirect("/err/no_object")

        try:
            id=datetime.now().strftime('%Y%m%d%H%M%S')+get_random_number(6)
            cb=cBill(id=id,company=u.company,cproduct=cp,amount=cp.price,status=1)
            cb.save()
        except:
            return HttpResponseRedirect("/err/record_already_exists/")

        return HttpResponseRedirect("/business/unit/")
    else:
        return HttpResponseRedirect("/err/no_enough_information")
     





