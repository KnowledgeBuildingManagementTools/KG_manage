from django.db import models


# Create your models here.

class Noumenon(models.Model):
    noumenon_name = models.TextField(null=True, verbose_name="本体名称")
    noumenon_attribute = models.TextField(null=True, verbose_name="本体属性")

    def __str__(self):
        return self.noumenon_name

    class Meta:
        db_table = 'noumenon'
        verbose_name = '本体表'
        verbose_name_plural = verbose_name

class History(models.Model):
    node = models.TextField(null=True,verbose_name="节点")
    record = models.TextField(null=True,verbose_name="记录")
    time = models.DateTimeField(null=True,auto_now=True,verbose_name="时间")


    def __str__(self):
        return self.node

    class Meta:
        db_table = 'history'
        verbose_name = '历史操作表'
        verbose_name_plural = verbose_name

class Wikipedia_template(models.Model):
    id = models.AutoField(verbose_name='id', primary_key=True)
    name = models.CharField(verbose_name='模板名称', max_length=50)
    content = models.CharField(verbose_name='模板内容', max_length=5000)
    card_template = models.CharField(verbose_name='知识卡片模板内容', max_length=256, null=True)


class Require_wikipedia(models.Model):
    id = models.AutoField(verbose_name='id', primary_key=True)
    name = models.CharField(verbose_name='需求百科名称', max_length=50)
    content = models.TextField(verbose_name='需求百科内容')
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True, null=True)


class Knowledge_card(models.Model):
    id = models.AutoField(verbose_name='id', primary_key=True)
    name = models.CharField(verbose_name='需求百科名称', max_length=50)
    content = models.TextField(verbose_name='知识卡片内容')
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True, null=True)


class Card_template(models.Model):
    id = models.AutoField(verbose_name='id', primary_key=True)
    name = models.CharField(verbose_name='知识卡片模板名称', max_length=50)
    content = models.CharField(verbose_name='知识卡片模板内容', max_length=5000, null=True)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True, null=True)
