#coding=UTF-8
from datetime import datetime
'''
Created on 2014-10-17

settings.py里加入

TEMPLATE_CONTEXT_PROCESSORS = (
   'business.processors.custom_proc',
)

所有类似
return render_to_response ('main.html',{'c':u.company,'a':a}, RequestContext(request))
都注入了新的参数u

@author: 李璟潭
'''
def custom_proc(request):
    try:
        u=request.session['user']
        h=datetime.now().hour
        if h<6:
            hi='凌晨好'
        elif h<8:
            hi='早晨好'
        elif h<12:
            hi='上午好'
        elif h<14:
            hi='中午好'
        elif h<17:
            hi='下午好'
        elif h<19:
            hi='傍晚好'
        elif h<22:
            hi='晚上好'
        else:
            hi='夜里好' 
        return {'u': u,'hi':hi,}
    except:
        return {}