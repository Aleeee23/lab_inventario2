from django import forms
from django.db import models
from empleados_Alex.models import Departamento

class DepartamentoForm(forms.ModelForm):
    class Meta:
        model = Departamento
        fields = "__all__"
        
        labels = {
            'nombre': 'Nombre del Departamento',
            'descripcion': 'Descripcion del Departamento',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={ 'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
            "nuemero_empleados": forms.NumberInput(attrs={'class':'form-control'}),
        }
