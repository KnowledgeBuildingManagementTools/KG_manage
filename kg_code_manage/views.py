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
        sign = request.GET.get("sign")
        return render(request, "knowledge_building/model_create.html", {"sign": sign})
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
        """ 返回数据格式示例
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

def wikipedia_classification(request):
    """ 百科分类展示 """
    wikipedia_template_obj = models.Wikipedia_template.objects.filter()
    return render(request, 'wikipedia_template/wikipedia_classification.html', {'wikipedia_template_obj': wikipedia_template_obj})

def search_wikipedia_classification(request):
    """ 百科分类搜索 """
    wikipedia_classification = request.GET.get("wikipedia_classification")
    wikipedia_template_obj = models.Wikipedia_template.objects.filter(name__icontains=wikipedia_classification)
    return render(request, 'wikipedia_template/wikipedia_classification.html', {'wikipedia_template_obj': wikipedia_template_obj})

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
    id = require_wikipedia_obj.id
    name = require_wikipedia_obj.name
    card_id = require_wikipedia_obj.knowledge_card
    all_tem = '，'.join([key for key, value in content_dict.items()])
    return render(request, 'require_wikipedia/edit_require_wikipedia.html', {'id': id, 'all_tem': all_tem, 'name': name, 'content': content, "card_id": card_id})


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
    """
    业务模型构建服务接口中--推理分析
    """
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
    """本体页面服务接口"""
    if request.method == 'GET':
        return render(request, 'business_model/table.html')


def noumenon_load(request):
    """本体全部查询接口"""
    data = requests.post(settings.service_ip + '/ontology/getOntology', )

    res_data = json.loads(data.text)
    count = len(res_data)
    res = {'code': 0, 'count': count, 'data': res_data}
    return JsonResponse(res)


def noumenon_create(request):
    """请求创建本体服务窗口接口"""
    if request.method == "GET":
        return render(request, 'business_model/noumenon_add.html')
    else:
        res = {'status': 1}
        return JsonResponse(res)


def noumenon_add(request):
    """提交本体创建"""
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
    """本体删除"""
    id = request.GET.get("id")

    data = requests.post(settings.service_ip + '/ontology/deleteOntology',
                         data={"id": id})
    if data:
        res = {"status": 1}
    else:
        res = {"status": 0}

    return JsonResponse(res)


def noumenon_edit(request):
    """本体更新请求页面"""
    if request.method == "GET":
        id = request.GET.get("id")
        name = request.GET.get("name")
        attributes = request.GET.get("attributes")
        res = {"id": id, "noumenon_name": name, "noumenon_attribute": attributes}
        return render(request, 'business_model/noumenon_edit.html', context={"noumenon": res})
    else:
        return HttpResponse('123456')


def noumenon_edit_submit(request):
    """本体更新提交"""
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


def association_analysis(request):
    """
    图谱展示
    get：请求页面
    post：提交参数，供返回数据
    # TODO 需要节点和关系
    """
    if request.method == "GET":
        sign = request.GET.get("sign")
        return render(request, 'spectrum_analysis/datashow.html', {"sign":sign})
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


def node_side_nodes(request):
    """
    双击图谱node时，返回该点周边的点与该点的关系
    """
    id = request.POST.get("id")
    uuid = request.POST.get("uuid")
    label = request.POST.get("label")
    print(id, uuid, label)

    level = 1
    headers = {'content_type': 'multipart/form-data; boundary=--------------------------879346903113862253548472'}

    data = requests.post(settings.neo4j_ip + '/kg/graph/query',
                         data={"start_node_uuid": uuid, "level": level, "headers": headers})

    data = data.json()
    print(data)

    datas = []
    for sg_data in data.get('data').get('nodes'):
        datas.append({"id": sg_data.get("id"), "uuid": sg_data.get("uuid"), "label": sg_data.get("label"),
                      "properties": {"name": sg_data.get("name"), "create_time": sg_data.get("created_time")}})

    edgeall = []
    for sg_data in data.get('data').get('edges'):
        edgeall.append({
            "source": str(sg_data.get("start_node_id")),
            "target": str(sg_data.get("end_node_id")),
            "type": sg_data.get("type"),
            "id": sg_data.get("id")
        })

    res = {'code': 1, "msg": "success", 'data': {"nodes": datas, "edges": edgeall}}

    print("res================", res)
    return JsonResponse(res)


def map_analysis(request):
    """
    地图展示
    get:请求页面
    post：提交数据，返回数据
    TODO 需要事件名，和事件发展和地点
    """
    if request.method == "GET":
        return render(request, 'spectrum_analysis/mapshow.html')
    elif request.method == "POST":
        entity = request.POST.get("entity")
        entity_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, entity))
        headers = {'content_type': 'multipart/form-data; boundary=--------------------------879346903113862253548472'}

        res_data = requests.post(settings.neo4j_ip + '/kg/node/query',
                                 data={"uuid": entity_uuid, "headers": headers, })
        res_data = res_data.json()
        geoCoordMap = {}
        data = []
        for sg_data in res_data.get('data').get('nodes'):
            geoCoordMap[sg_data.get("name")] = eval(sg_data.get("area"))
            data.append(sg_data)
        res = {'code': 1, "msg": "success", 'data': {"geoCoordMap": geoCoordMap, "data": data}}
        return JsonResponse(res)
    else:
        return render(request, 'not_find.html')


def analysis_aide(request):
    """
    分析助手请求页面接口
    """

    return render(request, 'spectrum_analysis/analysis_aide.html')


def histogram(request):
    """直方图分析接口"""
    # TODO 分析直方图需要节点统计
    if request.method == "POST":
        histogram_text = request.POST.get("histogram_text")
        project = models.Project.objects.filter(project_name=histogram_text).first()
        res_datas = models.Histogram.objects.filter(project_id=str(project.id))
        xAxis_data = []
        value_data = []
        for res_data in res_datas:
            xAxis_data.append(res_data.class_name)
            value_data.append(int(res_data.require_count))

        res = {"code": 1, "msg": "success", "data": {"xAxis_data": xAxis_data, "value_data": value_data}}
        return JsonResponse(res)


def timeline(request):
    """时间线"""
    # TODO 时间线需要节点的发展历程
    timeline_text = request.GET.get("Timeline_text")
    project = models.Project.objects.filter(project_name=timeline_text).first()
    res_datas = models.Timeline.objects.filter(project_id=str(project.id)).order_by("time")
    data = []
    for res_data in res_datas:
        print(res_data)
        res_dict = {}
        res_dict["label"] = res_data.event_name
        res_dict["date"] = res_data.time
        data.append(res_dict)
    print(data)
    # mid_dict = {key: value for x in data for key, value in x.items()}
    # mid_list = sorted(mid_dict.items(), key=itemgetter(2))
    # data = [{x[0]: x[1]} for x in mid_list]

    res = {"code": 1, "msg": "success", "data": data}
    return JsonResponse(res)


def history_load(request):
    """历史分析接口"""
    # TODO 历史需要历史操作记录
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
    """历史数据删除接口"""
    id = request.GET.get("id")
    print(id)
    data = History.objects.filter(id=id).delete()
    if data:
        res = {"status": 1}
    else:
        res = {"status": 0}

    return JsonResponse(res)


def data_mining_model(request):
    # 查看数据挖掘模型表
    data_mining_obj = models.Data_mining.objects.filter()
    # 查看知识推理模型表
    knowledge_reasoning_obj = models.Knowledge_reasoning.objects.filter()
    # 查看关联分析模型表
    correlation_analysis_obj = models.Correlation_analysis.objects.filter()

    return render(request, 'data_mining_model/business_model_building.html', {"data_mining_obj": data_mining_obj, "knowledge_reasoning_obj": knowledge_reasoning_obj, "correlation_analysis_obj": correlation_analysis_obj})



class Model_import(View):
    """ 模型导入 """

    def get(self, request):
        # 模型文件导入
        # file_obj = request.FILES.get('file')
        # file_path = os.path.join(project_base_path, 'model_file', file_obj.name)
        # try:
        #     with open(file_path, 'wb') as f:
        #         for chunk in file_obj.chunks():
        #             f.write(chunk, )
        #     res_data = {"code": 1, "msg": "模型导入成功"}
        # except Exception:
        #     res_data = {"code": 0, "msg": "模型导入失败，请重试！！！"}
        # return JsonResponse(res_data)
        return render(request, 'data_mining_model/model_import.html')

    def post(self, request):
        uuid = request.POST.get("uuid", "")
        name = request.POST.get("name", "")
        label = request.POST.get("label", "")
        try:
            models.Data_mining.objects.create(name=name, label=label, uuid=uuid)
            res_data = {"code": 1, "msg": "模型导入成功"}
        except Exception:
            res_data = {"code": 0, "msg": "模型导入失败！！！"}
        return JsonResponse(res_data)


class Knowledge_reasoning_model_import(View):
    """ 知识推理模型导入 """
    def get(self, request):
        return render(request, 'knowledge_reasoning_model/model_import.html')

    def post(self, request):
        name = request.POST.get("name", "")
        start_node_uuid = request.POST.get("start_node_uuid", "")
        relation_type = request.POST.get("relation_type", "")
        try:
            models.Knowledge_reasoning.objects.create(name=name, start_node_uuid=start_node_uuid, relation_type=relation_type)
            res_data = {"code": 1, "msg": "模型导入成功"}
        except Exception:
            res_data = {"code": 0, "msg": "模型导入失败！！！"}
        return JsonResponse(res_data)


class Correlation_analysis_model_import(View):
    """ 关联分析模型导入 """
    def get(self, request):
        return render(request, 'correlation_analysis_model/model_import.html')

    def post(self, request):
        name = request.POST.get("name", "")
        start_node_uuid = request.POST.get("start_node_uuid", "")
        end_node_uuid = request.POST.get("end_node_uuid", "")
        try:
            models.Correlation_analysis.objects.create(name=name, start_node_uuid=start_node_uuid, end_node_uuid=end_node_uuid)
            res_data = {"code": 1, "msg": "模型导入成功"}
        except Exception:
            res_data = {"code": 0, "msg": "模型导入失败！！！"}
        return JsonResponse(res_data)

class Model_edit(View):
    """ 数据挖掘模型修改 """
    def get(self, request):
        model_id = request.GET.get("model_id")
        model_obj = models.Data_mining.objects.filter(pk=model_id).first()
        return render(request, 'data_mining_model/model_edit.html', {"model_obj": model_obj})
    def post(self, request):
        id = request.POST.get("id", "")
        uuid = request.POST.get("uuid", "")
        name = request.POST.get("name", "")
        label = request.POST.get("label", "")
        try:
            models.Data_mining.objects.filter(pk=id).update(name=name, label=label, uuid=uuid)
            res_data = {"code": 1, "msg": "模型配置修改成功"}
        except Exception:
            res_data = {"code": 0, "msg": "模型配置修改失败！！！"}
        return JsonResponse(res_data)


class Knowledge_reasoning_model_edit(View):
    """ 知识推理模型修改 """
    def get(self, request):
        model_id = request.GET.get("model_id")
        model_obj = models.Knowledge_reasoning.objects.filter(pk=model_id).first()
        return render(request, 'knowledge_reasoning_model/model_edit.html', {"model_obj": model_obj})
    def post(self, request):
        id = request.POST.get("id", "")
        name = request.POST.get("name", "")
        start_node_uuid = request.POST.get("start_node_uuid", "")
        relation_type = request.POST.get("relation_type", "")

        try:
            models.Knowledge_reasoning.objects.filter(pk=id).update(name=name, start_node_uuid=start_node_uuid, relation_type=relation_type)
            res_data = {"code": 1, "msg": "模型配置修改成功"}
        except Exception:
            res_data = {"code": 0, "msg": "模型配置修改失败！！！"}
        return JsonResponse(res_data)

class Correlation_analysis_model_edit(View):
    """ 关联分析模型修改 """
    def get(self, request):
        model_id = request.GET.get("model_id")
        model_obj = models.Correlation_analysis.objects.filter(pk=model_id).first()
        return render(request, 'correlation_analysis_model/model_edit.html', {"model_obj": model_obj})
    def post(self, request):
        id = request.POST.get("id", "")
        name = request.POST.get("name", "")
        start_node_uuid = request.POST.get("start_node_uuid", "")
        end_node_uuid = request.POST.get("end_node_uuid", "")
        try:
            models.Correlation_analysis.objects.filter(pk=id).update(name=name, start_node_uuid=start_node_uuid, end_node_uuid=end_node_uuid)
            res_data = {"code": 1, "msg": "模型配置修改成功"}
        except Exception:
            res_data = {"code": 0, "msg": "模型配置修改失败！！！"}
        return JsonResponse(res_data)


class Model_run(View):
    def get(self, request):
        """ 数据挖掘运行 """
        model_id = request.GET.get("model_id")
        return render(request, 'data_mining_model/model_map_show.html', {"model_id": model_id})

    def post(self, request):
        id = request.POST.get("model_id")
        data_mining_obj = models.Data_mining.objects.filter(pk=id).first()
        uuid = data_mining_obj.uuid

        data = requests.post(settings.neo4j_ip + '/kg/node/query',
                             data={"uuid ": uuid})
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

        return JsonResponse(res_data)


class Knowledge_reasoning_model_run(View):
    def get(self, request):
        """ 知识推理模型运行 """
        model_id = request.GET.get("model_id")
        return render(request, 'knowledge_reasoning_model/model_map_show.html', {"model_id": model_id})

    def post(self, request):
        id = request.POST.get("model_id")
        knowledge_reasoning_obj = models.Knowledge_reasoning.objects.filter(pk=id).first()
        start_node_uuid = knowledge_reasoning_obj.start_node_uuid
        relation_type = knowledge_reasoning_obj.relation_type

        headers = {'content_type': 'multipart/form-data; boundary=--------------------------879346903113862253548472'}
        data = requests.post(settings.neo4j_ip + '/kg/graph/query',
                             data={"start_node_uuid": start_node_uuid, "relation_type": [relation_type], "headers": headers})
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

        return JsonResponse(res_data)


class Correlation_analysis_model_run(View):
    def get(self, request):
        """ 关联分析模型运行 """
        model_id = request.GET.get("model_id")
        return render(request, 'correlation_analysis_model/model_map_show.html', {"model_id": model_id})

    def post(self, request):
        # todo 没接收到数据
        id = request.POST.get("model_id")
        correlation_analysis_obj = models.Correlation_analysis.objects.filter(pk=id).first()
        start_node_uuid = correlation_analysis_obj.start_node_uuid
        end_node_uuid = correlation_analysis_obj.end_node_uuid

        headers = {'content_type': 'multipart/form-data; boundary=--------------------------879346903113862253548472'}
        data = requests.post(settings.neo4j_ip + '/kg/path/query',
                             data={"start_node_uuid": start_node_uuid, "end_node_uuid": end_node_uuid, "headers": headers})
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

        return JsonResponse(res_data)