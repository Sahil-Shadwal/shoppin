from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import F
from pgvector.django import CosineDistance
import requests
from PIL import Image
import os
import tempfile
from ultralytics import YOLO

from .models import ScrapedImage, Product
from .serializers import (
    ScrapedImageSerializer,
    ScrapedImageCreateSerializer,
    ProductSerializer
)
from .ml_service import ml_service

# Global YOLO model (load once)
yolo = YOLO('yolov8n.pt')  # using the tiny model for speed

# Helper to download image to a temporary file
def download_image(url: str) -> str:
    resp = requests.get(url, stream=True, timeout=10)
    resp.raise_for_status()
    fd, path = tempfile.mkstemp(suffix='.jpg')
    with os.fdopen(fd, 'wb') as out:
        for chunk in resp.iter_content(chunk_size=8192):
            out.write(chunk)
    return path

@api_view(['POST'])
def store_scraped_images(request):
    """
    Endpoint for Next.js to send scraped images in bulk.
    Generates CLIP embeddings for each image before saving.
    """
    images_data = request.data.get('images', [])
    
    if not images_data:
        return Response(
            {'error': 'No images provided'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    created_images = []
    errors = []
    
    for img_data in images_data:
        # Generate embedding
        image_url = img_data.get('image_url')
        if image_url:
            embedding = ml_service.generate_image_embedding(image_url)
            if embedding:
                img_data['visual_embedding'] = embedding
        
        serializer = ScrapedImageCreateSerializer(data=img_data)
        if serializer.is_valid():
            image = serializer.save()
            created_images.append(image)
        else:
            errors.append({
                'data': img_data,
                'errors': serializer.errors
            })
    
    return Response({
        'success': True,
        'created_count': len(created_images),
        'error_count': len(errors),
        'created_ids': [img.id for img in created_images],
        'errors': errors if errors else None
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def get_gallery(request):
    """
    Get scraped images for gallery display.
    Supports pagination and filtering.
    """
    source = request.query_params.get('source')  # pinterest or instagram
    limit = int(request.query_params.get('limit', 50))
    offset = int(request.query_params.get('offset', 0))
    
    queryset = ScrapedImage.objects.all()
    
    if source:
        queryset = queryset.filter(source=source)
    
    images = queryset[offset:offset + limit]
    total_count = queryset.count()
    
    serializer = ScrapedImageSerializer(images, many=True)
    
    return Response({
        'success': True,
        'images': serializer.data,
        'total': total_count,
        'limit': limit,
        'offset': offset
    })


@api_view(['GET'])
def get_products(request):
    """Get all products (or filtered)"""
    category = request.query_params.get('category')
    
    queryset = Product.objects.all()
    
    if category:
        queryset = queryset.filter(category=category)
    
    serializer = ProductSerializer(queryset, many=True)
    
    return Response({
        'success': True,
        'products': serializer.data
    })


@api_view(['POST'])
def shop_the_look(request):
    """
    'Shop the Look' endpoint.
    Uses YOLO to detect person in image, crops that region, and searches across categories.
    """
    try:
        print("Shop the Look request received")
        image_url = request.data.get('external_image_url')
        query_text = request.data.get('query_text')
        
        if not image_url:
            print("Error: external_image_url missing")
            return Response({'error': 'external_image_url is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 1️⃣ Download image locally
        print(f"Downloading image: {image_url}")
        local_path = download_image(image_url)
        
        # 2️⃣ Run YOLO detection to find person
        print("Running YOLO detection...")
        detections = yolo.predict(source=local_path, conf=0.25, verbose=False)[0].boxes
        
        # Find the person with highest confidence
        person_box = None
        max_conf = 0
        for det in detections:
            class_id = int(det.cls)
            class_name = yolo.names[class_id]
            conf = float(det.conf)
            print(f"Detected: {class_name} (conf: {conf:.2f})")
            
            if class_name == 'person' and conf > max_conf:
                max_conf = conf
                person_box = det
        
        # 3️⃣ Generate query embedding
        query_embedding = None
        if person_box is not None:
            # Crop person region and use it as query
            print(f"Found person with confidence {max_conf:.2f}, cropping region")
            x1, y1, x2, y2 = map(int, person_box.xyxy[0].tolist())
            img = Image.open(local_path)
            
            # Add some padding (10%) to capture full outfit
            width, height = img.size
            padding_x = int((x2 - x1) * 0.1)
            padding_y = int((y2 - y1) * 0.1)
            x1 = max(0, x1 - padding_x)
            y1 = max(0, y1 - padding_y)
            x2 = min(width, x2 + padding_x)
            y2 = min(height, y2 + padding_y)
            
            person_region = img.crop((x1, y1, x2, y2))
            
            # Save cropped region
            fd, region_path = tempfile.mkstemp(suffix='.jpg')
            os.close(fd)
            person_region.save(region_path)
            
            # Generate embedding from cropped person
            query_embedding = ml_service.generate_image_embedding(region_path)
            os.unlink(region_path)  # Clean up temp file
        else:
            # No person detected, use full image
            print("No person detected, using full image")
            query_embedding = ml_service.generate_image_embedding(image_url)
        
        # Clean up downloaded image
        os.unlink(local_path)
        
        text_embedding = None
        if query_text:
            print(f"Generating text embedding for: {query_text}")
            text_embedding = ml_service.generate_text_embedding(query_text)
        
        if not query_embedding:
            print("Error: Failed to generate image embedding")
            return Response({'error': 'Failed to generate embedding'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 4️⃣ Search across all categories
        categories = ['tops', 'bottoms', 'footwear', 'outerwear', 'accessories']
        results = {}
        
        print("Scanning categories...")
        for category in categories:
            queryset = Product.objects.filter(category__icontains=category)
            
            if not queryset.exists():
                print(f"No products found for category: {category}")
                continue
            
            if text_embedding:
                # Hybrid Search
                matches = queryset.annotate(
                    visual_dist=CosineDistance('visual_embedding', query_embedding),
                    text_dist=CosineDistance('text_embedding', text_embedding)
                ).annotate(
                    combined_dist=(F('visual_dist') * 0.6) + (F('text_dist') * 0.4)
                ).order_by('combined_dist')[:4]
            else:
                # Visual Only
                matches = queryset.annotate(
                    distance=CosineDistance('visual_embedding', query_embedding)
                ).order_by('distance')[:4]
            
            if matches:
                print(f"Found {len(matches)} matches for {category}")
                cat_results = []
                for product in matches:
                    if hasattr(product, 'combined_dist'):
                        score = 1 - product.combined_dist
                    else:
                        score = 1 - product.distance if product.distance is not None else 0
                    cat_results.append({
                        "product_id": product.product_id,
                        "title": product.title,
                        "image_url": product.image_url,
                        "price": product.price,
                        "visual_score": score,
                        "brand": product.brand_name
                    })
                results[category] = cat_results
        
        print(f"Shop the Look completed. Categories found: {list(results.keys())}")
        return Response({"success": True, "results": results})
    except Exception as e:
        print(f"CRITICAL ERROR in shop_the_look: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def search_by_image(request):
    """
    Visual search endpoint - receives image URL, returns similar products.
    Uses CLIP embeddings and vector similarity search.
    """
    image_url = request.data.get('external_image_url')
    top_k = int(request.data.get('top_k', 10))
    
    if not image_url:
        return Response({'error': 'external_image_url is required'}, status=status.HTTP_400_BAD_REQUEST)

    # 1. Generate embedding for query image
    print(f"Generating embedding for: {image_url}")
    query_embedding = ml_service.generate_image_embedding(image_url)
    if not query_embedding:
        print("Failed to generate embedding")
        return Response({'error': 'Failed to generate embedding for image'}, status=status.HTTP_400_BAD_REQUEST)

    print(f"Query embedding generated. Shape: {len(query_embedding)}")

    # Check for optional text query for hybrid search
    query_text = request.data.get('query_text')
    text_embedding = None
    if query_text:
        print(f"Generating text embedding for: {query_text}")
        text_embedding = ml_service.generate_text_embedding(query_text)

    # Check for category filter
    category = request.data.get('category')
    queryset = Product.objects.all()
    if category:
        print(f"Filtering by category: {category}")
        queryset = queryset.filter(category=category)

    # 2. Search in Products table
    if text_embedding:
        # Hybrid Search
        print("Performing Hybrid Search")
        matches = queryset.annotate(
            visual_dist=CosineDistance('visual_embedding', query_embedding),
            text_dist=CosineDistance('text_embedding', text_embedding)
        ).annotate(
            # Weighted average: 60% visual, 40% text
            # Note: CosineDistance is 0 for identical, 1 for orthogonal. Lower is better.
            combined_dist=(F('visual_dist') * 0.6) + (F('text_dist') * 0.4)
        ).order_by('combined_dist')[:top_k]
    else:
        # Visual Only
        print("Performing Visual Only Search")
        matches = queryset.annotate(
            distance=CosineDistance('visual_embedding', query_embedding)
        ).order_by('distance')[:top_k]
    
    print(f"Found {len(matches)} matches")
    for m in matches:
        dist = getattr(m, 'combined_dist', getattr(m, 'distance', 0))
        print(f"Match: {m.title} - Distance: {dist}")

    # 3. Serialize results
    results = []
    for product in matches:
        # Determine which distance to use for score
        if hasattr(product, 'combined_dist'):
            score = 1 - product.combined_dist
        else:
            score = 1 - product.distance if product.distance is not None else 0

        results.append({
            "product_id": product.product_id,
            "title": product.title,
            "image_url": product.image_url,
            "price": product.price,
            "visual_score": score, 
            "brand": product.brand_name,
            "category": product.category
        })

    return Response({
        "matches": results,
        "total_results": len(results)
    })


@api_view(['POST'])
def search_by_text(request):
    """
    Text search endpoint - receives text query, returns matching products.
    Uses Sentence-Transformer embeddings and vector similarity search.
    """
    query = request.data.get('query')
    top_k = int(request.data.get('top_k', 10))
    
    if not query:
        return Response({'error': 'query is required'}, status=status.HTTP_400_BAD_REQUEST)

    # 1. Generate embedding for text query
    query_embedding = ml_service.generate_text_embedding(query)
    if not query_embedding:
        return Response({'error': 'Failed to generate embedding for text'}, status=status.HTTP_400_BAD_REQUEST)

    # 2. Search in Products table using Cosine Distance on text_embedding
    matches = Product.objects.annotate(
        distance=CosineDistance('text_embedding', query_embedding)
    ).order_by('distance')[:top_k]
    
    # 3. Serialize results
    results = []
    for product in matches:
        results.append({
            "product_id": product.product_id,
            "title": product.title,
            "image_url": product.image_url,
            "price": product.price,
            "semantic_score": 1 - product.distance if product.distance is not None else 0,
            "brand": product.brand_name,
            "category": product.category
        })

    return Response({
        "matches": results,
        "total_results": len(results)
    })

