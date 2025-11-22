import csv
from django.core.management.base import BaseCommand
from search.models import Product

class Command(BaseCommand):
    help = 'Update existing products with pdp_url from CSV'

    def handle(self, *args, **options):
        csv_path = 'products.csv'
        
        updated_count = 0
        not_found_count = 0
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                product_id = row['id']
                pdp_url = row.get('pdp_url', '')
                
                try:
                    product = Product.objects.get(product_id=product_id)
                    product.pdp_url = pdp_url
                    product.save(update_fields=['pdp_url'])
                    updated_count += 1
                    
                    if updated_count % 100 == 0:
                        self.stdout.write(f'Updated {updated_count} products...')
                        
                except Product.DoesNotExist:
                    not_found_count += 1
                    continue
        
        self.stdout.write(self.style.SUCCESS(f'✅ Successfully updated {updated_count} products with URLs'))
        self.stdout.write(self.style.WARNING(f'⚠️  {not_found_count} products not found in database'))
