from django import forms
from kg_code_manage import models

class WikipediaTemplateModelForm(forms.ModelForm):
    class Meta:
        model = models.Wikipedia_template
        fields = '__all__'

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for field in self.fields.values():
                field.widget.attrs.update({'class':'form-control'})

class KnowledgeCardModelForm(forms.ModelForm):
    class Meta:
        model = models.Knowledge_card
        fields = '__all__'

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for field in self.fields.values():
                field.widget.attrs.update({'class':'form-control'})