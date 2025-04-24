from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from hr.models import OperationalUnit, Employee, TimeRecord, OvertimeBank
from datetime import timedelta

class Command(BaseCommand):
    help = 'Creates initial test data for the HR system'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating test data...')

        # Create operational units
        unit1 = OperationalUnit.objects.create(
            name='Matriz',
            address='Av. Principal, 1000 - Centro',
            active=True
        )
        
        unit2 = OperationalUnit.objects.create(
            name='Filial Sul',
            address='Rua do Comércio, 500 - Zona Sul',
            active=True
        )

        self.stdout.write('Created operational units')

        # Create employees
        # Manager 1
        manager1_user = User.objects.create_user(
            username='gerente1',
            password='gerente123',
            first_name='João',
            last_name='Silva',
            email='joao.silva@example.com'
        )
        
        manager1 = Employee.objects.create(
            user=manager1_user,
            registration_number='M001',
            operational_unit=unit1,
            phone='(11) 98765-4321',
            address='Rua das Flores, 100',
            weekly_hours=40,
            is_manager=True
        )

        # Manager 2
        manager2_user = User.objects.create_user(
            username='gerente2',
            password='gerente123',
            first_name='Maria',
            last_name='Santos',
            email='maria.santos@example.com'
        )
        
        manager2 = Employee.objects.create(
            user=manager2_user,
            registration_number='M002',
            operational_unit=unit2,
            phone='(11) 98765-4322',
            address='Rua das Palmeiras, 200',
            weekly_hours=40,
            is_manager=True
        )

        # Regular employees
        employee1_user = User.objects.create_user(
            username='func1',
            password='func123',
            first_name='Pedro',
            last_name='Oliveira',
            email='pedro.oliveira@example.com'
        )
        
        employee1 = Employee.objects.create(
            user=employee1_user,
            registration_number='F001',
            operational_unit=unit1,
            phone='(11) 98765-4323',
            address='Rua dos Pinheiros, 300',
            weekly_hours=44
        )

        employee2_user = User.objects.create_user(
            username='func2',
            password='func123',
            first_name='Ana',
            last_name='Souza',
            email='ana.souza@example.com'
        )
        
        employee2 = Employee.objects.create(
            user=employee2_user,
            registration_number='F002',
            operational_unit=unit2,
            phone='(11) 98765-4324',
            address='Rua das Acácias, 400',
            weekly_hours=44
        )

        self.stdout.write('Created employees')

        # Create time records
        now = timezone.now()
        
        # Time records for employee1
        TimeRecord.objects.create(
            employee=employee1,
            timestamp=now - timedelta(days=1, hours=8),
            record_type='IN',
            operational_unit=unit1
        )
        
        TimeRecord.objects.create(
            employee=employee1,
            timestamp=now - timedelta(days=1),
            record_type='OUT',
            operational_unit=unit1
        )

        # Time records for employee2
        TimeRecord.objects.create(
            employee=employee2,
            timestamp=now - timedelta(days=1, hours=8),
            record_type='IN',
            operational_unit=unit2
        )
        
        TimeRecord.objects.create(
            employee=employee2,
            timestamp=now - timedelta(days=1),
            record_type='OUT',
            operational_unit=unit2
        )

        self.stdout.write('Created time records')

        # Create overtime bank entries
        OvertimeBank.objects.create(
            employee=employee1,
            balance=timedelta(hours=5),  # Positive balance
        )
        
        OvertimeBank.objects.create(
            employee=employee2,
            balance=timedelta(hours=-3),  # Negative balance
        )
        
        OvertimeBank.objects.create(
            employee=manager1,
            balance=timedelta(hours=2),
        )
        
        OvertimeBank.objects.create(
            employee=manager2,
            balance=timedelta(hours=0),
        )

        self.stdout.write('Created overtime bank entries')
        
        self.stdout.write(self.style.SUCCESS('Successfully created test data'))
