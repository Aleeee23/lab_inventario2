from django.db import models
from django.contrib.auth.models import User

class Departamento(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    
    def __str__(self):
        return f"Registro de  {self.nombre}"
    
    
class Empleado(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    puesto = models.CharField(max_length=100)
    departamento = models.CharField(max_length=100)
    fecha_inicio = models.DateField(auto_now_add=True)
    foto_perfil = models.ImageField(upload_to='fotos_perfil/', null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.puesto}"


# Modelo de la Tarea 4 Subir archivos y guardar en Base de Datos xd
class ArchivoSubido(models.Model):
    titulo = models.CharField(max_length=150)
    archivo = models.FileField(upload_to='archivos/')
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo
    
#  AGREGADO: PROYECTOS + ASIGNACIONES


class Proyecto(models.Model):
    nombre = models.CharField(max_length=120)
    descripcion = models.TextField(blank=True, null=True)
    fecha_inicio = models.DateField(blank=True, null=True)
    fecha_fin = models.DateField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class EmpleadoProyecto(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name="asignaciones")
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name="asignaciones")
    fecha_asignacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("empleado", "proyecto")  # evita duplicados

    def __str__(self):
        return f"{self.empleado} -> {self.proyecto}"
    


class SolicitudVacaciones(models.Model):
    ESTADOS = (
        ("PENDIENTE", "Pendiente"),
        ("APROBADA", "Aprobada"),
        ("RECHAZADA", "Rechazada"),
    )

    empleado = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    motivo = models.TextField(blank=True, null=True)
    estado = models.CharField(max_length=10, choices=ESTADOS, default="PENDIENTE")
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.empleado.username} ({self.fecha_inicio} - {self.fecha_fin})"
    
    #notificaciones 
    
class Notificacion(models.Model):

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notificaciones")
    titulo = models.CharField(max_length=150)
    mensaje = models.TextField()
    leida = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.titulo}"   