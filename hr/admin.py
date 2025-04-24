from django.contrib import admin
from .models import OperationalUnit, Employee, TimeRecord, OvertimeBank

@admin.register(OperationalUnit)
class OperationalUnitAdmin(admin.ModelAdmin):
    list_display = ('name', 'active')
    list_filter = ('active',)
    search_fields = ('name', 'address')

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('registration_number', 'get_full_name', 'operational_unit', 
                   'weekly_hours', 'is_manager', 'active')
    list_filter = ('is_manager', 'active', 'operational_unit')
    search_fields = ('registration_number', 'user__first_name', 'user__last_name')
    raw_id_fields = ('user',)

@admin.register(TimeRecord)
class TimeRecordAdmin(admin.ModelAdmin):
    list_display = ('employee', 'timestamp', 'record_type', 'operational_unit')
    list_filter = ('record_type', 'operational_unit', 'timestamp')
    search_fields = ('employee__registration_number', 'employee__user__first_name', 
                    'employee__user__last_name')
    date_hierarchy = 'timestamp'

@admin.register(OvertimeBank)
class OvertimeBankAdmin(admin.ModelAdmin):
    list_display = ('employee', 'get_balance_display', 'last_update')
    search_fields = ('employee__registration_number', 'employee__user__first_name', 
                    'employee__user__last_name')
    readonly_fields = ('last_update',)
