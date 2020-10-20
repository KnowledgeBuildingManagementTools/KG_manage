import os
import json
import math

from django.views import View
from django.http import JsonResponse, HttpResponse
from kg_code_manage import models, myforms
from django.shortcuts import render, redirect
import requests

project_base_path = os.getcwd()


def index(request):
    return render(request, 'index.html')


def model(request):
    if request.method == "GET":
        return render(request, "model_create.html")
    else:
        # 上传文件
        file_type = request.POST.get('file_type')
        file_obj = request.FILES.get('file')
        file_path = os.path.join(project_base_path, 'upload_file', file_obj.name)
        try:
            with open(file_path, 'wb') as f:
                for chunk in file_obj.chunks():
                    f.write(chunk, )
        except Exception as e:
            pass

        # 请求文件抽取的结果数据
        res_data = [{
            "id": "10002",
            "head_node": "异构知识的统一存储、映射、检索和接口技术",
            "head_type": "项目",
            "relationship": "技术指标",
            "tail_node": "异构知识种类不少于5种；知识的存储容量规模达到万级，不少于1GB；",
            "tail_type": "技术指标"
        }, {
            "id": "10003",
            "head_node": "异构知识的统一存储、映射、检索和接口技术",
            "head_type": "项目",
            "relationship": "专业领域",
            "tail_node": "探测与识别",
            "tail_type": "专业领域"
        }, {
            "id": "10004",
            "head_node": "异构知识的统一存储、映射、检索和接口技术",
            "head_type": "项目",
            "relationship": "专业领域",
            "tail_node": "计算机与软件    ",
            "tail_type": "专业领域"
        }, {
            "id": "10005",
            "head_node": "异构知识的统一存储、映射、检索和接口技术",
            "head_type": "项目",
            "relationship": "专业领域",
            "tail_node": "探测与识别",
            "tail_type": "专业领域"
        }]
        res = {'code': 0, 'data': res_data}

        return JsonResponse(res)


def knowledge(request):
    if request.method == "GET":
        return render(request, 'knowledge_creat.html')

def map_preview(request):
    """ 抽取的信息知识图谱预览 """
    return render(request, 'map_previews.html')

def knowledge_wikipedia(request):
    """ 知识百科 """
    return render(request, 'knowledge_wikipedia.html')

class Wikipedia_template(View):
    def get(self, request):
        all_data = []
        for single_data in models.Wikipedia_template.objects.filter():
            single_data_dict = {}
            id = single_data.id
            name = single_data.name
            content = single_data.content
            card_template = single_data.card_template
            if card_template:
                card_id_list = [int(card_id) for card_id in card_template.split('，')]
                card_name_list = []
                for sg_card_id in card_id_list:
                    if models.Card_template.objects.filter(pk=sg_card_id).exists():
                        sg_card_name = models.Card_template.objects.filter(pk=sg_card_id).first().name
                        card_name_list.append(sg_card_name)
                mu_card_name = '，'.join(card_name_list)
            else:
                mu_card_name = ''

            single_data_dict["id"] = id
            single_data_dict["name"] = name
            single_data_dict["content"] = content
            single_data_dict["mu_card_name"] = mu_card_name
            all_data.append(single_data_dict)

        """
        all_data[0].card_template_set.all()

        res_data = []
        for single_data in all_data:
            single_data_dict = {}
            id = single_data.id
            name = single_data.name
            content = single_data.content
            card_list = []
            for sg_card in single_data.card_template_set.all():
                card_list.append(sg_card.name)
            mu_card_name = '，'.join(card_list)

            single_data_dict["id"] = id
            single_data_dict["name"] = name
            single_data_dict["content"] = content
            single_data_dict["mu_card_name"] = mu_card_name
            res_data.append(single_data_dict)
        """

        return render(request, 'wikipedia_template.html', {'all_data': all_data})

    def post(self, request):
        """ 批量删除 """
        id_list = request.POST.getlist('checked')
        data_obj = models.Wikipedia_template.objects.filter(id__in=id_list)
        data_obj.delete()
        return redirect(request.path)

def search_wikipedia(request):
    """ 百科模板 - 搜索 """
    template_name = request.GET.get("template_name")
    all_data = models.Wikipedia_template.objects.filter(name__icontains=template_name)
    return render(request, 'wikipedia_template.html', {'all_data': all_data})


class Add_wikipedia(View):
    def get(self, request):
        card_list = models.Card_template.objects.filter()
        return render(request, 'add_wikipedia_template.html', {"card_list": card_list})
    def post(self, request):
        name = request.POST.get("name")
        content = request.POST.get("content")
        card_template = '，'.join(request.POST.getlist("card_template"))
        models.Wikipedia_template.objects.create(name=name, content=content, card_template=card_template)
        return redirect('wikipedia_template')

class Edit_wikipedia(View):
    def get(self, request, id):
        Wikipedia_template = models.Wikipedia_template.objects.filter(pk=id).first()
        card_id_list = Wikipedia_template.card_template.split('，')

        selected_card_list = models.Card_template.objects.filter(id__in=card_id_list)
        selected_card_id = [sg_card.id for sg_card in selected_card_list]

        all_card_list = models.Card_template.objects.filter()
        return render(request, 'edit_wikipedia_template.html', {"Wikipedia_template": Wikipedia_template, "all_card_list": all_card_list, "selected_card_id": selected_card_id})

    def post(self, request):
        name = request.POST.get("name")
        content = request.POST.get("content")
        card_template = '，'.join(request.POST.getlist("card_template"))
        models.Wikipedia_template.objects.create(name=name, content=content, card_template=card_template)
        return redirect('wikipedia_template')


def add_edit_wikipedia(request, n=None):
    """ 百科模板 - 添加/编辑 """
    remark = '模板、知识卡片模板'
    data_obj = models.Wikipedia_template.objects.filter(pk=n).first()
    label = '编辑模板信息' if n else '添加模板信息'
    if request.method == 'GET':
        inventory_obj = myforms.WikipediaTemplateModelForm(instance=data_obj)
        return render(request, 'add_edit_general.html', {'general_obj': inventory_obj, 'label': label, 'remark': remark})
    else:
        inventory_obj = myforms.WikipediaTemplateModelForm(request.POST, instance=data_obj)
        if inventory_obj.is_valid():
            inventory_obj.save()
            return redirect('wikipedia_template')
        else:
            return render(request, 'add_edit_general.html', {'general_obj': inventory_obj, 'label': label})

def delete_wikipedia(request, n):
    """ 百科模板 - 删除 """
    models.Wikipedia_template.objects.filter(id=n).delete()
    return redirect('wikipedia_template')

def preview_wikipedia(request, n):
    """ 百科模板 - 预览 """
    template_obj = models.Wikipedia_template.objects.filter(pk=n).first()
    template_name = template_obj.name
    template_content = template_obj.content
    all_content_list = template_content.split("，")[1:]

    # 知识卡片模板内容
    # card_template = template_obj.knowledge_card
    # all_card_list = card_template.split("，")
    # card_dict = {"left": all_card_list[:int(len(all_card_list)/2)], "right": all_card_list[int(len(all_card_list)/2)+1:]}

    return render(request, 'template_preview.html', {"template_name": template_name, "data_list": all_content_list})

class Require_wikipedia(View):
    """ 需求百科 - 展示 """
    def get(self,request):
        # 查询所有的模板名称
        template_name_list = [{"id": sg_tem.id, "name": sg_tem.name} for sg_tem in models.Wikipedia_template.objects.filter()]

        # 查询所有的需求百科
        all_wikipedia_data = models.Require_wikipedia.objects.filter()
        res_data = [{"id": sg_data.id, "name": sg_data.name, "create_time": sg_data.create_time} for sg_data in all_wikipedia_data]
        return render(request, 'require_wikipedia.html', {"template_name_list": template_name_list, "res_data": res_data})

    def post(self, request):
        choiced_template_id = request.POST.get("template_choiced")
        template_content = models.Wikipedia_template.objects.filter(id=choiced_template_id).first().content
        template_content_list = template_content.split('，')
        return render(request, 'add_require_wikipedia.html', {'template_content_list': template_content_list, 'template_content': template_content})

def add_require_wikipedia(request):
    """ 需求百科 - 添加 """
    id = request.POST.get("id")
    name = request.POST.get("name")
    all_tem = request.POST.get("all_tem")
    template_content_list = all_tem.split('，')
    template_content_dict = {}
    for sg_tem_con in template_content_list:
        template_content_dict[sg_tem_con] = request.POST.get(sg_tem_con)
    template_content_str = json.dumps(template_content_dict)

    if id:
        models.Require_wikipedia.objects.filter(id=id).update(name=name, content=template_content_str)
    else:
        models.Require_wikipedia.objects.create(name=name, content=template_content_str)
    return redirect('require_wikipedia')

def preview_require_wikipedia(request, id):
    """ 需求百科 - 预览 """
    require_wikipedia_obj = models.Require_wikipedia.objects.filter(pk=id).first()
    name = require_wikipedia_obj.name
    content = json.loads(require_wikipedia_obj.content)
    res_data = [{"key": key, "value": value} for key, value in content.items()]
    return render(request, 'require_wikipedia_preview.html', {"name": name, "res_data": res_data})

def edit_require_wikipedia(request, id):
    """ 需求百科 - 编辑 """
    require_wikipedia_obj = models.Require_wikipedia.objects.filter(pk=id).first()
    content_dict = json.loads(require_wikipedia_obj.content)
    content = [{"key": key, "value": value} for key, value in content_dict.items()]
    name = require_wikipedia_obj.name
    id = require_wikipedia_obj.id
    all_tem = '，'.join([key for key, value in content_dict.items()])
    return render(request, 'edit_require_wikipedia.html', {'id': id, 'all_tem': all_tem, 'name': name, 'content': content})

def delete_require_wikipedia(request, id):
    """ 需求百科 - 删除 """
    models.Require_wikipedia.objects.filter(pk=id).delete()
    return redirect('require_wikipedia')

def search_require_wikipedia(request):
    """ 需求百科 - 搜索 """
    # 查询所有的模板名称
    template_name_list = [{"id": sg_tem.id, "name": sg_tem.name} for sg_tem in models.Wikipedia_template.objects.filter()]

    # 查询所有的需求百科
    search_name = request.GET.get("search_name")
    all_wikipedia_data = models.Require_wikipedia.objects.filter(name__icontains=search_name)
    res_data = [{"id": sg_data.id, "name": sg_data.name, "create_time": sg_data.create_time} for sg_data in all_wikipedia_data]
    return render(request, 'require_wikipedia.html', {"template_name_list": template_name_list, "res_data": res_data})


def card_template(request):
    """ 知识卡片模板 - 展示 """
    card_obj = models.Card_template.objects.filter()
    return render(request, 'card_template.html', {'card_obj': card_obj})

class Add_card_template(View):
    """ 知识卡片模板 - 添加 """
    def get(self, request):
        card_template_obj = models.Card_template.objects.filter()
        return render(request, 'add_card_template.html', {"card_template_obj": card_template_obj})

    def post(self, request):
        name = request.POST.get("name")
        content = request.POST.get("content")
        models.Card_template.objects.create(name=name, content=content)
        return redirect('card_template')

class Edit_card_template(View):
    """ 知识卡片模板 - 编辑 """
    def get(self, request, id):
        card_template_obj = models.Card_template.objects.filter(pk=id).first()
        return render(request, 'edit_card_template.html', {"card_template_obj": card_template_obj})

    def post(self, request, id):
        name = request.POST.get("name")
        content = request.POST.get("content")
        models.Card_template.objects.filter(pk=id).update(name=name, content=content)
        return redirect('knowledge_card')

def delete_card_template(request, id):
    """ 知识卡片模板 - 删除 """
    models.Card_template.objects.filter(pk=id).delete()
    return redirect('card_template')

def knowledge_card(request):
    """ 知识卡片 - 展示 """
    template_obj = models.Card_template.objects.filter()
    card_obj = models.Knowledge_card.objects.filter()
    res_data = []
    for sg_card in card_obj:
        sg_data_dict = {}
        sg_data_dict["id"] = sg_card.id
        sg_data_dict["name"] = sg_card.name
        sg_data_dict["content"] = '，'.join([sg_data for sg_data in json.loads(sg_card.content).keys()])
        sg_data_dict["create_time"] = sg_card.create_time
        res_data.append(sg_data_dict)

    return render(request, 'knowledge_card.html', {'template_obj': template_obj, 'card_obj': card_obj, 'res_data': res_data})

class Add_knowledge_card(View):
    """ 知识卡片 - 添加 """
    def get(self, request):
        choiced_card_tempalte_id = request.GET.get("template_choiced")
        choiced_card_tempalte_obj = models.Card_template.objects.filter(id=choiced_card_tempalte_id).first()
        tem_content = choiced_card_tempalte_obj.content
        tem_content_list = tem_content.split('，')
        return render(request, 'add_knowledge_card.html', {"tem_content_str": tem_content, "tem_content_list": tem_content_list})

    def post(self, request):
        name = request.POST.get("name")
        all_tem = request.POST.get("all_tem")
        con_list = all_tem.split('，')
        con_dict = {}
        for sg_con in con_list:
            con_dict[sg_con] = request.POST.get(sg_con)
        content = json.dumps(con_dict)

        models.Knowledge_card.objects.create(name=name, content=content)
        return redirect('knowledge_card')

class Edit_knowledge_card(View):
    """ 知识卡片 - 编辑 """
    def get(self, request, id):
        Knowledge_card_obj = models.Knowledge_card.objects.filter(pk=id).first()
        name = Knowledge_card_obj.name
        content = json.loads(Knowledge_card_obj.content)
        content_title = '，'.join([sg_con_ti for sg_con_ti in content.keys()])
        content_list = [{'key': key, 'value': value} for key, value in content.items()]
        return render(request, 'edit_card_template.html', {"id": id, "name": name, "content_title": content_title, "content_list": content_list})

    def post(self, request, id):
        name = request.POST.get("name")
        all_tem = request.POST.get("all_tem")
        con_list = all_tem.split('，')
        con_dict = {}
        for sg_con in con_list:
            con_dict[sg_con] = request.POST.get(sg_con)
        content = json.dumps(con_dict)

        models.Knowledge_card.objects.filter(pk=id).update(name=name, content=content)
        return redirect('Knowledge_card')

def delete_knowledge_card(request, id):
    """ 知识卡片 - 删除 """
    models.Knowledge_card.objects.filter(pk=id).delete()
    return redirect('knowledge_card')

def preview_knowledge_card(request, id):
    knowledge_card_obj = models.Knowledge_card.objects.filter(pk=id).first()
    name = knowledge_card_obj.name
    content = json.loads(knowledge_card_obj.content)

    all_card_list = [{'key': key, 'value': value} for key, value in content.items()]

    card_dict = {"left": all_card_list[:math.ceil(len(all_card_list)/2)], "right": all_card_list[math.ceil(len(all_card_list)/2):]}

    return render(request, 'knowledge_card_preview.html', {"name": name, "card_dict": card_dict})



def chart(request):
    DataUtil = {"name": "DataUtil", "value": 3322}
    Converters = {"name": "Converters", "value": 721},
    DelimitedTextConverter = {"name": "DelimitedTextConverter", "value": 4294}

    DirtySprite = {"name": "DirtySprite", "value": 8833},
    LineSprite = {"name": "LineSprite", "value": 1732},
    RectSprite = {"name": "RectSprite", "value": 3623}

    FlareVis = {"name": "FlareVis", "value": 4116}

    AggregateExpression = {"name": "AggregateExpression", "value": 1616},
    And = {"name": "And", "value": 1027},
    Arithmetic = {"name": "Arithmetic", "value": 3891},
    Average = {"name": "Average", "value": 891},
    BinaryExpression = {"name": "BinaryExpression", "value": 2893},
    Comparison = {"name": "Comparison", "value": 5103},
    CompositeExpression = {"name": "CompositeExpression", "value": 3677},
    Count = {"name": "Count", "value": 781},
    DateUtil = {"name": "DateUtil", "value": 4141},
    Distinct = {"name": "Distinct", "value": 933},
    Expression = {"name": "Expression", "value": 5130},
    ExpressionIterator = {"name": "ExpressionIterator", "value": 3617},
    Fn = {"name": "Fn", "value": 3240},
    If = {"name": "If", "value": 2732},
    IsA = {"name": "IsA", "value": 2039},
    Literal = {"name": "Literal", "value": 1214},
    Match = {"name": "Match", "value": 3748},
    Maximum = {"name": "Maximum", "value": 843},
    Minimum = {"name": "Minimum", "value": 843},
    Not = {"name": "Not", "value": 1554},
    Or = {"name": "Or", "value": 970},
    Query = {"name": "Query", "value": 13896},
    Range = {"name": "Range", "value": 1594},
    StringUtil = {"name": "StringUtil", "value": 4130},
    Sum = {"name": "Sum", "value": 791},
    Variable = {"name": "Variable", "value": 1124},
    Variance = {"name": "Variance", "value": 1876},
    Xor = {"name": "Xor", "value": 1101}
    add = {"name": "add", "value": 593},
    and1 = {"name": "and", "value": 330},
    average = {"name": "average", "value": 287},
    count = {"name": "count", "value": 277},
    distinct = {"name": "distinct", "value": 292},
    div = {"name": "div", "value": 595},
    eq = {"name": "eq", "value": 594},
    fn = {"name": "fn", "value": 460},
    gt = {"name": "gt", "value": 603},
    gte = {"name": "gte", "value": 625},
    iff = {"name": "iff", "value": 748},
    isa = {"name": "isa", "value": 461},
    lt = {"name": "lt", "value": 597},
    lte = {"name": "lte", "value": 619},
    max = {"name": "max", "value": 283},
    min = {"name": "min", "value": 283},
    mod = {"name": "mod", "value": 591},
    mul = {"name": "mul", "value": 603},
    neq = {"name": "neq", "value": 599},
    not1 = {"name": "not", "value": 386},
    or1 = {"name": "or", "value": 323},
    orderby = {"name": "orderby", "value": 307},
    range = {"name": "range", "value": 772},
    select = {"name": "select", "value": 296},
    stddev = {"name": "stddev", "value": 363},
    sub = {"name": "sub", "value": 600},
    sum = {"name": "sum", "value": 280},
    update = {"name": "update", "value": 307},
    variance = {"name": "variance", "value": 335},
    where = {"name": "where", "value": 299},
    xor = {"name": "xor", "value": 354},
    abcv = {"name": "_", "value": 264}

    IScaleMap = {"name": "IScaleMap", "value": 2105},
    LinearScale = {"name": "LinearScale", "value": 1316},
    LogScale = {"name": "LogScale", "value": 3151},
    OrdinalScale = {"name": "OrdinalScale", "value": 3770},
    QuantileScale = {"name": "QuantileScale", "value": 2435},
    QuantitativeScale = {"name": "QuantitativeScale", "value": 4839},
    RootScale = {"name": "RootScale", "value": 1756},
    Scale = {"name": "Scale", "value": 4268},
    ScaleType = {"name": "ScaleType", "value": 1821},
    TimeScale = {"name": "TimeScale", "value": 5833}

    converter = {"name": "converter", "children": [Converters, DelimitedTextConverter]}
    methods = {"name": "methods",
               "children": [add, and1, average, count, distinct, div, eq, fn, gt, gte, iff, isa, lt, lte, max, min, mod,
                            mul, neq, not1, or1, orderby, range, select, stddev, sub, sum, update, variance, where, xor,
                            abcv, ]}

    data = {"name": "data", "children": [converter, DataUtil]}
    display = {"name": "display", "children": [DirtySprite, LineSprite, RectSprite]}
    flex = {"name": "flex", "children": [FlareVis]}
    query = {"name": "query", "children": [AggregateExpression, And, Arithmetic, Average, BinaryExpression, Comparison,
                                           CompositeExpression, Count, DateUtil, Distinct, Expression,
                                           ExpressionIterator, Fn, If, IsA, Literal, Match, Maximum, methods, Minimum,
                                           Not, Or, Query, Range, StringUtil, Sum, Variable, Variance, Xor, ]},

    scale = {"name": "scale",
             "children": [IScaleMap, LinearScale, LogScale, OrdinalScale, QuantileScale, QuantitativeScale, RootScale,
                          Scale, ScaleType, TimeScale, ]}

    all_data = {"name": "flare", "children": [data, display, flex, query, scale]}

    print(all_data["children"][3])

    data = {
        "name": "flare",
        "children": [
            {
                "name": "data",
                "children": [
                    {
                        "name": "converters",
                        "children": [
                            {"name": "Converters", "value": 721},
                            {"name": "DelimitedTextConverter", "value": 4294}
                        ]
                    },
                    {
                        "name": "DataUtil",
                        "value": 3322
                    }
                ]
            },
            {
                "name": "display",
                "children": [
                    {"name": "DirtySprite", "value": 8833},
                    {"name": "LineSprite", "value": 1732},
                    {"name": "RectSprite", "value": 3623}
                ]
            },
            {
                "name": "flex",
                "children": [
                    {"name": "FlareVis", "value": 4116}
                ]
            },
            {
                "name": "query",
                "children": [
                    {"name": "AggregateExpression", "value": 1616},
                    {"name": "And", "value": 1027},
                    {"name": "Arithmetic", "value": 3891},
                    {"name": "Average", "value": 891},
                    {"name": "BinaryExpression", "value": 2893},
                    {"name": "Comparison", "value": 5103},
                    {"name": "CompositeExpression", "value": 3677},
                    {"name": "Count", "value": 781},
                    {"name": "DateUtil", "value": 4141},
                    {"name": "Distinct", "value": 933},
                    {"name": "Expression", "value": 5130},
                    {"name": "ExpressionIterator", "value": 3617},
                    {"name": "Fn", "value": 3240},
                    {"name": "If", "value": 2732},
                    {"name": "IsA", "value": 2039},
                    {"name": "Literal", "value": 1214},
                    {"name": "Match", "value": 3748},
                    {"name": "Maximum", "value": 843},
                    {
                        "name": "methods",
                        "children": [
                            {"name": "add", "value": 593},
                            {"name": "and", "value": 330},
                            {"name": "average", "value": 287},
                            {"name": "count", "value": 277},
                            {"name": "distinct", "value": 292},
                            {"name": "div", "value": 595},
                            {"name": "eq", "value": 594},
                            {"name": "fn", "value": 460},
                            {"name": "gt", "value": 603},
                            {"name": "gte", "value": 625},
                            {"name": "iff", "value": 748},
                            {"name": "isa", "value": 461},
                            {"name": "lt", "value": 597},
                            {"name": "lte", "value": 619},
                            {"name": "max", "value": 283},
                            {"name": "min", "value": 283},
                            {"name": "mod", "value": 591},
                            {"name": "mul", "value": 603},
                            {"name": "neq", "value": 599},
                            {"name": "not", "value": 386},
                            {"name": "or", "value": 323},
                            {"name": "orderby", "value": 307},
                            {"name": "range", "value": 772},
                            {"name": "select", "value": 296},
                            {"name": "stddev", "value": 363},
                            {"name": "sub", "value": 600},
                            {"name": "sum", "value": 280},
                            {"name": "update", "value": 307},
                            {"name": "variance", "value": 335},
                            {"name": "where", "value": 299},
                            {"name": "xor", "value": 354},
                            {"name": "_", "value": 264}
                        ]
                    },
                    {"name": "Minimum", "value": 843},
                    {"name": "Not", "value": 1554},
                    {"name": "Or", "value": 970},
                    {"name": "Query", "value": 13896},
                    {"name": "Range", "value": 1594},
                    {"name": "StringUtil", "value": 4130},
                    {"name": "Sum", "value": 791},
                    {"name": "Variable", "value": 1124},
                    {"name": "Variance", "value": 1876},
                    {"name": "Xor", "value": 1101}
                ]
            },
            {
                "name": "scale",
                "children": [
                    {"name": "IScaleMap", "value": 2105},
                    {"name": "LinearScale", "value": 1316},
                    {"name": "LogScale", "value": 3151},
                    {"name": "OrdinalScale", "value": 3770},
                    {"name": "QuantileScale", "value": 2435},
                    {"name": "QuantitativeScale", "value": 4839},
                    {"name": "RootScale", "value": 1756},
                    {"name": "Scale", "value": 4268},
                    {"name": "ScaleType", "value": 1821},
                    {"name": "TimeScale", "value": 5833}
                ]
            }
        ]
    }
    if request.method == 'POST':
        return JsonResponse(all_data)


def noumenon(request):
    if request.method == 'GET':
        return render(request, 'table.html')


def noumenon_load(request):
    data = requests.post('http://192.168.43.189:8989/ontology/getOntology', )

    res_data = json.loads(data.text)
    res = {'code': 0, 'data': res_data}
    return JsonResponse(res)


def noumenon_create(request):
    if request.method == "GET":
        return render(request, 'noumenon_add.html')
    else:
        res = {'status': 1}
        return JsonResponse(res)


def noumenon_add(request):
    noumenon_name = request.GET.get("noumenon_name")
    noumenon_attribute = request.GET.get("noumenon_attribute")
    data = requests.post('http://192.168.43.189:8989/ontology/insertOntology',
                         data={"name": noumenon_name, "attributes": noumenon_attribute})

    if data:

        res = {'status': 1}
    else:
        res = {"status": 0}
    return JsonResponse(res)


def noumenon_delete(request):
    id = request.GET.get("id")

    data = requests.post('http://192.168.43.189:8989/ontology/deleteOntology',
                         data={"id": id})
    if data:
        res = {"status": 1}
    else:
        res = {"status": 0}

    return JsonResponse(res)


def noumenon_edit(request):
    if request.method == "GET":
        id = request.GET.get("id")
        name = request.GET.get("name")
        attributes = request.GET.get("attributes")
        res = {"id": id, "noumenon_name": name, "noumenon_attribute": attributes}
        return render(request, 'noumenon_edit.html', context={"noumenon": res})
    else:
        return HttpResponse('123456')


def noumenon_edit_submit(request):
    id = request.GET.get("id")
    noumenon_name = request.GET.get("noumenon_name")
    noumenon_attribute = request.GET.get("noumenon_attribute")
    print(id, noumenon_name, noumenon_attribute)

    data = requests.post('http://192.168.43.189:8989/ontology/updateOntology',
                         data={"id": id, "name": noumenon_name, "attributes": noumenon_attribute})

    if data:
        res = {"status": 1}
    else:
        res = {"status": 0}
    return JsonResponse(res)

def association_analysis(request):
    if request.method == "GET":
        res = ["项目", "学校", "外协公司"]
        return render(request, 'datashow.html', context={"noumenons": res})
    elif request.method == "POST":
        noumenon = request.POST.get("noumenon")
        entity = request.POST.get("entity")

        datas = [{
            "id": 71,
            "uuid": "XDETGG1",
            "label": "Person",
            "properties": {
                "born": "1956",
                "name": "Tom Hanks"
            }
        }, {
            "id": 72,
            "uuid": "XDETGG2",
            "label": "Person",
            "properties": {
                "born": "1956",
                "name": "Tom Hanks"
            }
        }, {
            "id": 73,
            "uuid": "XDETGG3",
            "label": "Movie",
            "properties": {
                "title": "Joe Versus the Volcano",
                "tagline": "A story of love, lava and burning desire.",
                "released": "1990"
            }
        }, {
            "id": 74,
            "uuid": "XDETGG4",
            "label": "MUSIC",
            "properties": {
                "born": "1956",
                "name": "Tom Hanks"
            }
        }, {
            "id": 75,
            "uuid": "XDETGG5",
            "label": "Person",
            "properties": {
                "born": "1956",
                "name": "Tom Hanks"
            }
        }, {
            "id": 76,
            "uuid": "XDETGG6",
            "label": "Movie",
            "properties": {
                "title": "Joe Versus the Volcano",
                "tagline": "A story of love, lava and burning desire.",
                "released": "1990"
            }
        }, {
            "id": 77,
            "uuid": "XDETGG7",
            "label": "Person",
            "properties": {
                "born": "1956",
                "name": "Tom Hanks"
            }
        }, {
            "id": 78,
            "uuid": "XDETGG8",
            "label": "Movie",
            "properties": {
                "title": "Joe Versus the Volcano",
                "tagline": "A story of love, lava and burning desire.",
                "released": "1990"
            }
        }, {
            "id": 79,
            "uuid": "XDETGG9",
            "label": "Person",
            "properties": {
                "name": "John Patrick Stanley",
                "born": 1950
            }
        }]

        edgeall = [{
            "source": '71',
            "target": '78',
            "type": "ACTED_IN",
            "id": 98
        }, {
            "source": '79',
            "target": '78',
            "type": "DIRECTED",
            "id": 101
        }, {
            "source": '79',
            "target": '77',
            "type": "DIRECTED",
            "id": 102
        }, {
            "source": '77',
            "target": '76',
            "type": "DIRECTED",
            "id": 103
        }, {
            "source": '76',
            "target": '75',
            "type": "DIRECTED",
            "id": 104
        }, {
            "source": '75',
            "target": '74',
            "type": "DIRECTED",
            "id": 105
        }, {
            "source": '74',
            "target": '73',
            "type": "DIRECTED",
            "id": 106
        }, {
            "source": '73',
            "target": '72',
            "type": "DIRECTED",
            "id": 107
        }, {
            "source": '74',
            "target": '72',
            "type": "DIRECTED",
            "id": 108
        }, {
            "source": '72',
            "target": '76',
            "type": "DIRECTED",
            "id": 109
        }]

        res = {'code': 1, "msg": "success", 'data': {"nodes": datas, "edges": edgeall}}
        return JsonResponse(res)
    else:
        return render(request, 'not_find.html')
