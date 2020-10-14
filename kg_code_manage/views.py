import json
import os

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

project_base_path = os.getcwd()

def index(request):
    return render(request, 'index.html')


def model(request):
    if request.method == "GET":
        return render(request, "model_create.html")
    else:
        # 上传文件
        type = request.POST.get('file_type')
        file_obj = request.FILES.get('choosed_file', '')
        file_path = os.path.join(project_base_path, 'upload_file', file_obj.name)
        try:
            with open(file_path, 'wb') as f:
                for chunk in file_obj.chunks():
                    f.write(chunk, )
        except Exception as e:
            pass

        # 请求文件抽取的结果数据
        # ternary_data_path = os.path.join(project_base_path, 'simulation_data', 'ternary_data.json')
        # with open(ternary_data_path, 'w', encoding='utf-8') as fin:
        #     fin.write('data')
        res = {'code': 0, }

        return JsonResponse


def extract_data(request):
    # todo 接收上传文件抽取结果
    ternary_data_path = os.path.join(project_base_path, 'simulation_data', 'ternary_data.json')
    with open(ternary_data_path, 'r', encoding='utf-8') as fout:
        ternary_data = json.loads(fout.read())
    return JsonResponse(ternary_data)
