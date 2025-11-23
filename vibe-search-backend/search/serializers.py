from rest_framework import serializers
from .models import ScrapedImage, Product


class ScrapedImageSerializer(serializers.ModelSerializer):
    """Serializer for scraped images"""
    
    class Meta:
        model = ScrapedImage
        fields = [
            'id', 'image_url', 'thumbnail_url', 'source', 'caption',
            'hashtags', 'likes', 'comments', 'posted_date', 'user_info',
            'query', 'scraped_at', 'updated_at'
        ]
        read_only_fields = ['id', 'scraped_at', 'updated_at']


class ScrapedImageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating scraped images (bulk from Next.js)"""
    
    class Meta:
        model = ScrapedImage
        fields = [
            'image_url', 'thumbnail_url', 'source', 'caption',
            'hashtags', 'likes', 'comments', 'posted_date', 'user_info', 'query'
        ]


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for products"""
    
    class Meta:
        model = Product
        fields = [
            'product_id', 'title', 'brand_name', 'category', 'image_url',
            'price', 'pdp_url', 'colors', 'style_tags', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ProductSearchResultSerializer(serializers.Serializer):
    """Serializer for product search results with scores"""
    
    product = ProductSerializer()
    visual_score = serializers.FloatField()
    semantic_score = serializers.FloatField(required=False)
    combined_score = serializers.FloatField()
    match_reasons = serializers.ListField(child=serializers.CharField())


class ImageSearchRequestSerializer(serializers.Serializer):
    """Serializer for image search requests"""
    
    external_image_url = serializers.URLField()
    top_k = serializers.IntegerField(default=10, min_value=1, max_value=50)
    rerank = serializers.BooleanField(default=False)
    filters = serializers.JSONField(required=False)


class TextSearchRequestSerializer(serializers.Serializer):
    """Serializer for text search requests"""
    
    query = serializers.CharField(max_length=500)
    top_k = serializers.IntegerField(default=10, min_value=1, max_value=50)
    filters = serializers.JSONField(required=False)
