#coding=UTF-8
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext

from utils.switchcase.sw import switch
from utils.toolkit.string import strQ2B

from models import *
from forms import *
from manage.decorators import manage_required



def document(request):
    list=Document.objects.all()
    return render_to_response('document.html',{'list':list},RequestContext(request))

def document_list(request,sort):
    for case in switch(sort):
        if case('01'):
            k=u'会员'
            break
    list=Document.objects.filter(keyword__keyword_name=k)
    return render_to_response('document.html',{'k':k,'list':list},RequestContext(request))


def document_view(request,doc_id):
    try:
        d=Document.objects.get(id=doc_id)
    except:
        return HttpResponseRedirect("/err/no_object/")
    return render_to_response('document_view.html',{'d':d},RequestContext(request))

@manage_required
def document_new(request):
    if request.method=='POST':
        f=DocumentForm(request.POST)
        if f.is_valid():
            t=f.cleaned_data['title']
            d=f.cleaned_data['description']
            ks=f.cleaned_data['keywords']
            c=f.cleaned_data['content']
            ks=strQ2B(ks).split(',')

            try:
                doc=Document(title=t,description=d,content=c)
                doc.save()
                for i in ks:
                    k,created=Keyword.objects.get_or_create(keyword_name=i)
                    doc.keyword.add(k)
                return HttpResponseRedirect("/doc/")
            except:
                return HttpResponseRedirect("/err/record_already_exists/")
            
        else:
            return HttpResponseRedirect("/err/no_enough_information/")
    else:
        f=DocumentForm()
        f.fields['title'].widget.attrs['validate'] = 'not_null'
        f.fields['title'].widget.attrs['min'] = '2'
        f.fields['title'].widget.attrs['max'] = '32'
        f.fields['description'].widget.attrs['validate'] = 'not_null'
        f.fields['description'].widget.attrs['min'] = '5'
        f.fields['description'].widget.attrs['max'] = '128'
        f.fields['content'].widget.attrs['validate'] = 'not_null'
        f.fields['content'].widget.attrs['min'] = '5'
        return render_to_response('document_add.html',{'f':f},RequestContext(request))

@manage_required    
def document_edit(request,doc_id):
    try:
        doc=Document.objects.get(id=doc_id)
    except ObjectDoesNotExist:
        return HttpResponseRedirect("/err/no_object")   
     
    if request.method=='POST':
        f=DocumentForm(request.POST)
        if f.is_valid():
            t=f.cleaned_data['title']
            d=f.cleaned_data['description']
            ks=f.cleaned_data['keywords']
            c=f.cleaned_data['content']
            ks=strQ2B(ks).split(',')
            
            doc.title=t
            doc.description=d
            doc.content=c
            
            try:
                doc.save()
                
                doc.keyword.clear()
                for i in ks:
                    k,created=Keyword.objects.get_or_create(keyword_name=i)
                    doc.keyword.add(k)
                return HttpResponseRedirect("/doc/")
            except:
                return HttpResponseRedirect("/err/record_already_exists/")
            
        else:
            return HttpResponseRedirect("/err/no_enough_information/")
    else:
        f=DocumentForm({
            'title':doc.title,
            'description':doc.description,
            'keywords':','.join(i.keyword_name for i in doc.keyword.all()),
            'content':doc.content
            })
        f.fields['title'].widget.attrs['validate'] = 'not_null'
        f.fields['title'].widget.attrs['min'] = '2'
        f.fields['title'].widget.attrs['max'] = '32'
        f.fields['description'].widget.attrs['validate'] = 'not_null'
        f.fields['description'].widget.attrs['min'] = '5'
        f.fields['description'].widget.attrs['max'] = '128'
        f.fields['content'].widget.attrs['validate'] = 'not_null'
        f.fields['content'].widget.attrs['min'] = '5'
        return render_to_response('document_edit.html',{'f':f,'doc':doc},RequestContext(request))

@manage_required
def document_delete(request,doc_id):
    try:
        Document.objects.get(id=doc_id).delete()
    except:
        return HttpResponseRedirect("/err/no_object/")
    return HttpResponseRedirect("/doc/")
    
