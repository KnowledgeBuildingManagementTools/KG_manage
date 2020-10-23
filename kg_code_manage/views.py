import datetime
import os
import json
import math
import uuid
# from docx import Document

from django.views import View
from django.http import JsonResponse, HttpResponse

from KG_manage import settings
from kg_code_manage import models, myforms
from kg_code_manage.models import History
from django.shortcuts import render, redirect
import requests

from kg_code_manage.utils import excel_to_dict

project_base_path = os.getcwd()


def index(request):
    return render(request, 'index.html')


def model(request):
    if request.method == "GET":
        return render(request, "knowledge_building/model_create.html")
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
        """
        res_data = [{
            "id": "10002",
            "head_node": "异构知识的统一存储、映射、检索和接口技术",
            "head_type": "项目",
            "relationship": "技术指标",
            "tail_node": "异构知识种类不少于5种；知识的存储容量规模达到万级，不少于1GB；",
            "tail_type": "技术指标"
        }]
        """

        if file_type == "xls,xlsx":
            res_data = excel_to_dict(file_path).get("data")
        elif file_type == "txt":
            pass
            # with open(file_path, 'r', encoding='utf-8') as fout:
            #     txt_content_list = fout.read().split('\n\n')

        elif file_type == "docx,doc":
            pass
        elif file_type == "html":
            pass
        elif file_type == "sql":
            pass

        res = {'code': 0, 'data': res_data}
        print(res)
        return JsonResponse(res)


def insert_map(request):
    """ 插入图谱 """
    insert_map_data = json.loads(request.POST.get("insert_map_data"))
    for sg_map in insert_map_data:
        # 插入实体节点
        head_node = sg_map.get("head_node")
        head_type = sg_map.get("head_type")
        uuid_head_node = str(uuid.uuid5(uuid.NAMESPACE_DNS, head_node))
        create_time1 = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        res_data1 = {"label": head_type, "uuid": uuid_head_node, "name": head_node, "created_time": create_time1}
        response1 = requests.post(settings.neo4j_ip + '/kg/node/insert', data=res_data1)

        tail_node = sg_map.get("tail_node")
        tail_type = sg_map.get("tail_type")
        uuid_tail_node = str(uuid.uuid5(uuid.NAMESPACE_DNS, tail_node))
        create_time2 = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        res_data2 = {"label": tail_type, "uuid": uuid_tail_node, "name": tail_node, "created_time": create_time2}
        response2 = requests.post(settings.neo4j_ip + '/kg/node/insert', data=res_data2)

        # 插入实体之间的关系
        relation = sg_map.get("relation")
        create_time3 = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        res_data3 = {"start_node_uuid": uuid_head_node, "end_node_uuid": uuid_tail_node, "relation_type": relation, "created_time": create_time3}
        response3 = requests.post(settings.neo4j_ip + '/kg/edge/insert', data=res_data3)

    res = {'code': 0, 'data': "已插入到知识图谱"}
    return JsonResponse(res)


def knowledge(request):
    if request.method == "GET":
        return render(request, 'useless/knowledge_creat.html')


def map_preview(request):
    """ 抽取的信息知识图谱预览 """
    insert_map_data = json.loads(request.GET.get("insert_map_data"))
    datas = []
    edgeall = []
    for sg_map in insert_map_data:
        head_node = sg_map.get("head_node")
        head_type = sg_map.get("head_type")
        uuid_head_node = str(uuid.uuid5(uuid.NAMESPACE_DNS, head_node))
        create_time1 = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        datas.append({"id": uuid_head_node, "label": head_type, "uuid": uuid_head_node, "properties": {"name": head_node, "create_time": create_time1}})

        tail_node = sg_map.get("tail_node")
        tail_type = sg_map.get("tail_type")
        uuid_tail_node = str(uuid.uuid5(uuid.NAMESPACE_DNS, tail_node))
        create_time2 = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        datas.append({"id": uuid_tail_node, "label": tail_type, "uuid": uuid_tail_node, "properties": {"name": tail_node, "create_time": create_time2}})

        relation = sg_map.get("relation")
        # create_time3 = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        edgeall.append({"source": uuid_head_node, "target": uuid_tail_node, "type": relation})

    return render(request, 'knowledge_building/map_previews.html', {"datas": datas, "edgeall": edgeall})


def knowledge_wikipedia(request):
    """ 知识百科 """
    return render(request, 'useless/knowledge_wikipedia.html')


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

        return render(request, 'wikipedia_template/wikipedia_template.html', {'all_data': all_data})

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
    return render(request, 'wikipedia_template/wikipedia_template.html', {'all_data': all_data})


class Add_wikipedia(View):
    def get(self, request):
        card_list = models.Card_template.objects.filter()
        return render(request, 'wikipedia_template/add_wikipedia_template.html', {"card_list": card_list})

    def post(self, request):
        name = request.POST.get("name")
        content = request.POST.get("content")
        card_template = '，'.join(request.POST.getlist("card_template"))
        models.Wikipedia_template.objects.create(name=name, content=content, card_template=card_template)
        return redirect('wikipedia_template')


class Edit_wikipedia(View):
    def get(self, request, id):
        Wikipedia_template = models.Wikipedia_template.objects.filter(pk=id).first()
        card_id_list = [] if Wikipedia_template.card_template == '' else Wikipedia_template.card_template.split('，')

        selected_card_list = models.Card_template.objects.filter(id__in=card_id_list)
        selected_card_id = [sg_card.id for sg_card in selected_card_list]

        all_card_list = models.Card_template.objects.filter()
        return render(request, 'wikipedia_template/edit_wikipedia_template.html', {"Wikipedia_template": Wikipedia_template, "all_card_list": all_card_list, "selected_card_id": selected_card_id})

    def post(self, request, id):
        name = request.POST.get("name")
        content = request.POST.get("content")
        card_template = '，'.join(request.POST.getlist("card_template"))
        models.Wikipedia_template.objects.filter(pk=id).update(name=name, content=content, card_template=card_template)
        return redirect('wikipedia_template')


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
    card_template_list = [] if template_obj.card_template == '' else template_obj.card_template.split('，')
    card_template = models.Card_template.objects.filter(id__in=card_template_list)
    all_card_list = []

    for sg_ct in card_template:
        card_list = sg_ct.content.split("，")
        card_dict = {"left": card_list[:math.ceil(len(card_list) / 2)], "right": card_list[math.ceil(len(card_list) / 2):]}
        all_card_list.append(card_dict)

    return render(request, 'wikipedia_template/template_preview.html', {"template_name": template_name, "data_list": all_content_list, "all_card_list": all_card_list})


class Require_wikipedia(View):
    """ 需求百科 - 展示 """

    def get(self, request):
        # 查询所有的模板名称
        template_name_list = [{"id": sg_tem.id, "name": sg_tem.name} for sg_tem in models.Wikipedia_template.objects.filter()]
        # 查询所有的知识卡片名称
        card_name_list = [{"id": sg_card.id, "name": sg_card.name} for sg_card in models.Knowledge_card.objects.filter()]

        # 查询所有的需求百科
        all_wikipedia_data = models.Require_wikipedia.objects.filter()
        res_data = [{"id": sg_data.id, "name": sg_data.name, "create_time": sg_data.create_time} for sg_data in all_wikipedia_data]
        return render(request, 'require_wikipedia/require_wikipedia.html', {"template_name_list": template_name_list, "card_name_list": card_name_list, "res_data": res_data})

    def post(self, request):
        choiced_template_id = request.POST.get("template_choiced")
        choiced_card_id = request.POST.get("knowledge_card_choiced")
        template_content = models.Wikipedia_template.objects.filter(id=choiced_template_id).first().content
        card_content = models.Knowledge_card.objects.filter(id=choiced_card_id).first().content
        template_content_list = template_content.split('，')
        return render(request, 'require_wikipedia/add_require_wikipedia.html',
                      {'template_content_list': template_content_list, 'template_content': template_content, 'card_content': card_content, 'choiced_card_id': choiced_card_id})


def add_require_wikipedia(request):
    """ 需求百科 - 添加 """
    id = request.POST.get("id")
    name = request.POST.get("name")
    all_tem = request.POST.get("all_tem")
    card_id = request.POST.get("card_id")
    template_content_list = all_tem.split('，')
    template_content_dict = {}
    for sg_tem_con in template_content_list:
        template_content_dict[sg_tem_con] = request.POST.get(sg_tem_con)
    template_content_str = json.dumps(template_content_dict)

    if id:
        models.Require_wikipedia.objects.filter(id=id).update(name=name, content=template_content_str, knowledge_card=card_id)
    else:
        models.Require_wikipedia.objects.create(name=name, content=template_content_str, knowledge_card=card_id)
    return redirect('require_wikipedia')


def preview_require_wikipedia(request, id):
    """ 需求百科 - 预览 """
    require_wikipedia_obj = models.Require_wikipedia.objects.filter(pk=id).first()
    name = require_wikipedia_obj.name
    content = json.loads(require_wikipedia_obj.content)
    knowledge_card = require_wikipedia_obj.knowledge_card

    knowledge_card_content = models.Knowledge_card.objects.filter(pk=int(knowledge_card)).first()

    card_content = json.loads(knowledge_card_content.content)

    all_card_list = [{'key': key, 'value': value} for key, value in card_content.items()]

    card_dict = {"left": all_card_list[:math.ceil(len(all_card_list) / 2)], "right": all_card_list[math.ceil(len(all_card_list) / 2):]}

    res_data = [{"key": key, "value": value} for key, value in content.items()]

    return render(request, 'require_wikipedia/require_wikipedia_preview.html', {"name": name, "res_data": res_data, 'knowledge_card': knowledge_card, 'card_dict': card_dict})


def edit_require_wikipedia(request, id):
    """ 需求百科 - 编辑 """
    require_wikipedia_obj = models.Require_wikipedia.objects.filter(pk=id).first()
    content_dict = json.loads(require_wikipedia_obj.content)
    content = [{"key": key, "value": value} for key, value in content_dict.items()]
    name = require_wikipedia_obj.name
    id = require_wikipedia_obj.id
    all_tem = '，'.join([key for key, value in content_dict.items()])
    return render(request, 'require_wikipedia/edit_require_wikipedia.html', {'id': id, 'all_tem': all_tem, 'name': name, 'content': content})


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
    return render(request, 'require_wikipedia/require_wikipedia.html', {"template_name_list": template_name_list, "res_data": res_data})


def card_template(request):
    """ 知识卡片模板 - 展示 """
    card_obj = models.Card_template.objects.filter()
    return render(request, 'card_template/card_template.html', {'card_obj': card_obj})


class Add_card_template(View):
    """ 知识卡片模板 - 添加 """

    def get(self, request):
        card_template_obj = models.Card_template.objects.filter()
        return render(request, 'card_template/add_card_template.html', {"card_template_obj": card_template_obj})

    def post(self, request):
        name = request.POST.get("name")
        content = request.POST.get("content")
        models.Card_template.objects.create(name=name, content=content)
        return redirect('card_template')


class Edit_card_template(View):
    """ 知识卡片模板 - 编辑 """

    def get(self, request, id):
        card_template_obj = models.Card_template.objects.filter(pk=id).first()
        return render(request, 'card_template/edit_card_template.html', {"card_template_obj": card_template_obj})

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

    return render(request, 'knowledge_card/knowledge_card.html', {'template_obj': template_obj, 'card_obj': card_obj, 'res_data': res_data})


class Add_knowledge_card(View):
    """ 知识卡片 - 添加 """

    def get(self, request):
        choiced_card_tempalte_id = request.GET.get("template_choiced")
        choiced_card_tempalte_obj = models.Card_template.objects.filter(id=choiced_card_tempalte_id).first()
        tem_content = choiced_card_tempalte_obj.content
        tem_content_list = tem_content.split('，')
        return render(request, 'knowledge_card/add_knowledge_card.html', {"tem_content_str": tem_content, "tem_content_list": tem_content_list})

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
        return render(request, 'card_template/edit_card_template.html', {"id": id, "name": name, "content_title": content_title, "content_list": content_list})

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

    card_dict = {"left": all_card_list[:math.ceil(len(all_card_list) / 2)], "right": all_card_list[math.ceil(len(all_card_list) / 2):]}

    return render(request, 'knowledge_card/knowledge_card_preview.html', {"name": name, "card_dict": card_dict})


def service_interface(request):
    """ 知识图谱服务接口 """
    return render(request, 'service_interface/service_interface.html')


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
        return render(request, 'business_model/table.html')


def noumenon_load(request):
    data = requests.post(settings.service_ip + '/ontology/getOntology', )

    res_data = json.loads(data.text)
    count = len(res_data)
    res = {'code': 0, 'count': count, 'data': res_data}
    return JsonResponse(res)


def noumenon_create(request):
    if request.method == "GET":
        return render(request, 'business_model/noumenon_add.html')
    else:
        res = {'status': 1}
        return JsonResponse(res)


def noumenon_add(request):
    noumenon_name = request.GET.get("noumenon_name")
    noumenon_attribute = request.GET.get("noumenon_attribute")
    data = requests.post(settings.service_ip + '/ontology/insertOntology',
                         data={"name": noumenon_name, "attributes": noumenon_attribute})

    if data:

        res = {'status': 1}
    else:
        res = {"status": 0}
    return JsonResponse(res)


def noumenon_delete(request):
    id = request.GET.get("id")

    data = requests.post(settings.service_ip + '/ontology/deleteOntology',
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
        return render(request, 'business_model/noumenon_edit.html', context={"noumenon": res})
    else:
        return HttpResponse('123456')


def noumenon_edit_submit(request):
    id = request.GET.get("id")
    noumenon_name = request.GET.get("noumenon_name")
    noumenon_attribute = request.GET.get("noumenon_attribute")
    print(id, noumenon_name, noumenon_attribute)

    data = requests.post(settings.service_ip + '/ontology/updateOntology',
                         data={"id": id, "name": noumenon_name, "attributes": noumenon_attribute})

    if data:
        res = {"status": 1}
    else:
        res = {"status": 0}
    return JsonResponse(res)


def association_analysis(request):
    if request.method == "GET":

        return render(request, 'spectrum_analysis/datashow.html')
    elif request.method == "POST":
        start_point = request.POST.get("start_point")
        start_node_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, start_point))

        end_point = request.POST.get("end_point")
        end_node_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, end_point))

        maxnum = request.POST.get("max_num", "")

        headers = {'content_type': 'multipart/form-data; boundary=--------------------------879346903113862253548472'}

        data = requests.post(settings.neo4j_ip + '/kg/path/query',
                             data={"start_node_uuid": start_node_uuid, "end_node_uuid": end_node_uuid, "headers": headers, "level": maxnum})

        data = data.json()

        datas = []
        for sg_data in data.get('data').get('nodes'):
            datas.append({"id": sg_data.get("id"), "uuid": sg_data.get("uuid"), "label": sg_data.get("label"), "properties": {"name": sg_data.get("name"), "create_time": sg_data.get("created_time")}})

        edgeall = []
        for sg_data in data.get('data').get('edges'):
            edgeall.append({
                "source": str(sg_data.get("start_node_id")),
                "target": str(sg_data.get("end_node_id")),
                "type": sg_data.get("type"),
                "id": sg_data.get("id")
            })

        res_data = {'code': 1, "msg": "success", 'data': {"nodes": datas, "edges": edgeall}}

        print(res_data)

        return JsonResponse(res_data)
    else:
        return render(request, 'not_find.html')


def node_analysis(request):
    if request.method == "GET":
        return render(request, "spectrum_analysis/node_analysis.html")
    elif request.method == "POST":
        node_name = request.POST.get("node_name")
        node_name_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, node_name))

        headers = {'content_type': 'multipart/form-data; boundary=--------------------------879346903113862253548472'}

        data = requests.post(settings.neo4j_ip + '/kg/node/query',
                             data={"uuid": node_name_uuid, "headers": headers, })
        data = data.json()
        print(data)

        datas = []
        for sg_data in data.get('data').get('nodes'):
            datas.append({"id": sg_data.get("id"), "uuid": sg_data.get("uuid"), "label": sg_data.get("label"), "properties": {"name": sg_data.get("name"), "create_time": sg_data.get("created_time")}})

        edgeall = []
        for sg_data in data.get('data').get('edges'):
            edgeall.append({
                "source": str(sg_data.get("start_node_id")),
                "target": str(sg_data.get("end_node_id")),
                "type": sg_data.get("type"),
                "id": sg_data.get("id")
            })

        res_data = {'code': 1, "msg": "success", 'data': {"nodes": datas, "edges": edgeall}}

        return JsonResponse(res_data)
    else:
        return render(request, 'not_find.html')


def node_side_nodes(request):
    id = request.POST.get("id")
    uuid = request.POST.get("uuid")
    label = request.POST.get("label")

    data = requests.post(settings.neo4j_ip + '/kg/node/query',
                         data={"uuid ": uuid, "label": label})

    a = [{
        "id": 80,
        "uuid": "XDETGG10",
        "label": "PICTURE",
        "properties": {
            "born": "1956",
            "name": "Tom Hanks"
        }
    },
        {
            "id": 81,
            "uuid": "XDETGG11",
            "label": "TELEPLAY",
            "properties": {
                "born": "1956",
                "name": "Tom Hanks"
            }
        }]

    b = [{
        'source': '75',
        'target': '80',
        "type": "ACTED_IN",
        "id": 200
    }, {
        'source': '75',
        'target': '81',
        "type": "ACTED_IN",
        "id": 200
    }]

    res = {'code': 1, "msg": "success", 'data': {"nodes": a, "edges": b}}
    return JsonResponse(data)


def map_analysis(request):
    if request.method == "GET":
        return render(request, 'spectrum_analysis/mapshow.html')
    elif request.method == "POST":
        entity = request.POST.get("entity")

        geoCoordMap = {
            "海门": [121.15, 31.89],
            "鄂尔多斯": [109.781327, 39.608266],
            "招远": [120.38, 37.35],
            "舟山": [122.207216, 29.985295],
            "齐齐哈尔": [123.97, 47.33],
            "盐城": [120.13, 33.38],
            "赤峰": [118.87, 42.28],
            "青岛": [120.33, 36.07],
            "乳山": [121.52, 36.89],
            "金昌": [102.188043, 38.520089],
            "泉州": [118.58, 24.93],
            "莱西": [120.53, 36.86],
            "日照": [119.46, 35.42],
            "胶南": [119.97, 35.88],
            "南通": [121.05, 32.08],
            "拉萨": [91.11, 29.97],
            "云浮": [112.02, 22.93],
            "梅州": [116.1, 24.55],
            "文登": [122.05, 37.2],
            "上海": [121.48, 31.22],
            "攀枝花": [101.718637, 26.582347],
            "威海": [122.1, 37.5],
            "承德": [117.93, 40.97],
            "厦门": [118.1, 24.46],
            "汕尾": [115.375279, 22.786211],
            "潮州": [116.63, 23.68],
            "丹东": [124.37, 40.13],
            "太仓": [121.1, 31.45],
            "曲靖": [103.79, 25.51],
            "烟台": [121.39, 37.52],
            "福州": [119.3, 26.08],
            "瓦房店": [121.979603, 39.627114],
            "即墨": [120.45, 36.38],
            "抚顺": [123.97, 41.97],
            "玉溪": [102.52, 24.35],
            "张家口": [114.87, 40.82],
            "阳泉": [113.57, 37.85],
            "莱州": [119.942327, 37.177017],
            "湖州": [120.1, 30.86],
            "汕头": [116.69, 23.39],
            "昆山": [120.95, 31.39],
            "宁波": [121.56, 29.86],
            "湛江": [110.359377, 21.270708],
            "揭阳": [116.35, 23.55],
            "荣成": [122.41, 37.16],
            "连云港": [119.16, 34.59],
            "葫芦岛": [120.836932, 40.711052],
            "常熟": [120.74, 31.64],
            "东莞": [113.75, 23.04],
            "河源": [114.68, 23.73],
            "淮安": [119.15, 33.5],
            "泰州": [119.9, 32.49],
            "南宁": [108.33, 22.84],
            "营口": [122.18, 40.65],
            "惠州": [114.4, 23.09],
            "江阴": [120.26, 31.91],
            "蓬莱": [120.75, 37.8],
            "韶关": [113.62, 24.84],
            "嘉峪关": [98.289152, 39.77313],
            "广州": [113.23, 23.16],
            "延安": [109.47, 36.6],
            "太原": [112.53, 37.87],
            "清远": [113.01, 23.7],
            "中山": [113.38, 22.52],
            "昆明": [102.73, 25.04],
            "寿光": [118.73, 36.86],
            "盘锦": [122.070714, 41.119997],
            "长治": [113.08, 36.18],
            "深圳": [114.07, 22.62],
            "珠海": [113.52, 22.3],
            "宿迁": [118.3, 33.96],
            "咸阳": [108.72, 34.36],
            "铜川": [109.11, 35.09],
            "平度": [119.97, 36.77],
            "佛山": [113.11, 23.05],
            "海口": [110.35, 20.02],
            "江门": [113.06, 22.61],
            "章丘": [117.53, 36.72],
            "肇庆": [112.44, 23.05],
            "大连": [121.62, 38.92],
            "临汾": [111.5, 36.08],
            "吴江": [120.63, 31.16],
            "石嘴山": [106.39, 39.04],
            "沈阳": [123.38, 41.8],
            "苏州": [120.62, 31.32],
            "茂名": [110.88, 21.68],
            "嘉兴": [120.76, 30.77],
            "长春": [125.35, 43.88],
            "胶州": [120.03336, 36.264622],
            "银川": [106.27, 38.47],
            "张家港": [120.555821, 31.875428],
            "三门峡": [111.19, 34.76],
            "锦州": [121.15, 41.13],
            "南昌": [115.89, 28.68],
            "柳州": [109.4, 24.33],
            "三亚": [109.511909, 18.252847],
            "自贡": [104.778442, 29.33903],
            "吉林": [126.57, 43.87],
            "阳江": [111.95, 21.85],
            "泸州": [105.39, 28.91],
            "西宁": [101.74, 36.56],
            "宜宾": [104.56, 29.77],
            "呼和浩特": [111.65, 40.82],
            "成都": [104.06, 30.67],
            "大同": [113.3, 40.12],
            "镇江": [119.44, 32.2],
            "桂林": [110.28, 25.29],
            "张家界": [110.479191, 29.117096],
            "宜兴": [119.82, 31.36],
            "北海": [109.12, 21.49],
            "西安": [108.95, 34.27],
            "金坛": [119.56, 31.74],
            "东营": [118.49, 37.46],
            "牡丹江": [129.58, 44.6],
            "遵义": [106.9, 27.7],
            "绍兴": [120.58, 30.01],
            "扬州": [119.42, 32.39],
            "常州": [119.95, 31.79],
            "潍坊": [119.1, 36.62],
            "重庆": [106.54, 29.59],
            "台州": [121.420757, 28.656386],
            "南京": [118.78, 32.04],
            "滨州": [118.03, 37.36],
            "贵阳": [106.71, 26.57],
            "无锡": [120.29, 31.59],
            "本溪": [123.73, 41.3],
            "克拉玛依": [84.77, 45.59],
            "渭南": [109.5, 34.52],
            "马鞍山": [118.48, 31.56],
            "宝鸡": [107.15, 34.38],
            "焦作": [113.21, 35.24],
            "句容": [119.16, 31.95],
            "北京": [116.46, 39.92],
            "徐州": [117.2, 34.26],
            "衡水": [115.72, 37.72],
            "包头": [110, 40.58],
            "绵阳": [104.73, 31.48],
            "乌鲁木齐": [87.68, 43.77],
            "枣庄": [117.57, 34.86],
            "杭州": [120.19, 30.26],
            "淄博": [118.05, 36.78],
            "鞍山": [122.85, 41.12],
            "溧阳": [119.48, 31.43],
            "库尔勒": [86.06, 41.68],
            "安阳": [114.35, 36.1],
            "开封": [114.35, 34.79],
            "济南": [117, 36.65],
            "德阳": [104.37, 31.13],
            "温州": [120.65, 28.01],
            "九江": [115.97, 29.71],
            "邯郸": [114.47, 36.6],
            "临安": [119.72, 30.23],
            "兰州": [103.73, 36.03],
            "沧州": [116.83, 38.33],
            "临沂": [118.35, 35.05],
            "南充": [106.110698, 30.837793],
            "天津": [117.2, 39.13],
            "富阳": [119.95, 30.07],
            "泰安": [117.13, 36.18],
            "诸暨": [120.23, 29.71],
            "郑州": [113.65, 34.76],
            "哈尔滨": [126.63, 45.75],
            "聊城": [115.97, 36.45],
            "芜湖": [118.38, 31.33],
            "唐山": [118.02, 39.63],
            "平顶山": [113.29, 33.75],
            "邢台": [114.48, 37.05],
            "德州": [116.29, 37.45],
            "济宁": [116.59, 35.38],
            "荆州": [112.239741, 30.335165],
            "宜昌": [111.3, 30.7],
            "义乌": [120.06, 29.32],
            "丽水": [119.92, 28.45],
            "洛阳": [112.44, 34.7],
            "秦皇岛": [119.57, 39.95],
            "株洲": [113.16, 27.83],
            "石家庄": [114.48, 38.03],
            "莱芜": [117.67, 36.19],
            "常德": [111.69, 29.05],
            "保定": [115.48, 38.85],
            "湘潭": [112.91, 27.87],
            "金华": [119.64, 29.12],
            "岳阳": [113.09, 29.37],
            "长沙": [113, 28.21],
            "衢州": [118.88, 28.97],
            "廊坊": [116.7, 39.53],
            "菏泽": [115.480656, 35.23375],
            "合肥": [117.27, 31.86],
            "武汉": [114.31, 30.52],
            "大庆": [125.03, 46.58]
        }

        data = [
            {"name": "海门", "value": 9},
            {"name": "鄂尔多斯", "value": 12},
            {"name": "招远", "value": 12},
            {"name": "舟山", "value": 12},
            {"name": "齐齐哈尔", "value": 14},
            {"name": "盐城", "value": 15},
            {"name": "赤峰", "value": 16},
            {"name": "青岛", "value": 18},
            {"name": "乳山", "value": 18},
            {"name": "金昌", "value": 19},
            {"name": "泉州", "value": 21},
            {"name": "莱西", "value": 21},
            {"name": "日照", "value": 21},
            {"name": "胶南", "value": 22},
            {"name": "南通", "value": 23},
            {"name": "拉萨", "value": 24},
            {"name": "云浮", "value": 24},
            {"name": "梅州", "value": 25},
            {"name": "文登", "value": 25},
            {"name": "上海", "value": 25},
            {"name": "攀枝花", "value": 25},
            {"name": "威海", "value": 25},
            {"name": "承德", "value": 25},
            {"name": "厦门", "value": 26},
            {"name": "汕尾", "value": 26},
            {"name": "潮州", "value": 26},
            {"name": "丹东", "value": 27},
            {"name": "太仓", "value": 27},
            {"name": "曲靖", "value": 27},
            {"name": "烟台", "value": 28},
            {"name": "福州", "value": 29},
            {"name": "瓦房店", "value": 30},
            {"name": "即墨", "value": 30},
            {"name": "抚顺", "value": 31},
            {"name": "玉溪", "value": 31},
            {"name": "张家口", "value": 31},
            {"name": "阳泉", "value": 31},
            {"name": "莱州", "value": 32},
            {"name": "湖州", "value": 32},
            {"name": "汕头", "value": 32},
            {"name": "昆山", "value": 33},
            {"name": "宁波", "value": 33},
            {"name": "湛江", "value": 33},
            {"name": "揭阳", "value": 34},
            {"name": "荣成", "value": 34},
            {"name": "连云港", "value": 35},
            {"name": "葫芦岛", "value": 35},
            {"name": "常熟", "value": 36},
            {"name": "东莞", "value": 36},
            {"name": "河源", "value": 36},
            {"name": "淮安", "value": 36},
            {"name": "泰州", "value": 36},
            {"name": "南宁", "value": 37},
            {"name": "营口", "value": 37},
            {"name": "惠州", "value": 37},
            {"name": "江阴", "value": 37},
            {"name": "蓬莱", "value": 37},
            {"name": "韶关", "value": 38},
            {"name": "嘉峪关", "value": 38},
            {"name": "广州", "value": 38},
            {"name": "延安", "value": 38},
            {"name": "太原", "value": 39},
            {"name": "清远", "value": 39},
            {"name": "中山", "value": 39},
            {"name": "昆明", "value": 39},
            {"name": "寿光", "value": 40},
            {"name": "盘锦", "value": 40},
            {"name": "长治", "value": 41},
            {"name": "深圳", "value": 41},
            {"name": "珠海", "value": 42},
            {"name": "宿迁", "value": 43},
            {"name": "咸阳", "value": 43},
            {"name": "铜川", "value": 44},
            {"name": "平度", "value": 44},
            {"name": "佛山", "value": 44},
            {"name": "海口", "value": 44},
            {"name": "江门", "value": 45},
            {"name": "章丘", "value": 45},
            {"name": "肇庆", "value": 46},
            {"name": "大连", "value": 47},
            {"name": "临汾", "value": 47},
            {"name": "吴江", "value": 47},
            {"name": "石嘴山", "value": 49},
            {"name": "沈阳", "value": 50},
            {"name": "苏州", "value": 50},
            {"name": "茂名", "value": 50},
            {"name": "嘉兴", "value": 51},
            {"name": "长春", "value": 51},
            {"name": "胶州", "value": 52},
            {"name": "银川", "value": 52},
            {"name": "张家港", "value": 52},
            {"name": "三门峡", "value": 53},
            {"name": "锦州", "value": 54},
            {"name": "南昌", "value": 54},
            {"name": "柳州", "value": 54},
            {"name": "三亚", "value": 54},
            {"name": "自贡", "value": 56},
            {"name": "吉林", "value": 56},
            {"name": "阳江", "value": 57},
            {"name": "泸州", "value": 57},
            {"name": "西宁", "value": 57},
            {"name": "宜宾", "value": 58},
            {"name": "呼和浩特", "value": 58},
            {"name": "成都", "value": 58},
            {"name": "大同", "value": 58},
            {"name": "镇江", "value": 59},
            {"name": "桂林", "value": 59},
            {"name": "张家界", "value": 59},
            {"name": "宜兴", "value": 59},
            {"name": "北海", "value": 60},
            {"name": "西安", "value": 61},
            {"name": "金坛", "value": 62},
            {"name": "东营", "value": 62},
            {"name": "牡丹江", "value": 63},
            {"name": "遵义", "value": 63},
            {"name": "绍兴", "value": 63},
            {"name": "扬州", "value": 64},
            {"name": "常州", "value": 64},
            {"name": "潍坊", "value": 65},
            {"name": "重庆", "value": 66},
            {"name": "台州", "value": 67},
            {"name": "南京", "value": 67},
            {"name": "滨州", "value": 70},
            {"name": "贵阳", "value": 71},
            {"name": "无锡", "value": 71},
            {"name": "本溪", "value": 71},
            {"name": "克拉玛依", "value": 72},
            {"name": "渭南", "value": 72},
            {"name": "马鞍山", "value": 72},
            {"name": "宝鸡", "value": 72},
            {"name": "焦作", "value": 75},
            {"name": "句容", "value": 75},
            {"name": "北京", "value": 79},
            {"name": "徐州", "value": 79},
            {"name": "衡水", "value": 80},
            {"name": "包头", "value": 80},
            {"name": "绵阳", "value": 80},
            {"name": "乌鲁木齐", "value": 84},
            {"name": "枣庄", "value": 84},
            {"name": "杭州", "value": 84},
            {"name": "淄博", "value": 85},
            {"name": "鞍山", "value": 86},
            {"name": "溧阳", "value": 86},
            {"name": "库尔勒", "value": 86},
            {"name": "安阳", "value": 90},
            {"name": "开封", "value": 90},
            {"name": "济南", "value": 92},
            {"name": "德阳", "value": 93},
            {"name": "温州", "value": 95},
            {"name": "九江", "value": 96},
            {"name": "邯郸", "value": 98},
            {"name": "临安", "value": 99},
            {"name": "兰州", "value": 99},
            {"name": "沧州", "value": 100},
            {"name": "临沂", "value": 103},
            {"name": "南充", "value": 104},
            {"name": "天津", "value": 105},
            {"name": "富阳", "value": 106},
            {"name": "泰安", "value": 112},
            {"name": "诸暨", "value": 112},
            {"name": "郑州", "value": 113},
            {"name": "哈尔滨", "value": 114},
            {"name": "聊城", "value": 116},
            {"name": "芜湖", "value": 117},
            {"name": "唐山", "value": 119},
            {"name": "平顶山", "value": 119},
            {"name": "邢台", "value": 119},
            {"name": "德州", "value": 120},
            {"name": "济宁", "value": 120},
            {"name": "荆州", "value": 127},
            {"name": "宜昌", "value": 130},
            {"name": "义乌", "value": 132},
            {"name": "丽水", "value": 133},
            {"name": "洛阳", "value": 134},
            {"name": "秦皇岛", "value": 136},
            {"name": "株洲", "value": 143},
            {"name": "石家庄", "value": 147},
            {"name": "莱芜", "value": 148},
            {"name": "常德", "value": 152},
            {"name": "保定", "value": 153},
            {"name": "湘潭", "value": 154},
            {"name": "金华", "value": 157},
            {"name": "岳阳", "value": 169},
            {"name": "长沙", "value": 175},
            {"name": "衢州", "value": 177},
            {"name": "廊坊", "value": 193},
            {"name": "菏泽", "value": 194},
            {"name": "合肥", "value": 229},
            {"name": "武汉", "value": 273},
            {"name": "大庆", "value": 279}
        ]

        res = {'code': 1, "msg": "success", 'data': {"geoCoordMap": geoCoordMap, "data": data}}
        return JsonResponse(res)
    else:
        return render(request, 'not_find.html')


def analysis_aide(request):
    return render(request, 'spectrum_analysis/analysis_aide.html')


def histogram(request):
    if request.method == "POST":
        histogram_text = request.POST.get("histogram_text")
        print(histogram_text)
        xAxis_data = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        value_data = [10, 52, 200, 334, 390, 330, 220]
        res = {"code": 1, "msg": "success", "data": {"xAxis_data": xAxis_data, "value_data": value_data}}
        return JsonResponse(res)


def timeline(request):
    Timeline_text = request.GET.get("Timeline_text")
    print(Timeline_text)
    data = [
        {
            'label': 'John Resig提议改进Prototype的“Behaviour”库',
            'date': '2005年8月'
        },
        {
            'label': 'John Resig等人创建了jQuery',
            'date': '2006年1月'
        },
        {
            'label': 'jQuery 1.1.3版发布，这次小版本的变化包含了对jQuery选择符引擎执行速度的显著提升',
            'date': '2007年7月'
        },
        {
            'label': 'jQuery 1.2.6版发布，这版主要是将Brandon Aaron开发的流行的Dimensions插件的功能移植到了核心库',
            'date': '2008年5月'
        },
        {
            'label': 'jQuery 1.3版发布，它使用了全新的选择符引擎Sizzle',
            'date': '2009年1月'
        },
        {
            'label': '也是jQuery的四周年生日，jQuery 1.4版发布',
            'date': '2010年1月'
        },
        {
            'label': 'jQuery 1.4.2版发布，它新增了有关事件委托的两个方法',
            'date': '2010年2月'
        },
        {
            'label': 'jQuery 1.5版发布',
            'date': '2011年1月'
        },

    ]
    res = {"code": 1, "msg": "success", "data": data}
    return JsonResponse(res)


def history_load(request):
    history_text = request.GET.get("history_text")
    res_data = History.objects.filter(node__contains=history_text)
    data = []
    for res in res_data:
        res_dict = {}
        res_dict["id"] = res.id
        res_dict["node"] = res.node
        res_dict["record"] = res.record
        res_dict["time"] = res.time
        print('ddsddd', res.node)
        data.append(res_dict)
    data1 = [{"node": "项目", "record": "新增", "time": '2020-02-23'},
             {"node": "项目", "record": "新增", "time": '2020-02-23'},
             {"node": "项目", "record": "新增", "time": '2020-02-23'},
             {"node": "项目", "record": "新增", "time": '2020-02-23'},
             {"node": "项目", "record": "新增", "time": '2020-02-23'},
             {"node": "项目", "record": "新增", "time": '2020-02-23'}]
    print(data)
    count = len(data)
    res = {"code": 0, "count": count, "msg": "success", "data": data}
    return JsonResponse(res)


def history_delete(request):
    id = request.GET.get("id")
    print(id)
    data = History.objects.filter(id=id).delete()
    if data:
        res = {"status": 1}
    else:
        res = {"status": 0}

    return JsonResponse(res)
