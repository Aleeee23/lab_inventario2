from django import forms
from .models import Empleado
from .models import Proyecto

class EmpleadoForm(forms.ModelForm):
    class Meta:
        model = Empleado
        fields = ["user", "puesto", "departamento", "foto_perfil"]


#  AGREGADO: FORM PROYECTO

class ProyectoForm(forms.ModelForm):
    class Meta:
        model = Proyecto
        fields = ["nombre", "descripcion", "fecha_inicio", "fecha_fin", "activo"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "w-full p-3 rounded-xl bg-slate-900 border border-white/10 text-white"}),
            "descripcion": forms.Textarea(attrs={"class": "w-full p-3 rounded-xl bg-slate-900 border border-white/10 text-white", "rows": 4}),
            "fecha_inicio": forms.DateInput(attrs={"type": "date", "class": "w-full p-3 rounded-xl bg-slate-900 border border-white/10 text-white"}),
            "fecha_fin": forms.DateInput(attrs={"type": "date", "class": "w-full p-3 rounded-xl bg-slate-900 border border-white/10 text-white"}),
            "activo": forms.CheckboxInput(attrs={"class": "h-5 w-5"}),
        }
        
        
from django import forms
from django.contrib.auth.models import User
from django.db import transaction
from .models import Empleado

class EmpleadoCrearConUsuarioForm(forms.ModelForm):
    # datos del usuario Django (login)
    username = forms.CharField(max_length=150, label="Usuario")
    email = forms.EmailField(required=False, label="Correo")
    password1 = forms.CharField(widget=forms.PasswordInput, label="Contraseña")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirmar contraseña")

    class Meta:
        model = Empleado
        fields = ["puesto", "departamento", "foto_perfil"]

        widgets = {
            "puesto": forms.TextInput(attrs={"class": "w-full p-3 rounded-xl bg-slate-900 border border-white/10 text-white"}),
            "departamento": forms.TextInput(attrs={"class": "w-full p-3 rounded-xl bg-slate-900 border border-white/10 text-white"}),
        }

    def clean_username(self):
        username = (self.cleaned_data.get("username") or "").strip()
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Ese usuario ya existe.")
        return username

    def clean(self):
        data = super().clean()
        p1 = data.get("password1")
        p2 = data.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Las contraseñas no coinciden.")
        return data

    @transaction.atomic
    def save(self, commit=True):
        # crea User
        user = User.objects.create_user(
            username=self.cleaned_data["username"],
            email=self.cleaned_data.get("email") or "",
            password=self.cleaned_data["password1"],
        )

        # crea Empleado
        empleado = super().save(commit=False)
        empleado.user = user

        if commit:
            empleado.save()

        return empleado
    
    from django import forms
from django.contrib.auth.models import User
from django.db import transaction
from .models import Empleado

class EmpleadoCrearConUsuarioForm(forms.ModelForm):
    username = forms.CharField(max_length=150, label="Usuario")
    email = forms.EmailField(required=False, label="Correo")
    password1 = forms.CharField(widget=forms.PasswordInput, label="Contraseña")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirmar contraseña")

    class Meta:
        model = Empleado
        fields = ["puesto", "departamento", "foto_perfil"]

        widgets = {
            "puesto": forms.TextInput(attrs={"class": "w-full p-3 rounded-xl bg-slate-900 border border-white/10 text-white"}),
            "departamento": forms.TextInput(attrs={"class": "w-full p-3 rounded-xl bg-slate-900 border border-white/10 text-white"}),
        }

    def clean_username(self):
        username = (self.cleaned_data.get("username") or "").strip()
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Ese usuario ya existe.")
        return username

    def clean(self):
        data = super().clean()
        if data.get("password1") != data.get("password2"):
            self.add_error("password2", "Las contraseñas no coinciden.")
        return data

    @transaction.atomic
    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data["username"],
            email=self.cleaned_data.get("email") or "",
            password=self.cleaned_data["password1"],
        )

        empleado = super().save(commit=False)
        empleado.user = user

        if commit:
            empleado.save()

        return empleado