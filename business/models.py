#coding=UTF-8
"""all models for business
@version:$Id$
@author:rokili
"""

#基础数据开始
from django.db import models
from utils.uuidfield import UUIDField
from django.utils import timezone
from utils.toolkit.datetime import add_months
from utils.toolkit.model import KnowsChild

class ContentGroup(models.Model):
    id=models.CharField(primary_key=True,max_length=4)
    content_group_name=models.CharField(max_length=10)

class Content(models.Model):
    id=models.CharField(primary_key=True,max_length=6)
    content_group=models.ForeignKey('ContentGroup')
    content_name=models.CharField(max_length=10)
    url=models.CharField(max_length=30)
class App(Content):
    display_order=models.IntegerField()
    icon=models.CharField(max_length=30)
    class Meta:
        ordering=['display_order']

class Role(models.Model):
    id=models.IntegerField(primary_key=True)
    role_name=models.CharField(max_length=10)
    permission=models.ManyToManyField('ContentGroup')
    def __unicode__(self):
        return self.role_name

class Service(models.Model):
    id=models.CharField(primary_key=True,max_length=1)
    service_name=models.CharField(max_length=30,verbose_name="使用版本")
    max_branch=models.IntegerField(verbose_name="最多店铺数")
    max_unit=models.IntegerField(verbose_name="最多客户数")

class Company(models.Model):
    id=UUIDField(primary_key=True,auto=True)
    company_name=models.CharField(max_length=30,verbose_name="公司名称")
    time_gen=models.DateTimeField(auto_now_add=True)
    time_expired=models.DateTimeField(null=False)
    service=models.ForeignKey('Service')


class MaxID(models.Model):
    id=UUIDField(primary_key=True,auto=True)
    company=models.OneToOneField('Company')
    branch_max_id=models.IntegerField()
    user_max_id=models.IntegerField()
    unit_max_id=models.IntegerField()
    product_max_id=models.IntegerField()
    bill_max_id=models.IntegerField()

class CompanySetting(models.Model):
    id=UUIDField(primary_key=True,auto=True)
    company=models.OneToOneField('Company')
    card_type=models.IntegerField()
    #custom_price=models.BooleanField()




#key_num是关键指标
#如果是时间,1表示1个月,3表示3个月,12表示1年
#如果是短信,1表示1条，100表示100条
class cProduct(models.Model):
    TYPE_CHOICES=(
        (1,'时间'),                
        (2,'短信'),
    )
    id=models.CharField(primary_key=True,max_length=4)
    product_type=models.IntegerField(choices=TYPE_CHOICES)
    product_name=models.CharField(verbose_name='商品名称',max_length=20)
    key_num=models.IntegerField()
    price=models.DecimalField(verbose_name='价格',max_digits=19,decimal_places=6)

#type:'platform','bank'
class cBank(models.Model):
    id=models.CharField(primary_key=True,max_length=20)
    type=models.CharField(max_length=10)
    gateway=models.CharField(max_length=10)
    bank_name=models.CharField(verbose_name='银行',max_length=20)
    img_url=models.CharField(max_length=10)
    is_display=models.BooleanField()
    display_order=models.IntegerField()
    class Meta:
        ordering=['display_order']

class cBill(models.Model):
    STATUS_CHOICES=(
        (0,'已删除'),                
        (1,'未付款'),
        (10,'已付款'),
    )
    id=models.CharField(verbose_name='订单编号',primary_key=True,max_length=22)
    company=models.ForeignKey('Company')
    cproduct=models.ForeignKey('cProduct')
    cbank=models.ForeignKey('cBank')
    amount=models.DecimalField(verbose_name='金额',max_digits=19,decimal_places=6)
    time_gen=models.DateTimeField(auto_now_add=True,db_index=True)
    time_update=models.DateTimeField(auto_now=True)
    status=models.IntegerField(choices=STATUS_CHOICES)
    class Meta:
        ordering=['-id']
    def exe(self):
        #product_type=1是时间卡
        if self.cproduct.product_type==1:
            c=self.company
            #如果是免费客户
            #修改为正式版，同时把过期日期修改成从今天起key_num个月以后
            timestart=timezone.now()
            if c.service.id=='1':
                c.service=Service.objects.get(id='2')

            #如果是正式版
            elif c.service.id=='2':
                if c.time_expired>timezone.now():
                    timestart=c.time_expired
    
            c.time_expired=add_months(timestart,self.cproduct.key_num)
            c.save()
            self.status=10
            self.save()
                     
             
class Branch(models.Model):
    id=UUIDField(primary_key=True,auto=True)
    company=models.ForeignKey('Company')
    branch_id=models.CharField(max_length=3,null=True)
    branch_name=models.CharField(max_length=20,verbose_name='店铺')
    is_base=models.BooleanField()
    class Meta:
        unique_together = (('company','branch_name'),)
        ordering=['branch_id'] 

class User(models.Model):
    id=UUIDField(primary_key=True,auto=True)
    company=models.ForeignKey('Company')
    branch=models.ForeignKey('Branch')
    user_id=models.CharField(max_length=3,null=True)
    real_name=models.CharField(max_length=5,verbose_name="真实姓名")
    mobile=models.CharField(max_length=11,unique=True,verbose_name="手机号")
    password=models.CharField(max_length=40,verbose_name="密码")
    role=models.ManyToManyField(Role,verbose_name="角色")
    is_admin=models.BooleanField()
    class Meta:
        ordering=['user_id'] 

class Unit(models.Model):
    """Unit
    Unit is one of the base class for client,supplier and employee
    """
    id=UUIDField(primary_key=True,auto=True)
    company=models.ForeignKey('Company')
    unit_id=models.CharField(verbose_name='客户编号',max_length=7,null=True,db_index=True)
    unit_name=models.CharField(verbose_name='客户名称',max_length=10)
    mobile=models.CharField(verbose_name='手机',max_length=11,null=True)
    time_gen=models.DateTimeField(auto_now_add=True,verbose_name='创建时间')
    class Meta:
        unique_together = (('company','mobile'),)
        ordering=['-unit_id'] 

class Product(models.Model):
    id=UUIDField(primary_key=True,auto=True)
    company=models.ForeignKey('Company')
    product_id=models.CharField(max_length=7,null=True)
    product_name=models.CharField(verbose_name='商品名称',max_length=50)
    class Meta:
        unique_together = (('company','product_name'),)
        ordering=['-product_id'] 

#新增卡随客户删除而删除，只要发生过交易的卡就不能被删除了
class Card(KnowsChild):
    id=UUIDField(primary_key=True,auto=True)
    unit=models.ForeignKey('Unit')
    cardno=models.CharField(verbose_name='卡号',max_length=16)
    time_gen=models.DateTimeField(auto_now_add=True,verbose_name='创建时间')  

class CardValue(Card):
    amount=models.DecimalField(verbose_name='金额',max_digits=19,decimal_places=6)

class CardTimes(Card):
    product=models.ForeignKey('Product',on_delete=models.PROTECT)
    times=models.IntegerField()
    
#财务
class Subject(models.Model):
    id=models.CharField(primary_key=True,max_length=4)
    subject_name=models.CharField(max_length=10,null=True)
    
class SubjectBranch(models.Model):
    id=UUIDField(primary_key=True,auto=True)
    branch=models.ForeignKey('Branch')
    subject=models.ForeignKey('Subject')
    amount=models.DecimalField(max_digits=19,decimal_places=6)


    
#bill_id订单号，采用自编号
class Bill(models.Model):
    STATUS_CHOICES=(
        (0,'已删除'),                
        (1,'新单据'),
        (5,'已审核'),
        (10,'已执行'),
    )
    id=UUIDField(primary_key=True,auto=True)
    branch=models.ForeignKey('Branch',on_delete=models.PROTECT)
    bill_id=models.CharField(max_length=9,null=True,db_index=True)
    time_gen=models.DateTimeField(auto_now_add=True,db_index=True)
    time_update=models.DateTimeField(auto_now=True)
    status=models.IntegerField(choices=STATUS_CHOICES)
    class Meta:
        ordering=['-bill_id']

#money：现金，amount：充值
class BillRechargeValue(Bill):
    cardvalue=models.ForeignKey('CardValue',on_delete=models.PROTECT)
    money=models.DecimalField(verbose_name='收款',max_digits=19,decimal_places=6)
    amount=models.DecimalField(verbose_name='充值',max_digits=19,decimal_places=6)

class BillRechargeTimes(Bill):
    cardtimes=models.ForeignKey('CardTimes',on_delete=models.PROTECT)
    money=models.DecimalField(verbose_name='收款',max_digits=19,decimal_places=6)
    times=models.IntegerField(verbose_name='次数')

class BillSaleValue(Bill):
    cardvalue=models.ForeignKey('CardValue',on_delete=models.PROTECT)
    amount=models.DecimalField(verbose_name='金额',max_digits=19,decimal_places=6)

class BillSaleTimes(Bill):
    cardtimes=models.ForeignKey('CardTimes',on_delete=models.PROTECT)
    times=models.IntegerField(verbose_name='次数')

class BillItemProduct(models.Model):
    id=UUIDField(primary_key=True,auto=True)
    bill=models.ForeignKey('Bill')
    product=models.ForeignKey('Product',on_delete=models.PROTECT)
    quantity=models.DecimalField(max_digits=19,decimal_places=6)
    price=models.DecimalField(max_digits=19,decimal_places=6)

 

#财务系统
class Ledger(models.Model):
    id=UUIDField(primary_key=True,auto=True)
    bill=models.OneToOneField('Bill')
    time_gen=models.DateTimeField(db_index=True)

class SubjectBranchChange(models.Model):
    id=UUIDField(primary_key=True,auto=True)
    ledger=models.ForeignKey('Ledger')
    subject_branch=models.ForeignKey('SubjectBranch')
    money=models.DecimalField(max_digits=19,decimal_places=6)
    class Meta:
        ordering=['-ledger__time_gen']

class CardValueChange(models.Model):
    id=UUIDField(primary_key=True,auto=True)
    ledger=models.ForeignKey('Ledger')
    card=models.ForeignKey('CardValue',on_delete=models.PROTECT)
    money=models.DecimalField(max_digits=19,decimal_places=6)
    class Meta:
        ordering=['-ledger__time_gen']
    
class CardTimesChange(models.Model):
    id=UUIDField(primary_key=True,auto=True)
    ledger=models.ForeignKey('Ledger')
    card=models.ForeignKey('CardTimes',on_delete=models.PROTECT)
    times=models.IntegerField()
    class Meta:
        ordering=['-ledger__time_gen']

class Log(models.Model):
    id=UUIDField(primary_key=True,auto=True)
    operation=models.CharField(max_length=100)
    time_gen=models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering=['time_gen']