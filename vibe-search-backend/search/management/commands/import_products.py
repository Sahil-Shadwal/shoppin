import csv
import os
from django.core.management.base import BaseCommand
from search.models import Product
from search.ml_service import ml_service
from tqdm import tqdm

class Command(BaseCommand):
    help = 'Import products from products.csv and generate embeddings'

    def handle(self, *args, **options):
        csv_path = 'products.csv'
        
        if not os.path.exists(csv_path):
            self.stdout.write(self.style.ERROR(f'File {csv_path} not found'))
            return

        # Category mapping
        category_map = {
            'T-Shirt': 'tops',
            'Hoodie': 'tops',
            'Sweatshirt': 'tops',
            'Jacket': 'outerwear',
            'Pants': 'bottoms',
            'Shorts': 'bottoms',
            'Jeans': 'bottoms',
            'Sneakers': 'footwear',
            'Shoes': 'footwear',
            'Sandals': 'footwear',
            'Slides': 'footwear',
            'Bag': 'accessories',
            'Hat': 'accessories',
            'Cap': 'accessories',
            'Socks': 'accessories',
            'Watch': 'accessories',
            'Tumbler': 'accessories',
        }

        products_to_create = []
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            self.stdout.write(f"Found {len(rows)} products. Processing ALL of them...")
            
            # Remove all limits/filters to import EVERYTHING
            # rows = rows[:50] 
            
            for row in tqdm(rows):
                try:
                    # Skip if already exists
                    if Product.objects.filter(product_id=row['id']).exists():
                        continue

                    # Map category
                    sub_cat = row.get('sub_category', '')
                    cat = row.get('category', '')
                    
                    mapped_category = category_map.get(sub_cat)
                    if not mapped_category:
                        if cat == 'Accessories':
                            mapped_category = 'accessories'
                        elif cat == 'Apparel':
                            mapped_category = 'tops' # Default fallback
                        elif cat == 'Shoes':
                            mapped_category = 'footwear'
                        else:
                            mapped_category = 'accessories' # Fallback

                    # Price handling
                    try:
                        price = float(row['lowest_price'])
                    except:
                        price = 0.0

                    # Generate embeddings
                    image_url = row['featured_image']
                    visual_embedding = None
                    if image_url:
                        visual_embedding = ml_service.generate_image_embedding(image_url)
                    
                    title = row['title']
                    text_embedding = None
                    if title:
                        text_embedding = ml_service.generate_text_embedding(title)

                    product = Product(
                        product_id=row['id'],
                        title=title,
                        brand_name=row['brand_name'],
                        category=mapped_category,
                        image_url=image_url,
                        price=price,
                        pdp_url=row.get('pdp_url', ''),  # Add product page URL
                        colors=row.get('colorways', '').split(',') if row.get('colorways') else [],
                        visual_embedding=visual_embedding,
                        text_embedding=text_embedding
                    )
                    products_to_create.append(product)
                    
                    # Batch create every 10 to save memory/time
                    if len(products_to_create) >= 10:
                        Product.objects.bulk_create(products_to_create)
                        products_to_create = []
                        
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"Error processing row {row.get('id')}: {e}"))

            # Create remaining
            if products_to_create:
                Product.objects.bulk_create(products_to_create)

        self.stdout.write(self.style.SUCCESS('Successfully imported products'))
