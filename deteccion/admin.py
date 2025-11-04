from django.contrib import admin

# deteccion/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    Menu, 
    Module, 
    GroupModulePermission, 
    User, 
    Cargo, 
    Empleado
)

# --- 1. Definir la clase Admin para el modelo User personalizado ---
# Esto es crucial para que el modelo User se muestre correctamente en el Admin.
class UserAdmin(BaseUserAdmin):
    # Campos que se mostrarán en la lista de usuarios del Admin
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_staff')
    # Campos que se podrán buscar
    search_fields = ('email', 'username', 'first_name', 'last_name', 'dni')
    # Campos para filtrar la lista
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')

    
    # Define la apariencia de las secciones de edición de usuario
    fieldsets = (
        (None, {'fields': ('email', 'password')}), # Se usa email como login
        ('Personal info', {'fields': ('first_name', 'last_name', 'dni', 'phone', 'direction', 'image')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    # Los REQUIRED_FIELDS definidos en tu modelo ya no se piden aquí.
    ordering = ('email',)


# --- 2. Definir las clases Admin para tus otros modelos ---

class MenuAdmin(admin.ModelAdmin):
    list_display = ('name', 'order', 'icon')
    list_editable = ('order', 'icon')
    ordering = ('order', 'name')
    search_fields = ('name',)

class ModuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'menu', 'is_active', 'order')
    list_editable = ('is_active', 'order')
    list_filter = ('menu', 'is_active')
    search_fields = ('name', 'url')

class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ('nombre_completo', 'cargo', 'cedula_ecuatoriana', 'fecha_ingreso', 'activo')
    list_filter = ('cargo', 'activo', 'fecha_ingreso')
    search_fields = ('nombres', 'apellidos', 'cedula_ecuatoriana')


# --- 3. Registrar los modelos en el sitio de administración ---

# Desregistrar el usuario por defecto (si estaba registrado) y registrar el tuyo
# Aunque tu modelo User hereda de AbstractUser, es mejor registrarlo con tu clase personalizada.
admin.site.register(User, UserAdmin)

# Registrar tus modelos de Menu y Módulos
admin.site.register(Menu, MenuAdmin)
admin.site.register(Module, ModuleAdmin)
admin.site.register(GroupModulePermission)

# Registrar tus modelos de Empleados
admin.site.register(Cargo)
admin.site.register(Empleado, EmpleadoAdmin)
# Register your models here.
