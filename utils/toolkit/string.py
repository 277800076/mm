#coding=UTF-8

#全角转半角
def strQ2B(ustring):
    rstring=''
    for i in ustring:
        inside_code=ord(i)
    
        #处理全角空格
        if inside_code==0x3000:
            inside_code=0x0020
        else:
            #处理其他字符，全角内部码减去一定数字就得到半角
            inside_code-=0xfee0
            #转完之后不是半角字符返回原来的字符
            if inside_code<0x0020 or inside_code>0x7e:   
                rstring += i
            else:
                rstring += unichr(inside_code)
    return rstring