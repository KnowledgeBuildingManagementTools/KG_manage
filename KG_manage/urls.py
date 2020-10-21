"""KG_manage URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from django.contrib import admin
from kg_code_manage import views

urlpatterns = [
    path('admin/', admin.site.urls),
    # 主页
    path('index/', views.index, name='index'),
    # 知识构建
    path('model', views.model, name="model"),
    # 知识构建 图谱预览
    path('map_preview', views.map_preview, name="map_preview"),
    # 知识构建 插入图谱
    path('insert_map', views.insert_map, name="insert_map"),
    # 业务模型构建
    path('knowledge', views.knowledge, name="knowledge"),
    # 知识百科
    path('knowledge_wikipedia', views.knowledge_wikipedia, name="knowledge_wikipedia"),

    # 百科模板 - 展示
    path('wikipedia_template', views.Wikipedia_template.as_view(), name="wikipedia_template"),
    # 百科模板 - 搜索
    path('search_wikipedia', views.search_wikipedia, name="search_wikipedia"),
    # 百科模板 - 编辑
    path('edit_wikipedia_template/<int:id>/', views.Edit_wikipedia.as_view(), name="edit_wikipedia_template"),
    # 百科模板 - 添加
    path('add_wikipedia_template', views.Add_wikipedia.as_view(), name="add_wikipedia_template"),
    # 百科模板 - 删除
    path('delete_wikipedia/<int:n>/', views.delete_wikipedia, name="delete_wikipedia"),
    # 百科模板 - 预览
    path('preview_wikipedia/<int:n>/', views.preview_wikipedia, name="preview_wikipedia"),

    # 需求百科 - 展示
    path('require_wikipedia', views.Require_wikipedia.as_view(), name="require_wikipedia"),
    # 需求百科 - 添加
    path('add_require_wikipedia', views.add_require_wikipedia, name="add_require_wikipedia"),
    # 需求百科 - 预览
    path('preview_require_wikipedia/<int:id>/', views.preview_require_wikipedia, name="preview_require_wikipedia"),
    # 需求百科 - 编辑
    path('edit_require_wikipedia/<int:id>/', views.edit_require_wikipedia, name="edit_require_wikipedia"),
    # 需求百科 - 删除
    path('delete_require_wikipedia/<int:id>/', views.delete_require_wikipedia, name="delete_require_wikipedia"),
    # 需求百科 - 搜索
    path('search_require_wikipedia', views.search_require_wikipedia, name="search_require_wikipedia"),

    # 知识模板卡片
    path('card_template', views.card_template, name="card_template"),
    # 知识模板卡片 - 添加
    path('add_card_template', views.Add_card_template.as_view(), name="add_card_template"),
    # 知识模板卡片 - 编辑
    path('edit_card_template/<int:id>/', views.Edit_card_template.as_view(), name="edit_card_template"),
    # 知识模板卡片 - 删除
    path('delete_card_template/<int:id>/', views.delete_card_template, name="delete_card_template"),

    # 知识卡片
    path('knowledge_card', views.knowledge_card, name="knowledge_card"),
    # 知识卡片 - 添加
    path('add_knowledge_card', views.Add_knowledge_card.as_view(), name="add_knowledge_card"),
    # 知识卡片 - 编辑
    path('edit_knowledge_card/<int:id>/', views.Edit_knowledge_card.as_view(), name="edit_knowledge_card"),
    # 知识卡片 - 删除
    path('delete_knowledge_card/<int:id>/', views.delete_knowledge_card, name="delete_knowledge_card"),
    # 知识卡片 - 预览
    path('preview_knowledge_card/<int:id>/', views.preview_knowledge_card, name="preview_knowledge_card"),

    # 知识图谱服务接口

    path('service_interface', views.service_interface, name="service_interface"),

    path('chart',views.chart ,name="chart"),
    path('noumenon',views.noumenon ,name="noumenon"),
    path('noumenon_load',views.noumenon_load ,name="noumenon_load"),
    path('noumenon_create',views.noumenon_create ,name="noumenon_create"),
    path('noumenon_add',views.noumenon_add ,name="noumenon_add"),
    path('noumenon_delete',views.noumenon_delete ,name="noumenon_delete"),
    path('noumenon_edit',views.noumenon_edit ,name="noumenon_edit"),
    path('noumenon_edit_submit',views.noumenon_edit_submit ,name="noumenon_edit_submit"),
    path('association_analysis',views.association_analysis ,name="association_analysis"),
    path('map_analysis',views.map_analysis ,name="map_analysis"),
    path('analysis_aide',views.analysis_aide ,name="analysis_aide"),
    path('histogram',views.histogram ,name="histogram"),
    path('timeline',views.timeline ,name="timeline"),
    path('history_load',views.history_load ,name="history_load"),
    path('history_delete',views.history_delete ,name="history_delete"),
]
