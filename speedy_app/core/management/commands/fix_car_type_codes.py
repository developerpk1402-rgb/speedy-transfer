from django.core.management.base import BaseCommand
from speedy_app.core.models import CarType


class Command(BaseCommand):
    help = 'Fix car type codes by removing trailing spaces'

    def handle(self, *args, **options):
        self.stdout.write('🔧 Fixing car type codes...')
        
        fixed_count = 0
        
        for car_type in CarType.objects.all():
            original_code = car_type.code
            cleaned_code = original_code.strip()
            
            if original_code != cleaned_code:
                car_type.code = cleaned_code
                car_type.save()
                self.stdout.write(f'  Fixed: "{original_code}" -> "{cleaned_code}"')
                fixed_count += 1
        
        self.stdout.write(f'✅ Fixed {fixed_count} car type codes')
        
        # Verify the fix
        self.stdout.write('\n📊 Current car type codes:')
        for car_type in CarType.objects.all():
            self.stdout.write(f'  - "{car_type.code}" ({car_type.name})')
