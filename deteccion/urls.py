# deteccion/urls.py
from django.urls import path
from . import views
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static
app_name = 'deteccion' # Define el namespace de la app

urlpatterns = [
    # URLs principales
    path('', lambda request: redirect('deteccion:login')),
    path('login/', views.login_vista, name='login'),
    path('inicio/', views.inicio, name='inicio'), 
    path('logout/', views.logout_view, name='logout'),

    # URLs para la cámara
    path('video_feed/', views.video_feed, name='video_feed'),
    path('toggle_camera/', views.toggle_camera, name='toggle_camera'),
    path('grabaciones/', views.grabaciones, name='grabaciones'),

    path('inicio/alerts/', views.alert_list, name='alert_data'),
    path('inicio/alerts/list/', views.alert_list_page, name='alert_list'),
    path('inicio/latest-alerts/', views.latest_alerts, name='latest_alerts'),
    
    path('inicio/incunplimiento/<int:incumplimiento_id>/', views.ver_incumplimiento, name='incunplimiento'),
    # URLs para Cargo
    path('cargos/', views.CargoListView.as_view(), name='cargo_list'),
    path('cargos/new/', views.CargoCreateView.as_view(), name='cargo_create'),
    path('cargos/edit/<int:pk>/', views.CargoUpdateView.as_view(), name='cargo_update'),
    path('cargos/delete/<int:pk>/', views.CargoDeleteView.as_view(), name='cargo_delete'),

    # URLs para Empleado
    path('inicio/empleados/', views.EmpleadoListView.as_view(), name='lista_empleados'),
    path('inicio/empleados/new/', views.EmpleadoCreateView.as_view(), name='crear_empleado'),
    path('inicio/empleados/edit/<int:pk>/', views.EmpleadoUpdateView.as_view(), name='empleado_editar'),
    path('inicio/empleados/delete/<int:pk>/', views.EmpleadoDeleteView.as_view(), name='empleado_eliminar'),

    # URLs para Menu y Module (ejemplo de lista)
    path('inicio/menus/', views.MenuListView.as_view(), name='menu_list'),
    path('inicio/create/', views.MenuCreateView.as_view(), name='menu_create'),
     path('inicio/edit/<int:pk>/', views.MenuUpdateView.as_view(), name='menu_editar'),
    path('inicio/delete/<int:pk>/', views.MenuDeleteView.as_view(), name='menu_eliminar'),



    path('inicio/modules/', views.ModuleListView.as_view(), name='module_list'),
    path('inicio/modules/create/',  views.ModuleCreateView.as_view(), name='module_create'),
    path('inicio/modules/update/<int:pk>/',  views.ModuleUpdateView.as_view(), name='module_update'),
    path('inicio/modules/delete/<int:pk>/',  views.ModuleDeleteView.as_view(), name='module_delete'),




    path('inicio/usuarios/crear/', views.usercreate, name='user_create'),
    path('inicio/usuarios/lista/', views.UserListView.as_view(), name='user_list'),
    path('inicio/usuarios/update/<int:pk>/',  views.user_edit, name='update_user'),
    path('inicio/usuarios/delete/<int:pk>/',  views.user_delete, name='user_delete'),
    path('inicio/usuarios/password/<int:pk>/',  views.user_change_password, name='user_password'),

  
    path('inicio/cargopermiso/', views.GroupModulePermissionsView.as_view(), name='cargo_permiso_list'),
    path('inicio/cargopermiso/new/', views.GroupModulePermissionCreateView.as_view(), name='cargo_permiso_create'),
    path('inicio/cargopermiso/delete/<int:pk>/', views.GroupModulePermissionDeleteView.as_view(), name='cargo_permiso_delete'),
    path('inicio/cargopermiso/edit/<int:pk>/', views.GroupModulePermissionUpdateView.as_view(), name='cargo_permiso_edit'),


    # URL de Creación de Usuarios (usando tu vista basada en función)
    path('usuarios/crear/', views.usercreate, name='user_create'),
    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)