from django.db import models


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
    node = models.TextField(null=True, verbose_name="节点")
    record = models.TextField(null=True, verbose_name="记录")
    time = models.DateTimeField(null=True, auto_now=True, verbose_name="时间")

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
    knowledge_card = models.CharField(verbose_name='知识卡片', max_length=50, null=True)
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


class Project(models.Model):
    id = models.AutoField(verbose_name="id", primary_key=True)
    project_name = models.CharField(verbose_name="项目名称", max_length=100)
    creat_time = models.DateField(verbose_name="创建时间")

    def __str__(self):
        return self.id

    class Meta:
        db_table = 'project'
        verbose_name = '项目表'
        verbose_name_plural = verbose_name


class Histogram(models.Model):
    id = models.AutoField(verbose_name='id', primary_key=True)
    class_name = models.CharField(verbose_name='种类名称', max_length=50)
    time = models.CharField(verbose_name='时间', max_length=100)
    require_count = models.CharField(verbose_name='个数', max_length=50)
    project_id = models.CharField(verbose_name="项目id", max_length=100, null=True)


class Timeline(models.Model):
    id = models.AutoField(verbose_name='id', primary_key=True)
    time = models.DateField(verbose_name='时间')
    event_name = models.CharField(verbose_name='事件名称', max_length=100)
    event_content = models.CharField(verbose_name='事件内容', max_length=2000)
    project_id = models.CharField(verbose_name="项目id", max_length=100, null=True)


class Data_mining(models.Model):
    id = models.AutoField(verbose_name='id', primary_key=True)
    name = models.CharField(verbose_name='模型名称', max_length=100, null=True)
    label = models.CharField(verbose_name='节点标签', max_length=100)
    uuid = models.CharField(verbose_name='节点唯一标识', max_length=100)


class Knowledge_reasoning(models.Model):
    id = models.AutoField(verbose_name='id', primary_key=True)
    name = models.CharField(verbose_name='模型名称', max_length=100)
    start_node_uuid = models.CharField(verbose_name='开始节点', max_length=100)
    relation_type = models.CharField(verbose_name='关系类型', max_length=100)


class Correlation_analysis(models.Model):
    id = models.AutoField(verbose_name='id', primary_key=True)
    name = models.CharField(verbose_name='模型名称', max_length=100)
    start_node_uuid = models.CharField(verbose_name='开始节点', max_length=100)
    end_node_uuid = models.CharField(verbose_name='终止节点', max_length=100)
