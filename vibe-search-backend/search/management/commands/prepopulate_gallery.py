import requests
import time
from django.core.management.base import BaseCommand
from search.models import ScrapedImage
from search.ml_service import ml_service


SCRAPING_TERMS = [
    # Pinterest Boards
    'Minimal Streetwear',
    'Men\'s Streetwear Outfit Ideas',
    'Streetwear Outfit Ideas',
    'Streetwear Fashion Instagram',
    'Luxury Fashion – Roxx Inspire',
    'Luxury Classy Outfits',
    'Luxury Streetwear Brands',
    
    # Instagram Pages
    '@minimalstreetstyle',
    '@outfitgrid',
    '@outfitpage',
    '@mensfashionpost',
    '@stadiumgoods',
    '@flightclub',
    '@hodinkee',
    '@wristcheck',
    '@purseblog',
    '@sunglasshut',
    '@rayban',
    '@prada',
    '@cartier',
    '@thesolesupplier',
]

MAX_IMAGES_PER_SOURCE = 5  # ~5 images per source = ~125 total
MAX_TOTAL_IMAGES = 300  # Keep max 300 images in DB


class Command(BaseCommand):
    help = 'Pre-populate gallery with scraped fashion images'

    SCRAPINGBEE_API_KEY = 'DGQAE9RYPCV7J6C2AMGV1H2OBV3BMAJ8P4NKVH6WBVRAF4RIV38BFVN2WKPFTE707RAAE9NX8DWKCPYN'
    TARGET_IMAGES_PER_CATEGORY = 50 # This is likely obsolete with MAX_IMAGES_PER_SOURCE, but kept as it wasn't explicitly removed.

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Starting gallery pre-population...'))
        
        # Delete old images if we're at or near capacity
        current_count = ScrapedImage.objects.count()
        if current_count >= MAX_TOTAL_IMAGES:
            # Delete oldest 50% to make room
            delete_count = current_count // 2
            oldest_images = ScrapedImage.objects.order_by('created_at')[:delete_count]
            oldest_ids = list(oldest_images.values_list('id', flat=True))
            ScrapedImage.objects.filter(id__in=oldest_ids).delete()
            self.stdout.write(self.style.WARNING(f'Deleted {len(oldest_ids)} old images to make room'))
        
        total_added = 0 # Renamed from total_scraped to match original variable name
        
        for term in SCRAPING_TERMS:
            self.stdout.write(f'\n📸 Processing term: "{term}"')
            
            # The original existing_count check was removed as per the instruction's implied new logic
            # where MAX_TOTAL_IMAGES and MAX_IMAGES_PER_SOURCE manage capacity.
            
            # Scrape images
            try:
                images = self.scrape_pinterest(term)
                
                if not images:
                    self.stdout.write(self.style.ERROR(f'   ❌ No images scraped for "{term}"'))
                    continue
                
                # Store in database with embeddings (limit to MAX_IMAGES_PER_SOURCE)
                images_to_store = images[:MAX_IMAGES_PER_SOURCE]
                added = self.store_images(images_to_store, term)
                total_added += added
                
                self.stdout.write(self.style.SUCCESS(f'   ✅ Added {added} images'))
                
                # Rate limiting - wait between categories
                time.sleep(2)
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'   ❌ Error: {str(e)}'))
                continue
        
        self.stdout.write(self.style.SUCCESS(f'\n🎉 Pre-population complete! Total images added: {total_added}'))

    def scrape_pinterest(self, query):
        """Scrape images from Pinterest using ScrapingBee"""
        pinterest_url = f'https://in.pinterest.com/search/pins/?q={requests.utils.quote(query)}'
        
        extract_rules = {
            'images': {
                'selector': 'img',
                'type': 'list',
                'output': {
                    'src': 'img@src',
                    'alt': 'img@alt'
                }
            }
        }
        
        scrapingbee_url = 'https://app.scrapingbee.com/api/v1'
        params = {
            'api_key': self.SCRAPINGBEE_API_KEY,
            'url': pinterest_url,
            'extract_rules': str(extract_rules),
            'render_js': 'true',
            'wait': '2000'
        }
        
        self.stdout.write(f'   🔍 Scraping Pinterest...')
        response = requests.get(scrapingbee_url, params=params, timeout=30)
        
        if not response.ok:
            raise Exception(f'ScrapingBee error: {response.status_code}')
        
        data = response.json()
        
        # Filter for valid Pinterest images
        filtered_images = []
        for img in data.get('images', []):
            src = img.get('src', '')
            alt = img.get('alt', '')
            
            if ('i.pinimg.com' in src and 
                ('236x' in src or '474x' in src or '736x' in src) and
                alt and len(alt) > 10):
                
                filtered_images.append({
                    'image_url': src.replace('236x', '474x'),
                    'thumbnail_url': src,
                    'caption': alt,
                })
        
        self.stdout.write(f'   📊 Scraped {len(filtered_images)} valid images')
        return filtered_images[:self.TARGET_IMAGES_PER_CATEGORY]

    def store_images(self, images, query):
        """Store images in database with CLIP embeddings"""
        added_count = 0
        
        for img_data in images:
            try:
                # Check if image already exists
                if ScrapedImage.objects.filter(image_url=img_data['image_url']).exists():
                    continue
                
                # Generate CLIP embedding
                self.stdout.write(f'   🧠 Generating embedding for: {img_data["caption"][:40]}...')
                embedding = ml_service.generate_image_embedding(img_data['image_url'])
                
                # Create database entry
                ScrapedImage.objects.create(
                    image_url=img_data['image_url'],
                    thumbnail_url=img_data['thumbnail_url'],
                    source='pinterest',
                    caption=img_data['caption'],
                    query=query,
                    visual_embedding=embedding,
                    hashtags=[]
                )
                
                added_count += 1
                
                # Small delay to avoid overwhelming the system
                time.sleep(0.5)
                
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'   ⚠️  Failed to store image: {str(e)}'))
                continue
        
        return added_count
