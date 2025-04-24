from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from datetime import datetime, timedelta
from .models import Employee, OperationalUnit, TimeRecord, OvertimeBank
from .forms import (
    EmployeeProfileForm, EmployeeForm, OperationalUnitForm,
    TimeRecordForm, ClockInOutForm, OvertimeBankUpdateForm
)

@login_required
def home(request):
    """Home view - shows different dashboard based on user role"""
    try:
        employee = request.user.employee
        context = {
            'employee': employee
        }
        
        if employee.is_manager:
            # Manager dashboard
            context.update({
                'total_employees': Employee.objects.filter(active=True).count(),
                'total_units': OperationalUnit.objects.filter(active=True).count(),
                'recent_records': TimeRecord.objects.select_related('employee', 'operational_unit')
                                        .order_by('-timestamp')[:10]
            })
            return render(request, 'hr/manager_dashboard.html', context)
        else:
            # Employee dashboard
            context.update({
                'recent_records': TimeRecord.objects.filter(employee=employee)
                                        .order_by('-timestamp')[:5],
                'overtime_bank': OvertimeBank.objects.get_or_create(employee=employee)[0]
            })
            return render(request, 'hr/employee_dashboard.html', context)
    except Employee.DoesNotExist:
        messages.error(request, 'Perfil de funcionário não encontrado.')
        return redirect('logout')

@login_required
def employee_profile(request):
    """View for employees to update their profile"""
    try:
        employee = request.user.employee
        if request.method == 'POST':
            form = EmployeeProfileForm(request.POST, instance=employee)
            if form.is_valid():
                form.save()
                messages.success(request, 'Perfil atualizado com sucesso!')
                return redirect('hr:employee_profile')
        else:
            form = EmployeeProfileForm(instance=employee)
        
        return render(request, 'hr/employee_profile.html', {'form': form})
    except Employee.DoesNotExist:
        messages.error(request, 'Perfil de funcionário não encontrado.')
        return redirect('logout')

@login_required
def attendance(request):
    """View for clock in/out"""
    if request.method == 'POST':
        form = ClockInOutForm(request.POST)
        if form.is_valid():
            registration_number = form.cleaned_data['registration_number']
            action = form.cleaned_data['action']
            
            try:
                employee = Employee.objects.get(registration_number=registration_number)
                
                # Create time record
                TimeRecord.objects.create(
                    employee=employee,
                    timestamp=timezone.now(),
                    record_type=action,
                    operational_unit=employee.operational_unit
                )
                
                messages.success(request, 
                    'Registro de {} realizado com sucesso!'.format(
                        'entrada' if action == 'IN' else 'saída'
                    ))
                return redirect('hr:attendance')
                
            except Employee.DoesNotExist:
                messages.error(request, 'Matrícula não encontrada.')
    else:
        form = ClockInOutForm()
    
    return render(request, 'hr/attendance.html', {'form': form})

# Manager views
@staff_member_required
def employee_list(request):
    """List all employees"""
    employees = Employee.objects.select_related('user', 'operational_unit').all()
    return render(request, 'hr/employee_list.html', {'employees': employees})

@staff_member_required
def employee_create(request):
    """Create new employee"""
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Funcionário cadastrado com sucesso!')
            return redirect('hr:employee_list')
    else:
        form = EmployeeForm()
    
    return render(request, 'hr/employee_form.html', {'form': form, 'title': 'Novo Funcionário'})

@staff_member_required
def employee_update(request, pk):
    """Update employee"""
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, 'Funcionário atualizado com sucesso!')
            return redirect('hr:employee_list')
    else:
        form = EmployeeForm(instance=employee)
    
    return render(request, 'hr/employee_form.html', 
                 {'form': form, 'title': 'Editar Funcionário', 'employee': employee})

@staff_member_required
def employee_delete(request, pk):
    """Delete employee"""
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        employee.active = False
        employee.save()
        messages.success(request, 'Funcionário desativado com sucesso!')
        return redirect('hr:employee_list')
    
    return render(request, 'hr/employee_confirm_delete.html', {'employee': employee})

@staff_member_required
def unit_list(request):
    """List all operational units"""
    units = OperationalUnit.objects.all()
    return render(request, 'hr/unit_list.html', {'units': units})

@staff_member_required
def unit_create(request):
    """Create new operational unit"""
    if request.method == 'POST':
        form = OperationalUnitForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Unidade operacional criada com sucesso!')
            return redirect('hr:unit_list')
    else:
        form = OperationalUnitForm()
    
    return render(request, 'hr/unit_form.html', {'form': form, 'title': 'Nova Unidade'})

@staff_member_required
def unit_update(request, pk):
    """Update operational unit"""
    unit = get_object_or_404(OperationalUnit, pk=pk)
    if request.method == 'POST':
        form = OperationalUnitForm(request.POST, instance=unit)
        if form.is_valid():
            form.save()
            messages.success(request, 'Unidade operacional atualizada com sucesso!')
            return redirect('hr:unit_list')
    else:
        form = OperationalUnitForm(instance=unit)
    
    return render(request, 'hr/unit_form.html', 
                 {'form': form, 'title': 'Editar Unidade', 'unit': unit})

@staff_member_required
def unit_delete(request, pk):
    """Delete operational unit"""
    unit = get_object_or_404(OperationalUnit, pk=pk)
    if request.method == 'POST':
        unit.active = False
        unit.save()
        messages.success(request, 'Unidade operacional desativada com sucesso!')
        return redirect('hr:unit_list')
    
    return render(request, 'hr/unit_confirm_delete.html', {'unit': unit})

@staff_member_required
def attendance_list(request):
    """List time records with filters"""
    records = TimeRecord.objects.select_related('employee', 'operational_unit').all()
    
    # Filter by date range
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date and end_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
            records = records.filter(timestamp__range=(start, end))
        except ValueError:
            messages.error(request, 'Formato de data inválido.')
    
    # Filter by employee
    employee_id = request.GET.get('employee')
    if employee_id:
        records = records.filter(employee_id=employee_id)
    
    # Filter by unit
    unit_id = request.GET.get('unit')
    if unit_id:
        records = records.filter(operational_unit_id=unit_id)
    
    context = {
        'records': records.order_by('-timestamp'),
        'employees': Employee.objects.filter(active=True),
        'units': OperationalUnit.objects.filter(active=True)
    }
    return render(request, 'hr/attendance_list.html', context)

@staff_member_required
def hours_bank(request):
    """Manage overtime bank"""
    overtime_banks = OvertimeBank.objects.select_related('employee').all()
    
    if request.method == 'POST':
        employee_id = request.POST.get('employee_id')
        if employee_id:
            overtime_bank = get_object_or_404(OvertimeBank, employee_id=employee_id)
            form = OvertimeBankUpdateForm(request.POST, instance=overtime_bank)
            if form.is_valid():
                form.save()
                messages.success(request, 'Banco de horas atualizado com sucesso!')
                return redirect('hr:hours_bank')
    else:
        form = OvertimeBankUpdateForm()
    
    context = {
        'overtime_banks': overtime_banks,
        'form': form
    }
    return render(request, 'hr/hours_bank.html', context)
