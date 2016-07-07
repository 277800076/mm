#coding=UTF-8
"""all models for docs
@version:$Id$
@author:rokili
"""

from django.db import models
from utils.uuidfield import UUIDField


class Keyword(models.Model):
    id=UUIDField(primary_key=True,auto=True)
    keyword_name=models.CharField(max_length=32)

class Document(models.Model):
    id=UUIDField(primary_key=True,auto=True)
    title=models.CharField(max_length=32)
    description=models.CharField(max_length=128)
    keyword=models.ManyToManyField('Keyword',verbose_name="角色")
    content=models.TextField()
    time_gen=models.DateTimeField(auto_now_add=True,db_index=True)
    time_update=models.DateTimeField(auto_now=True)
    class Meta:
        ordering=['-time_gen']

