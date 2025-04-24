from django import forms
from django.contrib.auth.models import User
from .models import Employee, OperationalUnit, TimeRecord, OvertimeBank

class EmployeeProfileForm(forms.ModelForm):
    """Form for employees to update their own profile (excluding registration number)"""
    first_name = forms.CharField(label='Nome', max_length=30)
    last_name = forms.CharField(label='Sobrenome', max_length=150)
    email = forms.EmailField(label='E-mail')
    
    class Meta:
        model = Employee
        fields = ['phone', 'address']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
            
    def save(self, commit=True):
        employee = super().save(commit=False)
        user = employee.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            employee.save()
        return employee

class EmployeeForm(forms.ModelForm):
    """Form for managers to create/update employees"""
    first_name = forms.CharField(label='Nome', max_length=30)
    last_name = forms.CharField(label='Sobrenome', max_length=150)
    email = forms.EmailField(label='E-mail')
    username = forms.CharField(label='Nome de usuário', max_length=150)
    password = forms.CharField(label='Senha', widget=forms.PasswordInput, required=False,
                             help_text='Deixe em branco para manter a senha atual')
    
    class Meta:
        model = Employee
        fields = ['registration_number', 'operational_unit', 'phone', 'address',
                 'weekly_hours', 'is_manager', 'active']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user_id:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
            self.fields['username'].initial = self.instance.user.username
            self.fields['username'].disabled = True
            
    def save(self, commit=True):
        employee = super().save(commit=False)
        
        if not employee.user_id:
            # Creating new user
            user = User.objects.create_user(
                username=self.cleaned_data['username'],
                password=self.cleaned_data['password'],
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                email=self.cleaned_data['email']
            )
            employee.user = user
        else:
            # Updating existing user
            user = employee.user
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.email = self.cleaned_data['email']
            if self.cleaned_data['password']:
                user.set_password(self.cleaned_data['password'])
            user.save()
            
        if commit:
            employee.save()
        return employee

class OperationalUnitForm(forms.ModelForm):
    class Meta:
        model = OperationalUnit
        fields = ['name', 'address', 'active']

class TimeRecordForm(forms.ModelForm):
    class Meta:
        model = TimeRecord
        fields = ['employee', 'timestamp', 'record_type', 'operational_unit']
        widgets = {
            'timestamp': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            )
        }

class ClockInOutForm(forms.Form):
    """Simple form for clock in/out actions"""
    registration_number = forms.CharField(
        label='Matrícula',
        max_length=20,
        widget=forms.TextInput(attrs={'autofocus': True})
    )
    action = forms.ChoiceField(
        label='Ação',
        choices=[('IN', 'Entrada'), ('OUT', 'Saída')],
        widget=forms.HiddenInput
    )

class OvertimeBankUpdateForm(forms.ModelForm):
    """Form for updating overtime bank balance"""
    adjustment_hours = forms.DecimalField(
        label='Ajuste (horas)',
        max_digits=5,
        decimal_places=2,
        required=True,
        help_text='Use valores positivos para adicionar horas e negativos para subtrair'
    )
    justification = forms.CharField(
        label='Justificativa',
        widget=forms.Textarea(attrs={'rows': 3}),
        required=True
    )

    class Meta:
        model = OvertimeBank
        fields = []  # We don't actually update any model fields directly

    def save(self, commit=True):
        hours_adjustment = self.cleaned_data['adjustment_hours']
        minutes_adjustment = int(hours_adjustment * 60)
        
        overtime_bank = self.instance
        current_balance = overtime_bank.balance.total_seconds() / 60  # Convert to minutes
        new_balance = current_balance + minutes_adjustment
        
        overtime_bank.balance = timedelta(minutes=new_balance)
        
        if commit:
            overtime_bank.save()
        return overtime_bank
