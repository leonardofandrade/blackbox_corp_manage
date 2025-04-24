from django.urls import path
from . import views

app_name = 'hr'

urlpatterns = [
    # Employee views
    path('', views.home, name='home'),
    path('perfil/', views.employee_profile, name='employee_profile'),
    path('ponto/', views.attendance, name='attendance'),
    
    # Manager views
    path('funcionarios/', views.employee_list, name='employee_list'),
    path('funcionarios/novo/', views.employee_create, name='employee_create'),
    path('funcionarios/<int:pk>/editar/', views.employee_update, name='employee_update'),
    path('funcionarios/<int:pk>/excluir/', views.employee_delete, name='employee_delete'),
    
    path('unidades/', views.unit_list, name='unit_list'),
    path('unidades/nova/', views.unit_create, name='unit_create'),
    path('unidades/<int:pk>/editar/', views.unit_update, name='unit_update'),
    path('unidades/<int:pk>/excluir/', views.unit_delete, name='unit_delete'),
    
    path('registros/', views.attendance_list, name='attendance_list'),
    path('banco-horas/', views.hours_bank, name='hours_bank'),
]
