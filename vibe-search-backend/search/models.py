from django.db import models
from pgvector.django import VectorField


class ScrapedImage(models.Model):
    """Images scraped from Pinterest/Instagram for inspiration gallery"""
    
    SOURCE_CHOICES = [
        ('pinterest', 'Pinterest'),
        ('instagram', 'Instagram'),
    ]
    
    image_url = models.URLField(max_length=1000)
    thumbnail_url = models.URLField(max_length=1000, blank=True, null=True)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    caption = models.TextField(blank=True, null=True)
    hashtags = models.JSONField(default=list, blank=True)
    likes = models.IntegerField(null=True, blank=True)
    comments = models.IntegerField(null=True, blank=True)
    posted_date = models.DateTimeField(null=True, blank=True)
    user_info = models.JSONField(default=dict, blank=True)
    query = models.CharField(max_length=255, blank=True)
    
    # CLIP visual embedding (512 dimensions for CLIP ViT-B/32)
    visual_embedding = VectorField(dimensions=512, null=True, blank=True)
    
    scraped_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'scraped_images'
        ordering = ['-scraped_at']
        indexes = [
            models.Index(fields=['-scraped_at']),
            models.Index(fields=['source']),
        ]
    
    def __str__(self):
        return f"{self.source} - {self.caption[:50] if self.caption else 'No caption'}"


class Product(models.Model):
    """Internal product catalog for matching against scraped images"""
    
    CATEGORY_CHOICES = [
        ('footwear', 'Footwear'),
        ('tops', 'Tops'),
        ('bottoms', 'Bottoms'),
        ('outerwear', 'Outerwear'),
        ('accessories', 'Accessories'),
        ('swimwear', 'Swimwear'),
    ]
    
    product_id = models.CharField(max_length=100, unique=True, primary_key=True)
    title = models.CharField(max_length=500)
    brand_name = models.CharField(max_length=200, blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    image_url = models.URLField(max_length=1000)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    pdp_url = models.URLField(max_length=1000, blank=True, null=True)  # Product page URL
    
    # Auto-extracted metadata
    colors = models.JSONField(default=list, blank=True)  # ["Black", "White"]
    style_tags = models.JSONField(default=list, blank=True)  # ["streetwear", "minimal"]
    
    # Embeddings
    visual_embedding = VectorField(dimensions=512, null=True, blank=True)  # CLIP
    text_embedding = VectorField(dimensions=384, null=True, blank=True)  # Sentence-Transformers
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'products'
        ordering = ['product_id']
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['brand_name']),
        ]
    
    def __str__(self):
        return f"{self.product_id} - {self.title}"

