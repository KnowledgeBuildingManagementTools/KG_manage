import os

from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.

def index(request):
    return render(request, 'index.html')


def model(request):

    if request.method =="GET":
        return render(request,"model_create.html")
    else:
        domain = request.POST.get('file_type')
        # todo 前端传输过来的文件，没有文件路径。
        file_obj = request.FILES.get('choosed_file', '')
        file_path = os.getcwd()+'\\'+file_obj.name
        # todo 上传文件存储
        try:
            # 获取前端传递过来的数据进行保存
            with open(file_path, 'wb') as f:
                for chunk in file_obj.chunks():
                    f.write(chunk, )
        except Exception as e:
            print(e)

        return HttpResponse("123456")


