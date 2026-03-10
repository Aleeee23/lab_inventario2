from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.contrib import messages

import os

from .models import *
from .models import ArchivoSubido, Proyecto, EmpleadoProyecto, Empleado, SolicitudVacaciones, Notificacion
from .Formularios.empleado_forms import DepartamentoForm
from .forms import EmpleadoCrearConUsuarioForm, ProyectoForm


@login_required(login_url='/')
def home(request):
    if _es_admin(request):
        contexto = {
            'mensaje': 'Bienvenido al sistema de gestion de empleados',
            "user": request.user
        }
        return render(request, 'index.html', contexto)
    else:
        return redirect('empleados_Alex:user_dashboard')


@login_required(login_url='/')
def user_dashboard(request):
    if _es_admin(request):
        return redirect('empleados_Alex:home')

    empleado = get_object_or_404(
        Empleado.objects.select_related("user"),
        user=request.user
    )

    proyectos_asignados = (
        EmpleadoProyecto.objects
        .filter(empleado=empleado)
        .select_related("proyecto")
        .order_by("proyecto__nombre")
    )

    contexto = {
        "empleado": empleado,
        "proyectos_asignados": proyectos_asignados,
        "user": request.user,
    }

    return render(request, "usuarios/usuario.html", contexto)



# CRUD DEPARTAMENTO

class CreateViewDepartamento(LoginRequiredMixin, CreateView):
    model = Departamento
    form_class = DepartamentoForm
    template_name = 'Departamento/crear_departamento.html'
    success_url = reverse_lazy('empleados_Alex:home')
    login_url = '/'



# EMPLEADOS (vista datos/empleados)

@login_required(login_url='/')
def datos_Empleados(request):
    empleados = Empleado.objects.select_related("user").all().order_by("user__username")
    form = EmpleadoCrearConUsuarioForm()

    if request.method == "POST":
        accion = request.POST.get("accion")

        if accion == "crear":
            form = EmpleadoCrearConUsuarioForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, "✅ Empleado creado correctamente.")
                return redirect("empleados_Alex:datos_empleados")
            else:
                messages.error(request, "❌ Revisa los datos del formulario (hay errores).")

        elif accion == "eliminar":
            empleado_id = request.POST.get("empleado_id")
            emp = get_object_or_404(Empleado, id=empleado_id)

            if emp.foto_perfil and hasattr(emp.foto_perfil, "path"):
                if os.path.isfile(emp.foto_perfil.path):
                    os.remove(emp.foto_perfil.path)

            user = emp.user
            emp.delete()

            if user and not user.is_staff and not user.is_superuser:
                if not Empleado.objects.filter(user=user).exists():
                    user.delete()

            messages.success(request, "🗑️ Empleado eliminado correctamente.")
            return redirect("empleados_Alex:datos_empleados")

    contexto = {
        "empleados": empleados,
        "form": form,
    }
    return render(request, "datos_empleados.html", contexto)


# ARCHIVOS

@login_required(login_url='/')
def lista_archivos(request):
    archivos = ArchivoSubido.objects.all().order_by('-fecha_subida')
    return render(request, 'archivos/lista_archivos.html', {'archivos': archivos})


@login_required(login_url='/')
@require_POST
def subir_archivo(request):
    titulo = (request.POST.get('titulo') or '').strip()
    f = request.FILES.get('archivo')

    if not titulo:
        messages.error(request, "Falta el título.")
        return redirect('empleados_Alex:lista_archivos')

    if not f:
        messages.error(request, "No seleccionaste archivo.")
        return redirect('empleados_Alex:lista_archivos')

    ext = os.path.splitext(f.name)[1].lower()
    permitidas = {'.jpg', '.jpeg', '.png', '.gif', '.zip', '.rar'}

    if ext not in permitidas:
        messages.error(request, "Extensión no permitida. Usa JPG/PNG/GIF/ZIP/RAR.")
        return redirect('empleados_Alex:lista_archivos')

    ArchivoSubido.objects.create(titulo=titulo, archivo=f)
    messages.success(request, "Archivo subido y guardado en la base de datos")
    return redirect('empleados_Alex:lista_archivos')


@login_required(login_url='/')
@require_POST
def actualizar_archivo(request, pk):
    obj = get_object_or_404(ArchivoSubido, pk=pk)

    nuevo_titulo = (request.POST.get('titulo') or '').strip()
    nuevo_archivo = request.FILES.get('archivo')

    if nuevo_titulo:
        obj.titulo = nuevo_titulo

    if nuevo_archivo:
        if obj.archivo and os.path.isfile(obj.archivo.path):
            os.remove(obj.archivo.path)

        ext = os.path.splitext(nuevo_archivo.name)[1].lower()
        permitidas = {'.jpg', '.jpeg', '.png', '.gif', '.zip', '.rar'}
        if ext not in permitidas:
            messages.error(request, "Extensión no permitida. Usa JPG/PNG/GIF/ZIP/RAR.")
            return redirect('empleados_Alex:lista_archivos')

        obj.archivo = nuevo_archivo

    obj.save()
    messages.success(request, "Archivo actualizado correctamente")
    return redirect('empleados_Alex:lista_archivos')


@login_required(login_url='/')
@require_POST
def eliminar_archivo(request, pk):
    obj = get_object_or_404(ArchivoSubido, pk=pk)

    if obj.archivo and os.path.isfile(obj.archivo.path):
        os.remove(obj.archivo.path)

    obj.delete()
    messages.success(request, "Archivo eliminado (BD + carpeta media)")
    return redirect('empleados_Alex:lista_archivos')


@login_required(login_url='/')
@require_POST
def subir_archivo_ajax(request):
    titulo = (request.POST.get('titulo') or '').strip()
    f = request.FILES.get('archivo')

    if not titulo or not f:
        return JsonResponse({'ok': False, 'error': 'Falta título o archivo.'}, status=400)

    ext = os.path.splitext(f.name)[1].lower()
    permitidas = {'.jpg', '.jpeg', '.png', '.gif'}
    if ext not in permitidas:
        return JsonResponse({'ok': False, 'error': 'Solo imágenes (JPG/PNG/GIF).'}, status=400)

    obj = ArchivoSubido.objects.create(titulo=titulo, archivo=f)

    return JsonResponse({
        'ok': True,
        'id': obj.id,
        'titulo': obj.titulo,
        'url': obj.archivo.url,
        'fecha': obj.fecha_subida.isoformat()
    })



# HELPERS ADMIN

def _es_admin(request):
    u = request.user
    return u.is_authenticated and (u.username.lower() == "alex" or u.is_staff or u.is_superuser)


def es_admin(user):
    return user.is_superuser or user.is_staff



# NOTIFICACIONES ADMIN

@login_required(login_url="/")
def admin_notificaciones(request):
    if not _es_admin(request):
        return HttpResponseForbidden("No tienes permisos para ver esta sección.")

    vacaciones_pendientes = SolicitudVacaciones.objects.filter(
        estado="PENDIENTE"
    ).select_related("empleado").order_by("-creado_en")[:5]

    empleados_recientes = Empleado.objects.select_related("user").order_by("-id")[:5]
    archivos_recientes = ArchivoSubido.objects.order_by("-fecha_subida")[:5]

    asignaciones_recientes = (
        EmpleadoProyecto.objects
        .select_related("empleado__user", "proyecto")
        .order_by("-id")[:5]
    )

    total_notificaciones = (
        vacaciones_pendientes.count()
        + empleados_recientes.count()
        + archivos_recientes.count()
        + asignaciones_recientes.count()
    )

    contexto = {
        "vacaciones_pendientes": vacaciones_pendientes,
        "empleados_recientes": empleados_recientes,
        "archivos_recientes": archivos_recientes,
        "asignaciones_recientes": asignaciones_recientes,
        "total_notificaciones": total_notificaciones,
    }

    return render(request, "admin/notificaciones.html", contexto)


# VACACIONES (ADMIN)

@login_required(login_url="/")
@user_passes_test(es_admin)
def admin_vacaciones(request):
    if request.method == "POST":
        accion = request.POST.get("accion")
        sol_id = request.POST.get("solicitud_id")

        solicitud = get_object_or_404(SolicitudVacaciones, id=sol_id)

        if accion == "aprobar":
            solicitud.estado = "APROBADA"
            solicitud.save()

            Notificacion.objects.create(
                usuario=solicitud.empleado,
                titulo="Vacaciones aprobadas",
                mensaje=f"Tu solicitud de vacaciones del {solicitud.fecha_inicio} al {solicitud.fecha_fin} fue aprobada."
            )

            messages.success(request, "✅ Solicitud aprobada.")

        elif accion == "rechazar":
            solicitud.estado = "RECHAZADA"
            solicitud.save()

            Notificacion.objects.create(
                usuario=solicitud.empleado,
                titulo="Vacaciones rechazadas",
                mensaje=f"Tu solicitud de vacaciones del {solicitud.fecha_inicio} al {solicitud.fecha_fin} fue rechazada."
            )

            messages.warning(request, "⛔ Solicitud rechazada.")

        return redirect("empleados_Alex:admin_vacaciones")

    solicitudes = SolicitudVacaciones.objects.select_related("empleado").order_by("-creado_en")

    return render(request, "admin/admin_vacaciones.html", {
        "solicitudes": solicitudes
    })



# PROYECTOS (ADMIN)

@login_required(login_url="/")
def admin_proyectos(request):
    if not _es_admin(request):
        return HttpResponseForbidden("No tienes permisos para ver esta sección.")

    proyectos = Proyecto.objects.all().order_by("-id")

    data = []
    for p in proyectos:
        total = EmpleadoProyecto.objects.filter(proyecto=p).count()
        data.append({"proyecto": p, "total": total})

    return render(request, "admin/proyectos.html", {"data": data})


@login_required(login_url="/")
def admin_asignar_empleado_proyecto(request):
    if not _es_admin(request):
        return HttpResponseForbidden("No tienes permisos para ver esta sección.")

    empleados = Empleado.objects.select_related("user").order_by("user__username")
    proyectos = Proyecto.objects.order_by("nombre")

    if request.method == "POST":
        empleado_id = request.POST.get("empleado_id")
        proyecto_id = request.POST.get("proyecto_id")

        if not empleado_id or not proyecto_id:
            messages.error(request, "Selecciona empleado y proyecto.")
        else:
            empleado = Empleado.objects.get(id=empleado_id)
            proyecto = Proyecto.objects.get(id=proyecto_id)

            obj, created = EmpleadoProyecto.objects.get_or_create(
                empleado=empleado,
                proyecto=proyecto
            )

            if created:
                Notificacion.objects.create(
                    usuario=empleado.user,
                    titulo="Nuevo proyecto asignado",
                    mensaje=f"Has sido asignado al proyecto: {proyecto.nombre}."
                )
                messages.success(request, "✅ Empleado asignado al proyecto correctamente.")
            else:
                messages.warning(request, "⚠️ Ese empleado ya estaba asignado a ese proyecto.")

    return render(request, "admin/asignar_empleado_proyecto.html", {
        "empleados": empleados,
        "proyectos": proyectos
    })


class CreateViewProyecto(CreateView):
    model = Proyecto
    form_class = ProyectoForm
    template_name = "admin/crear_proyecto.html"
    success_url = reverse_lazy("empleados_Alex:admin_proyectos")

    def dispatch(self, request, *args, **kwargs):
        if not _es_admin(request):
            return HttpResponseForbidden("No tienes permisos para ver esta sección.")
        return super().dispatch(request, *args, **kwargs)


@login_required(login_url="/")
def admin_detalle_proyecto(request, pk):
    if not _es_admin(request):
        return HttpResponseForbidden("No tienes permisos para ver esta sección.")

    proyecto = Proyecto.objects.get(pk=pk)

    asignaciones = (
        EmpleadoProyecto.objects
        .filter(proyecto=proyecto)
        .select_related("empleado__user")
        .order_by("empleado__user__username")
    )

    return render(request, "admin/detalle_proyecto.html", {
        "proyecto": proyecto,
        "asignaciones": asignaciones
    })



# EMPLEADOS (ADMIN)

@login_required(login_url="/")
def admin_empleados(request):
    if not _es_admin(request):
        return HttpResponseForbidden("No tienes permisos para ver esta sección.")

    empleados = Empleado.objects.select_related("user").order_by("user__username")
    return render(request, "admin/empleados.html", {"empleados": empleados})


class CreateViewEmpleado(LoginRequiredMixin, CreateView):
    model = Empleado
    form_class = EmpleadoCrearConUsuarioForm
    template_name = "admin/crear_empleado.html"
    success_url = reverse_lazy("empleados_Alex:admin_empleados")
    login_url = "/"

    def dispatch(self, request, *args, **kwargs):
        if not _es_admin(request):
            return HttpResponseForbidden("No tienes permisos para ver esta sección.")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, "✅ Empleado creado correctamente.")
        return super().form_valid(form)


class DeleteViewEmpleado(LoginRequiredMixin, DeleteView):
    model = Empleado
    template_name = "admin/eliminar_empleado.html"
    success_url = reverse_lazy("empleados_Alex:admin_empleados")
    login_url = "/"

    def dispatch(self, request, *args, **kwargs):
        if not _es_admin(request):
            return HttpResponseForbidden("No tienes permisos para ver esta sección.")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        empleado = self.get_object()
        user = empleado.user

        if empleado.foto_perfil and hasattr(empleado.foto_perfil, "path"):
            if os.path.isfile(empleado.foto_perfil.path):
                os.remove(empleado.foto_perfil.path)

        response = super().form_valid(form)

        if user and not user.is_staff and not user.is_superuser:
            if not Empleado.objects.filter(user=user).exists():
                user.delete()

        messages.success(self.request, "🗑️ Empleado eliminado correctamente.")
        return response



# USUARIOS NORMALES

@login_required(login_url='/')
def usuario_vacaciones(request):
    if request.method == "POST":
        fecha_inicio = request.POST.get("fecha_inicio")
        fecha_fin = request.POST.get("fecha_fin")
        motivo = request.POST.get("motivo")

        SolicitudVacaciones.objects.create(
            empleado=request.user,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            motivo=motivo,
            estado="PENDIENTE"
        )

        Notificacion.objects.create(
            usuario=request.user,
            titulo="Solicitud enviada",
            mensaje=f"Tu solicitud de vacaciones del {fecha_inicio} al {fecha_fin} fue enviada correctamente y está pendiente de revisión."
        )

        messages.success(request, "Solicitud enviada correctamente.")
        return redirect("empleados_Alex:usuario_vacaciones")

    solicitudes = SolicitudVacaciones.objects.filter(
        empleado=request.user
    ).order_by("-creado_en")

    return render(request, "usuarios/vacaciones_usuario.html", {
        "solicitudes": solicitudes
    })


@login_required(login_url='/')
def usuario_notificaciones(request):
    notificaciones = Notificacion.objects.filter(
        usuario=request.user
    ).order_by("-fecha_creacion")

    return render(request, "usuarios/notificaciones_usuario.html", {
        "notificaciones": notificaciones
    })