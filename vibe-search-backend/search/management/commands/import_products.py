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
                    # Map category
                    sub_cat = row.get('sub_category', '')
                    cat = row.get('category', '')
                    title = row.get('title', '')
                    
                    mapped_category = category_map.get(sub_cat)
                    if not mapped_category:
                        # Try case-insensitive lookup
                        for key, val in category_map.items():
                            if key.lower() == sub_cat.lower():
                                mapped_category = val
                                break
                    
                    if not mapped_category:
                        # Keyword based mapping (Title & Sub-cat)
                        text_to_check = (sub_cat + ' ' + title).lower()
                        
                        if 'jeans' in text_to_check or 'pants' in text_to_check or 'trousers' in text_to_check or 'shorts' in text_to_check or 'skirt' in text_to_check or 'joggers' in text_to_check or 'sweatpants' in text_to_check:
                            mapped_category = 'bottoms'
                        elif 'hoodie' in text_to_check or 't-shirt' in text_to_check or 'sweater' in text_to_check or 'shirt' in text_to_check or 'top' in text_to_check or 'jacket' in text_to_check or 'coat' in text_to_check:
                            mapped_category = 'tops' # Jacket/Coat could be outerwear, but tops is safer fallback than accessories
                        elif 'shoe' in text_to_check or 'sneaker' in text_to_check or 'boot' in text_to_check or 'sandal' in text_to_check or 'slide' in text_to_check:
                            mapped_category = 'footwear'
                        elif 'bag' in text_to_check or 'tote' in text_to_check or 'purse' in text_to_check or 'wallet' in text_to_check:
                            mapped_category = 'bags'
                        elif cat == 'Accessories':
                            mapped_category = 'accessories'
                        elif cat == 'Apparel' or cat == 'streetwear':
                            mapped_category = 'tops' # Default fallback for apparel/streetwear if no specific keywords found
                        elif cat == 'Shoes' or cat == 'sneakers':
                            mapped_category = 'footwear'
                        else:
                            mapped_category = 'accessories' # Fallback

                    # Check if already exists
                    existing_product = Product.objects.filter(product_id=row['id']).first()
                    if existing_product:
                        # UPDATE category if it changed
                        if existing_product.category != mapped_category:
                            self.stdout.write(f"Updating category for {existing_product.title}: {existing_product.category} -> {mapped_category}")
                            existing_product.category = mapped_category
                            existing_product.save()
                        continue

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
