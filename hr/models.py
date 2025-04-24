from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from datetime import timedelta

class OperationalUnit(models.Model):
    name = models.CharField("Nome", max_length=100)
    address = models.TextField("Endereço")
    active = models.BooleanField("Ativo", default=True)

    class Meta:
        verbose_name = "Unidade Operacional"
        verbose_name_plural = "Unidades Operacionais"
        ordering = ['name']

    def __str__(self):
        return self.name

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Usuário")
    registration_number = models.CharField("Matrícula", max_length=20, unique=True)
    operational_unit = models.ForeignKey(
        OperationalUnit,
        on_delete=models.PROTECT,
        verbose_name="Unidade Operacional"
    )
    phone = models.CharField("Telefone", max_length=20)
    address = models.TextField("Endereço")
    weekly_hours = models.DecimalField(
        "Carga Horária Semanal",
        max_digits=4,
        decimal_places=1,
        validators=[MinValueValidator(0)],
        default=44.0
    )
    is_manager = models.BooleanField("É Gestor", default=False)
    active = models.BooleanField("Ativo", default=True)
    created_at = models.DateTimeField("Criado em", auto_now_add=True)
    updated_at = models.DateTimeField("Atualizado em", auto_now=True)

    class Meta:
        verbose_name = "Funcionário"
        verbose_name_plural = "Funcionários"
        ordering = ['registration_number']

    def __str__(self):
        return f"{self.registration_number} - {self.user.get_full_name()}"

    def get_full_name(self):
        return self.user.get_full_name()

class TimeRecord(models.Model):
    RECORD_TYPES = [
        ('IN', 'Entrada'),
        ('OUT', 'Saída'),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        verbose_name="Funcionário"
    )
    timestamp = models.DateTimeField("Data/Hora")
    record_type = models.CharField(
        "Tipo de Registro",
        max_length=3,
        choices=RECORD_TYPES
    )
    operational_unit = models.ForeignKey(
        OperationalUnit,
        on_delete=models.PROTECT,
        verbose_name="Unidade Operacional"
    )
    created_at = models.DateTimeField("Criado em", auto_now_add=True)

    class Meta:
        verbose_name = "Registro de Ponto"
        verbose_name_plural = "Registros de Ponto"
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.employee} - {self.get_record_type_display()} - {self.timestamp}"

class OvertimeBank(models.Model):
    employee = models.OneToOneField(
        Employee,
        on_delete=models.CASCADE,
        verbose_name="Funcionário"
    )
    balance = models.DurationField(
        "Saldo",
        default=timedelta(),
        help_text="Saldo em horas (positivo ou negativo)"
    )
    last_update = models.DateTimeField("Última Atualização", auto_now=True)
    
    class Meta:
        verbose_name = "Banco de Horas"
        verbose_name_plural = "Bancos de Horas"
        ordering = ['employee__registration_number']

    def __str__(self):
        hours = self.balance.total_seconds() / 3600
        return f"{self.employee} - {hours:+.1f}h"

    def get_balance_display(self):
        hours = self.balance.total_seconds() / 3600
        return f"{hours:+.1f}h"
