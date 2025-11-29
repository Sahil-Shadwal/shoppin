from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
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

# Global YOLO models (load once)
yolo = YOLO('yolov8n-pose.pt')  # using the pose model
yolo_obj = YOLO('yolov8n.pt')   # using the object detection model

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
    query = request.query_params.get('query')  # filter by search query/category
    limit = int(request.query_params.get('limit', 50))
    offset = int(request.query_params.get('offset', 0))
    
    queryset = ScrapedImage.objects.all()
    
    if source:
        queryset = queryset.filter(source=source)
    
    if query:
        queryset = queryset.filter(query=query)
    
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
    Uses YOLO-Pose to detect person and keypoints, crops specific regions based on category.
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
        
        # Extract category EARLY to use for cropping
        requested_category = request.data.get('category')
        print(f"Requested category for cropping: {requested_category}") # DEBUG
        
        # 3️⃣ Generate query embedding
        query_embedding = None
        detected_box = None  # To store normalized coordinates [x1, y1, x2, y2]
        
        img = Image.open(local_path)
        img_width, img_height = img.size

        # Handle Object Detection Categories (Bags, Bottles)
        if requested_category in ['bags', 'bottles']:
            print(f"Running YOLO Object Detection for {requested_category}...")
            results_obj = yolo_obj.predict(source=local_path, conf=0.15, verbose=False)[0]
            detections_obj = results_obj.boxes
            
            target_classes = []
            if requested_category == 'bags':
                target_classes = [24, 26, 28] # backpack, handbag, suitcase
            elif requested_category == 'bottles':
                target_classes = [39] # bottle
            
            best_obj_box = None
            max_conf = 0
            
            for det in detections_obj:
                cls_id = int(det.cls)
                conf = float(det.conf)
                if cls_id in target_classes and conf > max_conf:
                    max_conf = conf
                    best_obj_box = det
            
            if best_obj_box:
                print(f"Found {requested_category} with confidence {max_conf:.2f}")
                x1, y1, x2, y2 = map(int, best_obj_box.xyxy[0].tolist())
                
                # Add padding
                w = x2 - x1
                h = y2 - y1
                pad_x = w * 0.1
                pad_y = h * 0.1
                
                crop_x1 = max(0, int(x1 - pad_x))
                crop_y1 = max(0, int(y1 - pad_y))
                crop_x2 = min(img_width, int(x2 + pad_x))
                crop_y2 = min(img_height, int(y2 + pad_y))
                
                detected_box = [
                    crop_x1 / img_width,
                    crop_y1 / img_height,
                    crop_x2 / img_width,
                    crop_y2 / img_height
                ]
                
                obj_region = img.crop((crop_x1, crop_y1, crop_x2, crop_y2))
                
                # Save cropped region
                fd, region_path = tempfile.mkstemp(suffix='.jpg')
                os.close(fd)
                obj_region.save(region_path)
                
                query_embedding = ml_service.generate_image_embedding(region_path)
                os.unlink(region_path)
            else:
                print(f"No {requested_category} detected, falling back to full image")
                query_embedding = ml_service.generate_image_embedding(image_url)

        else:
            # Handle Person/Pose Categories
            print("Running YOLO-Pose detection...")
            results = yolo.predict(source=local_path, conf=0.25, verbose=False)[0]
            detections = results.boxes
            keypoints = results.keypoints
            
            # Find the person with highest confidence
            person_idx = -1
            max_conf = 0
            
            for i, det in enumerate(detections):
                class_id = int(det.cls)
                class_name = yolo.names[class_id]
                conf = float(det.conf)
                
                if class_name == 'person' and conf > max_conf:
                    max_conf = conf
                    person_idx = i
            
            if person_idx != -1:
                # Get person box and keypoints
                person_box = detections[person_idx]
                kpts = keypoints[person_idx].xy[0].cpu().numpy() # (17, 2) array of x,y
                
                print(f"Found person with confidence {max_conf:.2f}")
                x1, y1, x2, y2 = map(int, person_box.xyxy[0].tolist())
                
                # Keypoint indices for COCO format:
                # 0: nose, 1: left_eye, 2: right_eye, 3: left_ear, 4: right_ear
                # 5: left_shoulder, 6: right_shoulder, 7: left_elbow, 8: right_elbow
                # 9: left_wrist, 10: right_wrist, 11: left_hip, 12: right_hip
                # 13: left_knee, 14: right_knee, 15: left_ankle, 16: right_ankle
                
                crop_x1, crop_y1, crop_x2, crop_y2 = x1, y1, x2, y2
                
                # Helper to get bounding box of specific keypoints
                def get_kpt_box(indices, padding=0.1):
                    valid_kpts = [kpts[i] for i in indices if kpts[i][0] > 0 and kpts[i][1] > 0]
                    if not valid_kpts:
                        return None
                    
                    kx = [k[0] for k in valid_kpts]
                    ky = [k[1] for k in valid_kpts]
                    
                    min_x, max_x = min(kx), max(kx)
                    min_y, max_y = min(ky), max(ky)
                    
                    w = max_x - min_x
                    h = max_y - min_y
                    
                    pad_x = w * padding
                    pad_y = h * padding
                    
                    return (
                        max(0, int(min_x - pad_x)),
                        max(0, int(min_y - pad_y)),
                        min(img_width, int(max_x + pad_x)),
                        min(img_height, int(max_y + pad_y))
                    )
    
                if requested_category == 'tops':
                    # Shoulders to Hips
                    box = get_kpt_box([5, 6, 11, 12], padding=0.2)
                    if box:
                        crop_x1, crop_y1, crop_x2, crop_y2 = box
                        print("Applied 'tops' crop (Shoulders to Hips)")
                    else:
                        # Fallback
                        p_height = y2 - y1
                        crop_y2 = y1 + int(p_height * 0.6)
                        print("Fallback: 'tops' crop (Top 60%)")
                        
                elif requested_category == 'bottoms':
                    # Hips to Ankles
                    box = get_kpt_box([11, 12, 15, 16], padding=0.1)
                    if box:
                        crop_x1, crop_y1, crop_x2, crop_y2 = box
                        print("Applied 'bottoms' crop (Hips to Ankles)")
                    else:
                        # Fallback
                        p_height = y2 - y1
                        crop_y1 = y1 + int(p_height * 0.4)
                        print("Fallback: 'bottoms' crop (Bottom 60%)")
                        
                elif requested_category == 'footwear':
                    # IMPROVED: Cover BOTH shoes properly, using knees to ankles + extra padding
                    # This ensures we get both shoes even when knees are bent/folded
                    
                    # Get all relevant keypoints: knees (13, 14) and ankles (15, 16)
                    relevant_kpts = [13, 14, 15, 16]  # left_knee, right_knee, left_ankle, right_ankle
                    valid_kpts = [kpts[i] for i in relevant_kpts if kpts[i][0] > 0 and kpts[i][1] > 0]
                    
                    if len(valid_kpts) >= 2:  # Need at least 2 keypoints
                        kx = [k[0] for k in valid_kpts]
                        ky = [k[1] for k in valid_kpts]
                        
                        min_x, max_x = min(kx), max(kx)
                        min_y, max_y = min(ky), max(ky)
                        
                        # Person context for sizing
                        p_w = x2 - x1
                        p_h = y2 - y1
                        
                        # CRITICAL: Generous padding to capture BOTH shoes
                        # Horizontal: ensure we cover full width of both shoes
                        w = max_x - min_x
                        pad_x = max(w * 0.8, p_w * 0.3)  # At least 30% of person width or 80% of detected range
                        
                        # Vertical: extend significantly below ankles for full shoes
                        h = max_y - min_y
                        pad_y_top = h * 0.2   # Small padding above (from knees)
                        pad_y_bottom = max(h * 1.0, p_h * 0.25)  # Generous padding below ankles for shoes
                        
                        box = (
                            max(0, int(min_x - pad_x)),
                            max(0, int(min_y - pad_y_top)),
                            min(img_width, int(max_x + pad_x)),
                            min(img_height, int(max_y + pad_y_bottom))
                        )
                        
                def apply_category_crop(bbox, category, image_height, image_width):
                    """
                    Apply very precise category-specific cropping to detected person bounding box.
                    Makes boxes much tighter and more accurate for each category.
                    
                    Args:
                        bbox: Original person bounding box [x1, y1, x2, y2]
                        category: Selected category (shoes, bottoms, tops, etc.)
                        image_height: Full image height
                        image_width: Full image width
                    
                    Returns:
                        Cropped bounding box [x1, y1, x2, y2]
                    """
                    x1, y1, x2, y2 = bbox
                    box_height = y2 - y1
                    box_width = x2 - x1
                    
                    # Calculate person segments (more precise)
                    head_end = y1 + box_height * 0.15      # Top 15% is head
                    chest_start = y1 + box_height * 0.15   # Chest starts after head
                    waist = y1 + box_height * 0.45         # Waist at 45% 
                    hip = y1 + box_height * 0.55           # Hip at 55%
                    knee = y1 + box_height * 0.75          # Knee at 75%
                    ankle_start = y1 + box_height * 0.88   # Ankles start at 88%
                    
                    if category == 'footwear' or category == 'shoes':
                        # SHOES: Start from KNEE level to catch bent-knee poses
                        # Extend much wider to ensure BOTH shoes are captured
                        cropped_x1 = max(0, x1 - box_width * 0.25)  # Extend 25% left for wide stance
                        cropped_y1 = max(0, knee)                   # Start at KNEE, not ankle
                        cropped_x2 = min(image_width, x2 + box_width * 0.25)  # Extend 25% right
                        cropped_y2 = y2  # Bottom of person
                        
                    elif category == 'bottoms':
                        # BOTTOMS: Waist to ankles (45% to 88% of person height)
                        # Includes full pants/jeans but excludes shoes
                        cropped_x1 = max(0, x1 - box_width * 0.1)   # Extend 10% for baggy jeans
                        cropped_y1 = max(0, waist)                  # Start at waist
                        cropped_x2 = min(image_width, x2 + box_width * 0.1)  # Extend 10% right
                        cropped_y2 = min(image_height, ankle_start) # End just before shoes
                        
                    elif category == 'tops':
                        # TOPS: Head to waist (0% to 50% of person height)
                        # Includes shirts, sweaters, jackets worn on upper body
                        cropped_x1 = max(0, x1 - box_width * 0.15)  # Extend for sleeves
                        cropped_y1 = y1                              # Start from top
                        cropped_x2 = min(image_width, x2 + box_width * 0.15)  # Extend for sleeves
                        cropped_y2 = min(image_height, hip)         # End at hip
                        
                    elif category == 'outerwear' or category == 'jackets':
                        # OUTERWEAR: Head to hip (0% to 60% of person height)
                        # Longer than tops to include jacket length
                        cropped_x1 = max(0, x1 - box_width * 0.2)   # Extend more for oversized
                        cropped_y1 = y1                              # Start from top
                        cropped_x2 = min(image_width, x2 + box_width * 0.2)
                        cropped_y2 = min(image_height, knee)        # End at knee level
                        
                    elif category == 'accessories':
                        # ACCESSORIES: Focus on upper body and head area
                        cropped_x1 = max(0, x1 - box_width * 0.2)
                        cropped_y1 = y1                              # Include head
                        cropped_x2 = min(image_width, x2 + box_width * 0.2)
                        cropped_y2 = min(image_height, chest_start + box_height * 0.2)
                        
                    elif category == 'bags':
                        # BAGS: Usually carried at hip/shoulder level
                        cropped_x1 = max(0, x1 - box_width * 0.3)   # Extend to catch bags on sides
                        cropped_y1 = max(0, chest_start)            # Start at chest
                        cropped_x2 = min(image_width, x2 + box_width * 0.3)
                        cropped_y2 = min(image_height, hip + box_height * 0.2)
                        
                    else:
                        # DEFAULT: Use full person detection
                        cropped_x1 = x1
                        cropped_y1 = y1
                        cropped_x2 = x2
                        cropped_y2 = y2
                    
                    # Ensure box has minimum size (at least 50 pixels in each dimension)
                    min_size = 50
                    if (cropped_x2 - cropped_x1) < min_size:
                        center_x = (cropped_x1 + cropped_x2) / 2
                        cropped_x1 = max(0, center_x - min_size / 2)
                        cropped_x2 = min(image_width, center_x + min_size / 2)
                    
                    if (cropped_y2 - cropped_y1) < min_size:
                        center_y = (cropped_y1 + cropped_y2) / 2
                        cropped_y1 = max(0, center_y - min_size / 2)
                        cropped_y2 = min(image_height, center_y + min_size / 2)
                    
                    return [int(cropped_x1), int(cropped_y1), int(cropped_x2), int(cropped_y2)]
                
                # Apply precise category crop
                crop_x1, crop_y1, crop_x2, crop_y2 = apply_category_crop(
                    [x1, y1, x2, y2], requested_category, img_height, img_width
                )
                print(f"Applied '{requested_category}' crop: [{crop_x1}, {crop_y1}, {crop_x2}, {crop_y2}]")
                
                # Ensure coordinates are within image bounds and valid
                crop_x1 = max(0, int(crop_x1))
                crop_y1 = max(0, int(crop_y1))
                crop_x2 = min(img_width, int(crop_x2))
                crop_y2 = min(img_height, int(crop_y2))
                
                # Safety check: if crop is too small or invalid, revert to full person
                if crop_x2 <= crop_x1 + 10 or crop_y2 <= crop_y1 + 10:
                    print("Warning: Invalid crop dimensions, reverting to full person")
                    crop_x1, crop_y1, crop_x2, crop_y2 = x1, y1, x2, y2
    
                # Calculate normalized coordinates for frontend using the SPECIFIC CROP
                detected_box = [
                    crop_x1 / img_width,
                    crop_y1 / img_height,
                    crop_x2 / img_width,
                    crop_y2 / img_height
                ]
                
                person_region = img.crop((crop_x1, crop_y1, crop_x2, crop_y2))
                
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
        # Parse query for target categories if text is provided
        target_categories = None
        if query_text:
            try:
                from .gemini_utils import parse_search_query
                parsed_data = parse_search_query(query_text)
                if parsed_data.get('target_categories'):
                    target_categories = parsed_data['target_categories']
                    print(f"Gemini inferred target categories: {target_categories}")
            except Exception as e:
                print(f"Error parsing query for categories: {e}")

        if target_categories:
            # CRITICAL: If searching for multiple categories (e.g. "complete look"), 
            # exclude the category of the uploaded item itself.
            # User already has shoes, they don't want more shoes in the "complete look".
            if requested_category and requested_category in target_categories and len(target_categories) > 1:
                print(f"Excluding source category '{requested_category}' from target categories.")
                target_categories.remove(requested_category)
                
            categories = target_categories
        elif requested_category:
            categories = [requested_category]
        else:
            categories = ['tops', 'bottoms', 'footwear', 'outerwear', 'accessories']
            
        requested_brand = request.data.get('brand')
        if requested_brand and requested_brand.lower() == 'all':
            requested_brand = None
            
        requested_color = request.data.get('color')
        if requested_color and requested_color.lower() == 'all':
            requested_color = None
            
        results = {}
        
        print(f"Scanning categories: {categories} | Brand: {requested_brand} | Color: {requested_color}") # DEBUG
        for category in categories:
            queryset = Product.objects.filter(category__icontains=category)
            
            if requested_brand:
                queryset = queryset.filter(brand_name__icontains=requested_brand)
                
            if requested_color:
                # Filter by title containing the color since 'colors' field might be empty
                queryset = queryset.filter(title__icontains=requested_color)
            
            print(f"Category {category}: Found {queryset.count()} products in DB") # DEBUG
            
            if not queryset.exists():
                print(f"No products found for category: {category}")
                continue
            
            if text_embedding:
                # Hybrid Search
                matches = queryset.annotate(
                    visual_dist=CosineDistance('visual_embedding', query_embedding),
                    text_dist=CosineDistance('text_embedding', text_embedding)
                ).annotate(
                    combined_dist=(F('visual_dist') * 0.3) + (F('text_dist') * 0.7)
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
                        "pdp_url": product.pdp_url,
                        "visual_score": score,
                        "brand": product.brand_name
                    })
                results[category] = cat_results
            else:
                print(f"No matches found for {category} after vector search") # DEBUG
        
        print(f"Shop the Look completed. Categories found: {list(results.keys())}")
        return Response({
            "success": True, 
            "results": results,
            "detected_box": detected_box
        })
    except Exception as e:
        print(f"CRITICAL ERROR in shop_the_look: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def search_by_image(request):
    """
    Visual search endpoint - receives image URL, returns similar products.
    Uses CLIP embeddings and vector similarity search.
    Supports:
    - max_price: Filter items below a certain price
    - negative_query: Penalize items matching this text description
    """
    image_url = request.data.get('external_image_url')
    image_file = request.FILES.get('image')
    top_k = int(request.data.get('top_k', 10))
    max_price = request.data.get('max_price')
    negative_query = request.data.get('negative_query')
    
    if not image_url and not image_file:
        return Response({'error': 'external_image_url or image file is required'}, status=status.HTTP_400_BAD_REQUEST)

    # 1. Generate embedding for query image
    query_embedding = None
    
    if image_file:
        print(f"Processing uploaded image: {image_file.name}")
        # Save to temp file
        fd, path = tempfile.mkstemp(suffix='.jpg')
        with os.fdopen(fd, 'wb') as out:
            for chunk in image_file.chunks():
                out.write(chunk)
        
        # Generate embedding
        query_embedding = ml_service.generate_image_embedding(path)
        os.unlink(path) # Cleanup
    elif image_url:
        print(f"Generating embedding for: {image_url}")
        query_embedding = ml_service.generate_image_embedding(image_url)
        
    if not query_embedding:
        print("Failed to generate embedding")
        return Response({'error': 'Failed to generate embedding for image'}, status=status.HTTP_400_BAD_REQUEST)

    print(f"Query embedding generated. Shape: {len(query_embedding)}")

    # Check for optional text query for hybrid search
    query_text = request.data.get('query_text')
    text_embedding = None
    category = request.data.get('category') # Initialize category
    
    # Gemini Parsing
    if query_text:
        print(f"Parsing query with Gemini: {query_text}")
        try:
            from .gemini_utils import parse_search_query
            parsed_data = parse_search_query(query_text)
            
            # Update query_text with refined version
            # CRITICAL: If refined_query is explicitly empty string "", it means we should clear the query_text
            # and rely on visual search only (plus category filters).
            refined = parsed_data.get('refined_query')
            if refined is not None:
                query_text = refined
                print(f"Refined Query: '{query_text}'")
                
            # Update negative query
            if parsed_data.get('negative_query'):
                negative_query = parsed_data['negative_query']
                print(f"Inferred Negative Query: {negative_query}")
                
            # Update category if not explicitly provided
            if not request.data.get('category') and parsed_data.get('category'):
                category = parsed_data['category']
                print(f"Inferred Category: {category}")
                
            # Update max_price if inferred
            if parsed_data.get('max_price'):
                max_price = parsed_data['max_price']
                print(f"Inferred Max Price: {max_price}")
                
        except ImportError:
            print("Gemini utils not found, skipping parsing")
        except Exception as e:
            print(f"Error in Gemini parsing: {e}")

    if query_text:
        print(f"Generating text embedding for: {query_text}")
        text_embedding = ml_service.generate_text_embedding(query_text)

    # Generate negative embedding if provided
    negative_embedding = None
    if negative_query:
        print(f"Generating negative embedding for: {negative_query}")
        negative_embedding = ml_service.generate_text_embedding(negative_query)

    # Check for category filter
    # category variable might have been updated by Gemini
    queryset = Product.objects.all()
    
    if category:
        print(f"Filtering by category: {category}")
        queryset = queryset.filter(category=category)
        
    if max_price:
        try:
            price_limit = float(max_price)
            print(f"Filtering by max_price: {price_limit}")
            # Assuming price is stored as float or decimal. If string, might need casting.
            # For now assuming simple filter works.
            queryset = queryset.filter(price__lte=price_limit)
        except ValueError:
            print("Invalid max_price provided")

    # 2. Search in Products table
    if text_embedding:
        # Hybrid Search
        print("Performing Hybrid Search")
        matches = queryset.annotate(
            visual_dist=CosineDistance('visual_embedding', query_embedding),
            text_dist=CosineDistance('text_embedding', text_embedding)
        )
        
        if negative_embedding:
             matches = matches.annotate(
                neg_dist=CosineDistance('text_embedding', negative_embedding)
            ).annotate(
                # Combined: Visual(60%) + Text(40%) + Penalty for closeness to negative
                # If neg_dist is small (close to negative), we want to INCREASE the final distance/reduce score.
                # CosineDistance is [0, 2]. 0 = same, 1 = orthogonal, 2 = opposite.
                # So if neg_dist is small, it's bad.
                # Let's add (1 - neg_dist) * weight to the distance? 
                # Or just subtract neg_dist from score?
                # Simpler: combined_dist - (neg_dist * 0.5) -> No, we sort by distance (asc).
                # So we want to INCREASE distance if it matches negative.
                # Distance += (1 - neg_dist) if neg_dist < 1 else 0
                # Let's try a simple weighted sum where negative similarity adds to distance.
                # Similarity = 1 - distance.
                # We want to minimize: Distance(Query) - Weight * Distance(Negative) ? No.
                # We want to maximize: Sim(Query) - Sim(Negative)
                # => Minimize: (1 - Sim(Query)) + Sim(Negative)
                # => Minimize: Dist(Query) + (1 - Dist(Negative))
                combined_dist=(F('visual_dist') * 0.3) + (F('text_dist') * 0.7) + (1.0 - F('neg_dist')) * 0.5
            )
        else:
            matches = matches.annotate(
                combined_dist=(F('visual_dist') * 0.3) + (F('text_dist') * 0.7)
            )
            
        matches = matches.order_by('combined_dist')[:top_k]
    else:
        # Visual Only
        print("Performing Visual Only Search")
        matches = queryset.annotate(
            distance=CosineDistance('visual_embedding', query_embedding)
        )
        
        if negative_embedding:
            matches = matches.annotate(
                neg_dist=CosineDistance('text_embedding', negative_embedding)
            ).annotate(
                # Penalize visual matches that are semantically close to negative query
                final_dist=F('distance') + (1.0 - F('neg_dist')) * 0.5
            ).order_by('final_dist')[:top_k]
        else:
            matches = matches.order_by('distance')[:top_k]
    
    print(f"Found {len(matches)} matches")
    results = []
    for product in matches:
        # Determine which distance to use for score
        if hasattr(product, 'final_dist'):
             dist = product.final_dist
        elif hasattr(product, 'combined_dist'):
            dist = product.combined_dist
        else:
            dist = product.distance if product.distance is not None else 0
            
        # Normalize score roughly
        score = max(0, 1 - dist)

        results.append({
            "product_id": product.product_id,
            "title": product.title,
            "image_url": product.image_url,
            "price": product.price,
            "pdp_url": product.pdp_url,
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
    Supports:
    - max_price
    - negative_query
    """
    query = request.data.get('query')
    top_k = int(request.data.get('top_k', 10))
    max_price = request.data.get('max_price')
    negative_query = request.data.get('negative_query')
    
    if not query:
        return Response({'error': 'query is required'}, status=status.HTTP_400_BAD_REQUEST)

    # 1. Generate embedding for text query
    query_embedding = ml_service.generate_text_embedding(query)
    if not query_embedding:
        return Response({'error': 'Failed to generate embedding for text'}, status=status.HTTP_400_BAD_REQUEST)

    # Generate negative embedding
    negative_embedding = None
    if negative_query:
        negative_embedding = ml_service.generate_text_embedding(negative_query)

    queryset = Product.objects.all()
    
    if max_price:
        try:
            price_limit = float(max_price)
            queryset = queryset.filter(price__lte=price_limit)
        except ValueError:
            pass

    # 2. Search in Products table using Cosine Distance on text_embedding
    matches = queryset.annotate(
        distance=CosineDistance('text_embedding', query_embedding)
    )
    
    if negative_embedding:
        matches = matches.annotate(
            neg_dist=CosineDistance('text_embedding', negative_embedding)
        ).annotate(
            # Penalize: Distance + SimilarityToNegative
            final_dist=F('distance') + (1.0 - F('neg_dist')) * 0.6
        ).order_by('final_dist')[:top_k]
    else:
        matches = matches.order_by('distance')[:top_k]
    
    # 3. Serialize results
    results = []
    for product in matches:
        dist = getattr(product, 'final_dist', getattr(product, 'distance', 0))
        results.append({
            "product_id": product.product_id,
            "title": product.title,
            "image_url": product.image_url,
            "price": product.price,
            "semantic_score": max(0, 1 - dist),
            "brand": product.brand_name,
            "category": product.category
        })

    return Response({
        "matches": results,
        "total_results": len(results)
    })


@api_view(['POST'])
def shop_search(request):
    """
    Smart text-based product search endpoint.
    Uses text embeddings for semantic matching (spell-tolerant).
    
    Request body:
    - query: search text (e.g., "white sneakers", "whte snakers")
    - category: optional category filter
    - top_k: number of results (default 50)
    """
    query_text = request.data.get('query', '')
    category = request.data.get('category')
    top_k = int(request.data.get('top_k', 24))  # Reduced from 50 for faster loading
    
    if not query_text:
        return Response({'error': 'Query text is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    print(f"Shop Search: '{query_text}' | Category: {category}")
    
    # Generate text embedding for the search query
    query_embedding = ml_service.generate_text_embedding(query_text)
    
    if not query_embedding:
        return Response({'error': 'Failed to generate search embedding'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Build queryset
    queryset = Product.objects.all()
    
    if category:
        queryset = queryset.filter(category__icontains=category)
    
    # Search using text embedding similarity
    matches = queryset.annotate(
        distance=CosineDistance('text_embedding', query_embedding)
    ).order_by('distance')[:top_k]
    
    # Serialize results
    results = []
    for product in matches:
        results.append({
            'product_id': product.product_id,
            'title': product.title,
            'brand': product.brand_name,
            'price': float(product.price) if product.price else 0,
            'category': product.category,
            'image_url': product.image_url,
            'pdp_url': product.pdp_url,
            'similarity_score': 1 - float(product.distance) if hasattr(product, 'distance') else 0
        })
    
    return Response({
        'success': True,
        'query': query_text,
        'total': len(results),
        'products': results
    })


@api_view(['GET'])
def get_categories(request):
    """
    Get all available product categories with sample images.
    """
    try:
        # Use raw SQL for faster execution
        from django.db import connection
        
        with connection.cursor() as cursor:
            # Get one sample product per category with specific brand preferences
            cursor.execute("""
                WITH ranked_products AS (
                    SELECT 
                        category,
                        image_url,
                        title,
                        brand_name,
                        CASE 
                            WHEN category = 'bags' AND brand_name ILIKE '%henny%bear%' THEN 1
                            WHEN category = 'bottoms' AND brand_name ILIKE '%balenciaga%' THEN 1
                            ELSE 2
                        END as priority,
                        ROW_NUMBER() OVER (PARTITION BY category ORDER BY 
                            CASE 
                                WHEN category = 'bags' AND brand_name ILIKE '%henny%bear%' THEN 1
                                WHEN category = 'bottoms' AND brand_name ILIKE '%balenciaga%' THEN 1
                                ELSE 2
                            END,
                            product_id
                        ) as rn
                    FROM products
                    WHERE category IS NOT NULL 
                    AND image_url IS NOT NULL
                )
                SELECT category, image_url, title
                FROM ranked_products
                WHERE rn = 1
                ORDER BY category
            """)
            
            category_samples = cursor.fetchall()
            
        # Build response
        category_data = []
        for cat_name, image_url, title in category_samples:
            # Count products in this category
            count = Product.objects.filter(category=cat_name).count()
            
            category_data.append({
                'name': cat_name,
                'display_name': cat_name.title(),
                'count': count,
                'sample': {
                    'image_url': image_url,
                    'title': title
                }
            })
        
        return Response({
            'success': True,
            'categories': category_data
        })
    except Exception as e:
        print(f"Error in get_categories: {e}")
        return Response({
            'success': False,
            'error': str(e),
            'categories': []
        })
