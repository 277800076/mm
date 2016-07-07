#coding=UTF-8

from django.dispatch import dispatcher
from django.db.models.signals import post_syncdb
import models as business_app
from models import *

def init_content_group(sender,**kwargs):
    t=(
        ('0000','测试'),
        ('1000','公共'),
        ('2000','设置'),
        ('3000','业务')
       )
    cgs=ContentGroup.objects.all()
    if cgs.count()==0:
        for i in t:
            cg=ContentGroup(id=i[0],content_group_name=i[1])
            cg.save()

def init_content(sender,**kwargs):
    cg0000=ContentGroup.objects.get(id='0000') #测试
    cg1000=ContentGroup.objects.get(id='1000') #公共
    cg2000=ContentGroup.objects.get(id='2000') #设置
    cg3000=ContentGroup.objects.get(id='3000') #业务


    t=(
        ('100000',cg1000,'主页','/public/main/'),
        ('100010',cg1000,'修改口令','/public/passwd/'),
        ('100020',cg1000,'报表','/public/report/'),
        ('100021',cg1000,'日报表','/public/report/day/'),   
        ('100022',cg1000,'月报表','/public/report/month/'),   
        ('100023',cg1000,'年报表','/public/report/year/'),
        ('100090',cg1000,'帮助','/public/help/'),            

        ('200001',cg2000,'公司账户','/setting/company/'),
        
        ('200010',cg2000,'店铺管理','/setting/branch/'),
        ('200011',cg2000,'新增店铺','/setting/branch/new/'),
        ('200012',cg2000,'修改店铺','/setting/branch/edit/'),
        ('200013',cg2000,'删除店铺','/setting/branch/delete/'),
        ('200014',cg2000,'选择店铺','/setting/branch/select/'),

        ('200020',cg2000,'职员管理','/setting/user/'),
        ('200021',cg2000,'新增职员','/setting/user/new/'),
        ('200022',cg2000,'修改职员','/setting/user/edit/'),
        ('200023',cg2000,'删除职员','/setting/user/delete/'),
        
        ('200030',cg2000,'商品管理','/setting/product/'),
        ('200031',cg2000,'新增商品','/setting/product/new/'),
        ('200032',cg2000,'修改商品','/setting/product/edit/'),
        ('200033',cg2000,'删除商品','/setting/product/delete/'),
        ('200034',cg3000,'选择商品','/setting/product/select/'), #虽然前面的编号是2开始，此页却用于分店
        
        
        ('200090',cg2000,'设置','/setting/setup/'),        

        ('300010',cg3000,'客户','/business/unit/'),
        ('300011',cg3000,'新增客户','/business/unit/new/'),
        ('300012',cg3000,'修改客户','/business/unit/edit/'),
        ('300013',cg3000,'客户详细','/business/unit/view/'),
        ('300015',cg3000,'删除客户','/business/unit/delete/'),
        
        ('300020',cg3000,'充值','/bill/recharge/'),
        ('300021',cg3000,'新增充值单','/bill/recharge/new/'),
        ('300022',cg3000,'修改充值单','/bill/recharge/edit/'),
        ('300023',cg3000,'查看充值单','/bill/recharge/view/'),
        
        ('300030',cg3000,'消费','/bill/sale/'),
        ('300031',cg3000,'新增消费单','/bill/sale/new/'),
        ('300032',cg3000,'修改消费单','/bill/sale/edit/'),
        ('300033',cg3000,'查看消费单','/bill/sale/view/'),

       )
    cs=Content.objects.all()
    if cs.count()==0:
        for i in t:
            c=Content(id=i[0],content_group=i[1],content_name=i[2],url=i[3])
            c.save()

def init_app(sender,**kwargs):
    apps=App.objects.all()
    if apps.count()==0:
        t=(
           ('100010',95,'icon_password.png'),
           ('100020',85,'icon_report.png'),
           ('200010',1,'icon_branch.png'),
           ('200020',5,'icon_user.png'),
           ('200030',10,'icon_product.png'),
           ('200090',15,'icon_setting.png'),
           ('300010',35,'icon_unit.png'),
           ('300020',45,'icon_recharge.png'),
           ('300030',55,'icon_sale.png'),
           )
        for i in t:
            c=Content.objects.get(id=i[0])
            a=App(content_ptr_id=c.pk)
            a.__dict__.update(c.__dict__)
            a.display_order=i[1]
            a.icon=i[2]
            a.save()
        
        

def init_role(sender,**kwargs):
    #公共        1000
    #设置        2000
    #业务        2001
    t=(
        (1,'管理员',['1000','2000']),
        (2,'出纳',['1000','3000'])
       )
    rs=Role.objects.all()
    if rs.count()==0:
        for i in t:
            r=Role(id=i[0],role_name=i[1])
            r.save()
            r.permission.add(*i[2])

#初始化科目
def init_subject(sender,**kwargs):
    l=[]
    ss=Subject.objects.all()
    if ss.count()==0:
        s=Subject(id='1001',subject_name='现金')
        l.append(s)
        s=Subject(id='2205',subject_name='预收帐款')
        l.append(s)
        s=Subject(id='6001',subject_name='主营业务收入')
        l.append(s)
        for i in l:
            i.save()                


#初始化支付数据
#商品
def init_cproduct(sender,**kwargs):
    l=[]
    cps=cProduct.objects.all()
    if cps.count()==0:
        cp=cProduct(id='1001',product_type=1,product_name='月卡',key_num=1,price=85)
        l.append(cp)
        cp=cProduct(id='1002',product_type=1,product_name='季卡',key_num=3,price=210)
        l.append(cp)
        cp=cProduct(id='1003',product_type=1,product_name='年卡',key_num=12,price=600)
        l.append(cp)        
        for i in l:
            i.save()
#银行
def init_cbank(sender,**kwargs):
    l=[]
    cbs=cBank.objects.all()
    if cbs.count()==0:
        cb=cBank(id='alipay',type='platform',gateway='alipay',bank_name='支付宝',img_url='018351.png',is_display=1,display_order=1)
        l.append(cb)
        cb=cBank(id='tenpay',type='platform',gateway='tenpay',bank_name='财付通',img_url='028768.png',is_display=0,display_order=2)
        l.append(cb)  
        cb=cBank(id='BOCB2C',type='bank',gateway='alipay',bank_name='中国银行',img_url='035387.png',is_display=1,display_order=11)
        l.append(cb)
        cb=cBank(id='ICBCB2C',type='bank',gateway='alipay',bank_name='中国工商银行',img_url='065499.png',is_display=1,display_order=12)
        l.append(cb)
        cb=cBank(id='CMB',type='bank',gateway='alipay',bank_name='招商银行',img_url='136060.png',is_display=1,display_order=13)
        l.append(cb)
        cb=cBank(id='CCB',type='bank',gateway='alipay',bank_name='中国建设银行',img_url='185326.png',is_display=1,display_order=14)
        l.append(cb) 
        cb=cBank(id='ABC',type='bank',gateway='alipay',bank_name='中国农业银行',img_url='235525.png',is_display=1,display_order=15)
        l.append(cb)
        cb=cBank(id='SPDB',type='bank',gateway='alipay',bank_name='上海浦东发展银行',img_url='253380.png',is_display=1,display_order=16)
        l.append(cb)
        cb=cBank(id='CIB',type='bank',gateway='alipay',bank_name='兴业银行',img_url='312529.png',is_display=1,display_order=17)
        l.append(cb)
        cb=cBank(id='GDB',type='bank',gateway='alipay',bank_name='广发银行',img_url='335902.png',is_display=1,display_order=18)
        l.append(cb)
        cb=cBank(id='FDB',type='bank',gateway='alipay',bank_name='富滇银行',img_url='365104.png',is_display=1,display_order=19)
        l.append(cb)   
        cb=cBank(id='CITIC',type='bank',gateway='alipay',bank_name='中信银行',img_url='422103.png',is_display=1,display_order=20)
        l.append(cb)
        cb=cBank(id='HZCBB2C',type='bank',gateway='alipay',bank_name='杭州银行',img_url='452366.png',is_display=1,display_order=21)
        l.append(cb)
        cb=cBank(id='SHBANK',type='bank',gateway='alipay',bank_name='上海银行',img_url='534547.png',is_display=1,display_order=22)
        l.append(cb)
        cb=cBank(id='NBBANK',type='bank',gateway='alipay',bank_name='宁波银行',img_url='572970.png',is_display=1,display_order=23)
        l.append(cb)
        cb=cBank(id='SPABANK',type='bank',gateway='alipay',bank_name='平安银行',img_url='647517.png',is_display=1,display_order=24)
        l.append(cb)
        cb=cBank(id='POSTGC',type='bank',gateway='alipay',bank_name='中国邮政储蓄银行',img_url='728258.png',is_display=1,display_order=25)
        l.append(cb)
        cb=cBank(id='BJBANK',type='bank',gateway='alipay',bank_name='北京银行',img_url='755760.png',is_display=1,display_order=26)
        l.append(cb)
        cb=cBank(id='COMM',type='bank',gateway='alipay',bank_name='交通银行',img_url='802196.png',is_display=1,display_order=27)
        l.append(cb)
        cb=cBank(id='CMBC',type='bank',gateway='alipay',bank_name='民生银行',img_url='824321.png',is_display=1,display_order=28)
        l.append(cb)         
        for i in l:
            i.save()

#初始化服务
def init_service(sender,**kwargs):
    l=[]
    ss=Service.objects.all()
    if ss.count()==0:
        s=Service(id='1',service_name='免费版',max_branch=1,max_unit=1000)
        l.append(s)
        s=Service(id='2',service_name='正式版',max_branch=5,max_unit=10000)
        l.append(s)       
        for i in l:
            i.save()

post_syncdb.connect(init_content_group,sender=business_app)  
post_syncdb.connect(init_content,sender=business_app)
post_syncdb.connect(init_app,sender=business_app) 
post_syncdb.connect(init_role,sender=business_app)
post_syncdb.connect(init_subject,sender=business_app)
post_syncdb.connect(init_cproduct,sender=business_app)
post_syncdb.connect(init_cbank,sender=business_app)
post_syncdb.connect(init_service,sender=business_app)


