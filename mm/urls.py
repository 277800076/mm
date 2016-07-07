#coding=UTF-8
from django.conf.urls import patterns, include, url
from django.conf import settings
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    (r'^manage/',include('manage.urls')),
    (r'^doc/',include('doc.urls')),
    (r'^images/(?P<path>.*)$', 'django.views.static.serve',{'document_root': settings.IMAGE_DIR}),
    (r'^css/(?P<path>.*)$', 'django.views.static.serve',{'document_root': settings.CSS_DIR}),
    (r'^js/(?P<path>.*)$', 'django.views.static.serve',{'document_root': settings.JS_DIR}),
    (r'^docs/(?P<path>.*)$', 'django.views.static.serve',{'document_root': settings.DOC_DIR}),
    

    (r'^$', 'business.views.index'),
    (r'^register/$', 'business.views.register'),
    (r'^register_ok/$', 'business.views.register_ok'),
    (r'^win_login/$', 'business.views.win_login'),
    (r'^login/$', 'business.views.login'),
    (r'^auth/$', 'business.views.auth'),

    (r'^alipay/return/$','business.views.alipay_return_url'),
    (r'^alipay/notify/$','business.views.alipay_notify_url'),

    
    (r'^public/main/$','business.views.main'),
    (r'^public/report/$','business.views.report'),
    (r'^public/report/day/((?:(?!0000)[0-9]{4}-(?:(?:0[1-9]|1[0-2])-(?:0[1-9]|1[0-9]|2[0-8])|(?:0[13-9]|1[0-2])-(?:29|30)|(?:0[13578]|1[02])-31)|(?:[0-9]{2}(?:0[48]|[2468][048]|[13579][26])|(?:0[48]|[2468][048]|[13579][26])00)-02-29))$','business.views.report_day'),
    (r'^public/report/month/(\d{4}-(?:0[1-9]|1[0-2]))$','business.views.report_month'),
    (r'^public/report/year/(\d{4})$','business.views.report_year'),
    (r'^public/passwd/$','business.views.password'),
    (r'^public/help/$','business.views.help'),
    (r'^public/version/$','business.views.version'),
    (r'^public/buy/$','business.views.buy'),
    (r'^public/confirm/(\d{8}-\d{6}-\d{6})$','business.views.confirm'),
    (r'^public/pay/$','business.views.pay'),
    (r'^public/verify/(\d{8}-\d{6}-\d{6})$','business.views.verify'),

    
    (r'^setting/company/$','business.views.company_view'),
    
    (r'^setting/branch/$','business.views.branch'),
    (r'^setting/branch/new/$', 'business.views.branch_new'),
    (r'^setting/branch/edit/(\w{32})$', 'business.views.branch_edit'),
    (r'^setting/branch/delete/$', 'business.views.branch_delete'),
    (r'^setting/branch/select/$', 'business.views.branch_select'),
    
    (r'^setting/user/$', 'business.views.user'),
    (r'^setting/user/new/$', 'business.views.user_new'),
    (r'^setting/user/delete/$', 'business.views.user_delete'),
    (r'^setting/user/edit/(\w{32})$', 'business.views.user_edit'),

    (r'^setting/product/$', 'business.views.product'),
    (r'^setting/product/new/$', 'business.views.product_new'),
    (r'^setting/product/delete/$', 'business.views.product_delete'),
    (r'^setting/product/edit/(\w{32})$', 'business.views.product_edit'),

    (r'^setting/setup/$', 'business.views.setup'),

    (r'^business/unit/$', 'business.views.unit'),
    (r'^business/unit/new/$', 'business.views.unit_new'),
    (r'^business/unit/delete/$', 'business.views.unit_delete'),
    (r'^business/unit/edit/(\w{32})$', 'business.views.unit_edit'),
    (r'^business/unit/view/(\w{32})$', 'business.views.unit_view'),
   
    (r'^bill/recharge/$', 'business.views.bill_recharge'),

    (r'^bill/recharge/view/(\w{32})$', 'business.views.bill_recharge_view'),

    (r'^bill/recharge/value/$', 'business.views.bill_recharge_value'),
    (r'^bill/recharge/value/new/$', 'business.views.bill_recharge_value_new'),
    (r'^bill/recharge/value/edit/(\w{32})$', 'business.views.bill_recharge_value_edit'),
    
    (r'^bill/recharge/times/$', 'business.views.bill_recharge_times'),
    (r'^bill/recharge/times/new/$', 'business.views.bill_recharge_times_new'),
    (r'^bill/recharge/times/edit/(\w{32})$', 'business.views.bill_recharge_times_edit'),
    
    (r'^bill/sale/$', 'business.views.bill_sale'),
    (r'^bill/sale/value/view/(\w{32})$', 'business.views.bill_sale_value_view'),

    (r'^bill/sale/value/$', 'business.views.bill_sale_value'),
    (r'^bill/sale/value/new/$', 'business.views.bill_sale_value_new'),
    (r'^bill/sale/value/edit/(\w{32})$', 'business.views.bill_sale_value_edit'),
    
    (r'^bill/sale/times/$', 'business.views.bill_sale_times'),
    (r'^bill/sale/times/new/$', 'business.views.bill_sale_times_new'),
    (r'^bill/sale/times/edit/(\w{32})$', 'business.views.bill_sale_times_edit'),
            
    (r'^bill/delete/$','business.views.bill_delete'),
    (r'^bill/exe/$','business.views.bill_exe'),

    (r'^unit/select/$', 'business.views.unit_select'),
    (r'^unit/new/$', 'business.views.new_unit'),

    (r'^card/select/$', 'business.views.card_select'),
    
    (r'^card/value/select/$', 'business.views.card_value_select'),
    (r'^card/times/select/$', 'business.views.card_times_select'),      
    
    (r'^card/value/view/(\w{32})$', 'business.views.card_value_view'),
    (r'^card/times/view/(\w{32})$', 'business.views.card_times_view'),   
    
    (r'^product/select/$', 'business.views.select_product'),
    (r'^product/new/$', 'business.views.new_product'),



    
    (r'^err/no_access/$', 'business.views.err',{'err_id':1}),
    (r'^err/no_object/$', 'business.views.err',{'err_id':2}),
    (r'^err/no_program/$', 'business.views.err',{'err_id':3}),
    (r'^err/no_right/$', 'business.views.err',{'err_id':4}),
    (r'^err/no_enough_information/$', 'business.views.err',{'err_id':5}),
    (r'^err/record_already_exists/$', 'business.views.err',{'err_id':6}),
    (r'^err/oldpasswd_no_match/$', 'business.views.err',{'err_id':7}),
    (r'^err/newpasswd_no_match/$', 'business.views.err',{'err_id':8}),
    (r'^err/mobile_existed/$', 'business.views.err',{'err_id':9}),
    (r'^err/internal_error/$', 'business.views.err',{'err_id':10}),
    (r'^err/expired/$', 'business.views.err',{'err_id':11}),
    
    (r'^msg/passwd_change_ok/$', 'business.views.msg',{'msg_id':1}),
    
    (r'^dlg/no_more_branch/$', 'business.views.dlg',{'dlg_id':1}),
    (r'^dlg/no_more_unit/$', 'business.views.dlg',{'dlg_id':2}),

)
