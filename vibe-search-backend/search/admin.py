from django.contrib import admin
from .models import ScrapedImage, Product


@admin.register(ScrapedImage)
class ScrapedImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'source', 'caption_preview', 'query', 'likes', 'scraped_at']
    list_filter = ['source', 'scraped_at']
    search_fields = ['caption', 'query']
    readonly_fields = ['id', 'scraped_at', 'updated_at']
    
    def caption_preview(self, obj):
        return obj.caption[:50] if obj.caption else 'No caption'
    caption_preview.short_description = 'Caption'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['product_id', 'title', 'brand_name', 'category', 'price', 'created_at']
    list_filter = ['category', 'brand_name']
    search_fields = ['title', 'brand_name', 'product_id']
    readonly_fields = ['created_at', 'updated_at']
