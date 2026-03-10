from django.urls import path
from .views import *
from . import views
from django.contrib.auth.views import LoginView, LogoutView

app_name = "empleados_Alex"

urlpatterns = [
    
    path('', LoginView.as_view(template_name='login.html'), name='login'),
    
    path('home/', home, name='home'),
    path('mi-panel/', user_dashboard, name='user_dashboard'),

    # URLS CRUD DEPARTAMENTO
    path('departamento/crear/', CreateViewDepartamento.as_view(), name='crea_departamento'),

    # vista para los datos del empleado
    path('datos/empleados/', datos_Empleados, name='datos_empleados'),
    
    # LISTA DE ARCHIVOS  de la Tarea 4 Subir archivos y guardar en Base de Datos xd
    path('archivos/', lista_archivos, name='lista_archivos'),
    
    path('archivos/', lista_archivos, name='lista_archivos'),
    
    path('archivos/subir/', subir_archivo, name='subir_archivo'),
    
    path('archivos/<int:pk>/actualizar/', actualizar_archivo, name='actualizar_archivo'),
    
    path('archivos/<int:pk>/eliminar/', eliminar_archivo, name='eliminar_archivo'),
    
    path('archivos/subir-ajax/', subir_archivo_ajax, name='subir_archivo_ajax'),

    path('panel/notificaciones/', admin_notificaciones, name='admin_notificaciones'),
    
    path('panel/vacaciones/', admin_vacaciones, name='admin_vacaciones'),
    
    path('panel/proyectos/', admin_proyectos, name='admin_proyectos'),
    
    path('panel/proyectos/asignar/', admin_asignar_empleado_proyecto, name='admin_asignar_empleado_proyecto'),
    
    path('panel/proyectos/crear/', CreateViewProyecto.as_view(), name='crear_proyecto'),
    
    path('panel/proyectos/<int:pk>/', admin_detalle_proyecto, name='admin_detalle_proyecto'),
    
    path('panel/empleados/', admin_empleados, name='admin_empleados'),
    
    path('panel/empleados/crear/', CreateViewEmpleado.as_view(), name='crear_empleado'),
    
    path('panel/empleados/<int:pk>/eliminar/', DeleteViewEmpleado.as_view(), name='eliminar_empleado'),
    
    
    ## usuairos normales
    path('mis-vacaciones/', usuario_vacaciones, name='usuario_vacaciones'),
    
    path('mis-notificaciones/', usuario_notificaciones, name='usuario_notificaciones'),
]
