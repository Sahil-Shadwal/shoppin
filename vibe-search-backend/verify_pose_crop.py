import requests
from PIL import Image, ImageDraw
import os
from ultralytics import YOLO
import numpy as np

def download_image(url, path):
    resp = requests.get(url, stream=True)
    with open(path, 'wb') as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)

def test_pose_crop(image_url, category):
    print(f"Testing POSE crop for category: {category}")
    local_path = "test_pose.jpg"
    download_image(image_url, local_path)
    
    # Load Pose Model
    model = YOLO('yolov8n-pose.pt')
    results = model.predict(source=local_path, conf=0.25, verbose=False)[0]
    detections = results.boxes
    keypoints = results.keypoints
    
    # Find person
    person_idx = -1
    max_conf = 0
    for i, det in enumerate(detections):
        class_id = int(det.cls)
        class_name = model.names[class_id]
        conf = float(det.conf)
        if class_name == 'person' and conf > max_conf:
            max_conf = conf
            person_idx = i
            
    if person_idx == -1:
        print("No person detected")
        return

    person_box = detections[person_idx]
    kpts = keypoints[person_idx].xy[0].cpu().numpy()
    
    x1, y1, x2, y2 = map(int, person_box.xyxy[0].tolist())
    print(f"Person box: {x1}, {y1}, {x2}, {y2}")
    
    img = Image.open(local_path)
    img_width, img_height = img.size
    
    crop_x1, crop_y1, crop_x2, crop_y2 = x1, y1, x2, y2
    
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

    if category == 'tops':
        box = get_kpt_box([5, 6, 11, 12], padding=0.2)
        if box:
            crop_x1, crop_y1, crop_x2, crop_y2 = box
            print("Applied 'tops' crop (Shoulders to Hips)")
            
    elif category == 'bottoms':
        box = get_kpt_box([11, 12, 15, 16], padding=0.1)
        if box:
            crop_x1, crop_y1, crop_x2, crop_y2 = box
            print("Applied 'bottoms' crop (Hips to Ankles)")
            
    elif category == 'footwear':
        box = get_kpt_box([15, 16], padding=0.4)
        if box:
            crop_x1, crop_y1, crop_x2, crop_y2 = box
            print("Applied 'footwear' crop (Ankles)")
            
    elif category == 'outerwear':
        box = get_kpt_box([5, 6, 13, 14], padding=0.15)
        if box:
            crop_x1, crop_y1, crop_x2, crop_y2 = box
            print("Applied 'outerwear' crop (Shoulders to Knees)")
            
    print(f"Final Crop box: {crop_x1}, {crop_y1}, {crop_x2}, {crop_y2}")
    
    # Draw box
    draw = ImageDraw.Draw(img)
    draw.rectangle([crop_x1, crop_y1, crop_x2, crop_y2], outline="blue", width=3)
    
    # Draw keypoints for debug
    for i, (kx, ky) in enumerate(kpts):
        if kx > 0 and ky > 0:
            draw.ellipse([kx-3, ky-3, kx+3, ky+3], fill="yellow")
    
    output_path = f"verify_pose_{category}.jpg"
    img.save(output_path)
    print(f"Saved visualization to {output_path}")

# Test with the user's uploaded image
test_path = "/Users/sahilshadwal/.gemini/antigravity/brain/5a06bb85-e49d-40ca-b289-a7eedc0320aa/uploaded_image_1763891824825.png"

def test_pose_crop_local(image_path, category):
    print(f"Testing POSE crop for category: {category} on {image_path}")
    
    # Load Pose Model
    model = YOLO('yolov8n-pose.pt')
    results = model.predict(source=image_path, conf=0.25, verbose=False)[0]
    detections = results.boxes
    keypoints = results.keypoints
    
    # Find person
    person_idx = -1
    max_conf = 0
    for i, det in enumerate(detections):
        class_id = int(det.cls)
        class_name = model.names[class_id]
        conf = float(det.conf)
        if class_name == 'person' and conf > max_conf:
            max_conf = conf
            person_idx = i
            
    if person_idx == -1:
        print("No person detected")
        return

    person_box = detections[person_idx]
    kpts = keypoints[person_idx].xy[0].cpu().numpy()
    
    x1, y1, x2, y2 = map(int, person_box.xyxy[0].tolist())
    print(f"Person box: {x1}, {y1}, {x2}, {y2}")
    
    img = Image.open(image_path)
    img_width, img_height = img.size
    
    crop_x1, crop_y1, crop_x2, crop_y2 = x1, y1, x2, y2
    
    def get_kpt_box(indices, padding=0.1):
        valid_kpts = [kpts[i] for i in indices if kpts[i][0] > 0 and kpts[i][1] > 0]
        if not valid_kpts:
            print(f"No valid keypoints found for indices {indices}")
            return None
        
        kx = [k[0] for k in valid_kpts]
        ky = [k[1] for k in valid_kpts]
        
        print(f"Keypoints found: {list(zip(kx, ky))}")
        
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

    if category == 'tops':
        box = get_kpt_box([5, 6, 11, 12], padding=0.2)
        if box:
            crop_x1, crop_y1, crop_x2, crop_y2 = box
            print("Applied 'tops' crop (Shoulders to Hips)")
            
    elif category == 'bottoms':
        box = get_kpt_box([11, 12, 15, 16], padding=0.1)
        if box:
            crop_x1, crop_y1, crop_x2, crop_y2 = box
            print("Applied 'bottoms' crop (Hips to Ankles)")
            
    elif category == 'footwear':
        # Ankles only, sized relative to person width
        valid_ankles = [kpts[i] for i in [15, 16] if kpts[i][0] > 0 and kpts[i][1] > 0]
        box = None
        
        if valid_ankles:
            kx = [k[0] for k in valid_ankles]
            ky = [k[1] for k in valid_ankles]
            
            # Center of ankles
            cx = sum(kx) / len(kx)
            cy = sum(ky) / len(ky)
            
            # Person width context
            p_w = x2 - x1
            
            # Target crop size
            target_w = max(max(kx) - min(kx), p_w * 0.5)
            target_h = max(max(ky) - min(ky), p_w * 0.4)
            
            # Define box centered on ankles, but shifted down slightly
            half_w = target_w / 2
            
            # Top: 30% of height above center, Bottom: 90% below
            
            box = (
                max(0, int(cx - half_w)),
                max(0, int(cy - target_h * 0.3)), # 30% up
                min(img_width, int(cx + half_w)),
                min(img_height, int(cy + target_h * 0.9)) # 90% down
            )
            print("Applied 'footwear' crop (Ankles relative to person size)")
        
        if box:
            crop_x1, crop_y1, crop_x2, crop_y2 = box
        else:
            # Fallback to knees if ankles missing
            box = get_kpt_box([13, 14], padding=0.4)
            if box:
                crop_x1, crop_y1, crop_x2, crop_y2 = box
                print("Fallback: 'footwear' crop (Knees)")
            else:
                # Fallback
                # p_height = y2 - y1 (not available here easily without person box context, skipping fallback logic for viz)
                print("Fallback: 'footwear' crop (Bottom 15%)")
            
    elif category == 'outerwear':
        box = get_kpt_box([5, 6, 13, 14], padding=0.15)
        if box:
            crop_x1, crop_y1, crop_x2, crop_y2 = box
            print("Applied 'outerwear' crop (Shoulders to Knees)")
            
    print(f"Final Crop box: {crop_x1}, {crop_y1}, {crop_x2}, {crop_y2}")
    
    # Draw box
    draw = ImageDraw.Draw(img)
    draw.rectangle([crop_x1, crop_y1, crop_x2, crop_y2], outline="blue", width=3)
    
    # Draw keypoints for debug
    for i, (kx, ky) in enumerate(kpts):
        if kx > 0 and ky > 0:
            color = "yellow"
            if i in [15, 16]: color = "red" # Ankles
            if i in [13, 14]: color = "green" # Knees
            draw.ellipse([kx-3, ky-3, kx+3, ky+3], fill=color)
    
    output_path = f"verify_pose_local_{category}.jpg"
    if img.mode == 'RGBA':
        img = img.convert('RGB')
    img.save(output_path)
    print(f"Saved visualization to {output_path}")

test_pose_crop_local(test_path, 'footwear')
