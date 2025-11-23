import requests
from PIL import Image, ImageDraw
import os
from ultralytics import YOLO

def download_image(url, path):
    resp = requests.get(url, stream=True)
    with open(path, 'wb') as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)

def test_crop(image_url, category):
    print(f"Testing crop for category: {category}")
    local_path = "test_image.jpg"
    download_image(image_url, local_path)
    
    model = YOLO('yolov8n.pt')
    results = model.predict(source=local_path, conf=0.25, verbose=False)
    detections = results[0].boxes
    
    # Find person
    person_box = None
    max_conf = 0
    for det in detections:
        class_id = int(det.cls)
        class_name = model.names[class_id]
        conf = float(det.conf)
        if class_name == 'person' and conf > max_conf:
            max_conf = conf
            person_box = det
            
    if person_box is None:
        print("No person detected")
        return

    x1, y1, x2, y2 = map(int, person_box.xyxy[0].tolist())
    print(f"Person box: {x1}, {y1}, {x2}, {y2}")
    
    img = Image.open(local_path)
    img_width, img_height = img.size
    p_width = x2 - x1
    p_height = y2 - y1
    
    crop_x1, crop_y1, crop_x2, crop_y2 = x1, y1, x2, y2
    
    if category == 'tops':
        crop_y2 = y1 + int(p_height * 0.6)
    elif category == 'bottoms':
        crop_y1 = y1 + int(p_height * 0.5)
    elif category == 'footwear':
        crop_y1 = y1 + int(p_height * 0.8)
    elif category == 'outerwear':
        crop_y2 = y1 + int(p_height * 0.7)
        
    # Bounds check
    crop_x1 = max(0, int(crop_x1))
    crop_y1 = max(0, int(crop_y1))
    crop_x2 = min(img_width, int(crop_x2))
    crop_y2 = min(img_height, int(crop_y2))
    
    print(f"Crop box: {crop_x1}, {crop_y1}, {crop_x2}, {crop_y2}")
    
    # Draw box
    draw = ImageDraw.Draw(img)
    draw.rectangle([crop_x1, crop_y1, crop_x2, crop_y2], outline="red", width=3)
    
    output_path = f"test_crop_{category}.jpg"
    img.save(output_path)
    print(f"Saved visualization to {output_path}")

# Test with a sample image
test_url = "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?q=80&w=1000&auto=format&fit=crop" # Woman in full outfit
test_crop(test_url, 'footwear')
