import requests
import time
from django.core.management.base import BaseCommand
from search.models import ScrapedImage
from search.ml_service import ml_service


class Command(BaseCommand):
    help = 'Pre-populate gallery with images from Pinterest for multiple categories'

    terms = [
        'Minimal Streetwear',
        "Men's Streetwear Outfit Ideas",
        'Streetwear Outfit Ideas',
        'Streetwear Fashion Instagram',
        'Luxury Fashion – Roxx Inspire',
        'Luxury Classy Outfits',
        'Luxury Streetwear Brands',
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
        '@thesolesupplier'
    ]

    SCRAPINGBEE_API_KEY = 'LO2AZHTXFTWM383O0SHXU9EGZG86OZFGI6RIMLRPFXM4I7W0AKQKWK2ASO0CC3IPYJH7W607060YPW89'
    TARGET_IMAGES_PER_CATEGORY = 50

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Starting gallery pre-population...'))
        
        total_added = 0
        
        for category in self.CATEGORIES:
            self.stdout.write(f'\n📸 Processing category: "{category}"')
            
            # Check how many images we already have for this category
            existing_count = ScrapedImage.objects.filter(query=category).count()
            self.stdout.write(f'   Existing images: {existing_count}')
            
            if existing_count >= self.TARGET_IMAGES_PER_CATEGORY:
                self.stdout.write(self.style.WARNING(f'   ⏭️  Skipping (already has {existing_count} images)'))
                continue
            
            # Scrape images
            try:
                images = self.scrape_pinterest(category)
                
                if not images:
                    self.stdout.write(self.style.ERROR(f'   ❌ No images scraped for "{category}"'))
                    continue
                
                # Store in database with embeddings
                added = self.store_images(images, category)
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
