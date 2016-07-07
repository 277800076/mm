#coding=UTF-8
from django.db import models
'''
必须生成表以后
class Animal(KnowsChild):
    def speak(self):
        print "Generic Animal Sound"
 
class Dog(Animal):
    def speak(self):
        print "Woof!"
 
class Cat(Animal):
    def speak(self):
        print "Meow!"

Dog.objects.create()
Dog.objects.create()
Cat.objects.create()
for animal in Animal.objects.all():
    animal.as_child().speak()
'''
#所有继承此类的某类都会新增subclass字段，用来存放继承某类的子类的名字，以便知道究竟是谁继承了。
class KnowsChild(models.Model):
    #存子类名字
    subclass = models.CharField(max_length=128) 
 
    class Meta:
        abstract = True
 
    def as_child(self):
        return getattr(self, self.subclass)
 
    def save(self, *args, **kwargs):
        # save what kind we are.
        self.subclass = self.__class__.__name__.lower() 
        super(KnowsChild, self).save(*args, **kwargs)
