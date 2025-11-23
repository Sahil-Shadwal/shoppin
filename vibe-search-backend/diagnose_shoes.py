import requests
from PIL import Image, ImageDraw
import os
from ultralytics import YOLO
import numpy as np

# Test with the user's NEW uploaded image
test_path = "/Users/sahilshadwal/.gemini/antigravity/brain/5a06bb85-e49d-40ca-b289-a7eedc0320aa/uploaded_image_1763891824825.png"

def diagnose_shoes(image_path):
    print(f"Diagnosing footwear crop on {image_path}")
    
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
    if img.mode == 'RGBA':
        img = img.convert('RGB')
    img_width, img_height = img.size
    
    def get_box_from_indices(indices, padding, name):
        valid_kpts = [kpts[i] for i in indices if kpts[i][0] > 0 and kpts[i][1] > 0]
        if not valid_kpts:
            print(f"[{name}] No valid keypoints found")
            return None
        
        kx = [k[0] for k in valid_kpts]
        ky = [k[1] for k in valid_kpts]
        
        min_x, max_x = min(kx), max(kx)
        min_y, max_y = min(ky), max(ky)
        
        w = max_x - min_x
        h = max_y - min_y
        
        pad_x = w * padding
        pad_y = h * padding
        
        # Ensure minimum size (e.g., 50px) to avoid tiny boxes
        if w < 50: pad_x += (50 - w) / 2
        if h < 50: pad_y += (50 - h) / 2
        
        box = (
            max(0, int(min_x - pad_x)),
            max(0, int(min_y - pad_y)),
            min(img_width, int(max_x + pad_x)),
            min(img_height, int(max_y + pad_y))
        )
        print(f"[{name}] Box: {box}, Width: {box[2]-box[0]}, Height: {box[3]-box[1]}")
        return box

    # Strategy 1: Knees + Ankles (Current Bad Logic)
    box1 = get_box_from_indices([13, 14, 15, 16], 0.2, "Knees+Ankles")
    
    # Strategy 2: Ankles Only (Previous Logic)
    box2 = get_box_from_indices([15, 16], 0.4, "AnklesOnly")
    
    # Strategy 3: Ankles + Expanded Downwards
    # Logic: Take ankles, assume feet are below them. 
    # Expand Y2 significantly, Y1 slightly.
    valid_ankles = [kpts[i] for i in [15, 16] if kpts[i][0] > 0 and kpts[i][1] > 0]
    box3 = None
    if valid_ankles:
        kx = [k[0] for k in valid_ankles]
        ky = [k[1] for k in valid_ankles]
        min_x, max_x = min(kx), max(kx)
        min_y, max_y = min(ky), max(ky)
        
        # Heuristic: Foot height is roughly 1/6 of person height? Or just fixed pixels?
        # Let's try expanding relative to the ankle spread width?
        w = max_x - min_x
        if w < 20: w = 100 # Fallback if ankles are overlapping (side view)
        
        # Expand x by 50% width
        pad_x = w * 0.5
        
        # Expand y: 20% up, 100% down (to get the sole)
        # But "down" is limited by image height or person box
        h_est = w * 0.8 # Feet are roughly as high as they are wide apart?
        
        box3 = (
            max(0, int(min_x - pad_x)),
            max(0, int(min_y - h_est * 0.5)), # A bit up
            min(img_width, int(max_x + pad_x)),
            min(img_height, int(max_y + h_est * 1.2)) # More down
        )
        print(f"[Ankles+Heuristic] Box: {box3}")

    # Draw all
    draw = ImageDraw.Draw(img)
    if box1: draw.rectangle(box1, outline="red", width=3) # Current Bad
    if box2: draw.rectangle(box2, outline="blue", width=3) # Old Small
    if box3: draw.rectangle(box3, outline="green", width=5) # New Proposal
    
    # Draw keypoints
    for i, (kx, ky) in enumerate(kpts):
        if kx > 0 and ky > 0:
            color = "yellow"
            if i in [15, 16]: color = "cyan" # Ankles
            if i in [13, 14]: color = "orange" # Knees
            draw.ellipse([kx-3, ky-3, kx+3, ky+3], fill=color)
            
    img.save("diagnose_shoes.jpg")
    print("Saved diagnose_shoes.jpg")

diagnose_shoes(test_path)
