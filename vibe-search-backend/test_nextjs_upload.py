import requests
from PIL import Image
import io

# Create a test image
img = Image.new('RGB', (200, 200), color='blue')
img_bytes = io.BytesIO()
img.save(img_bytes, format='JPEG')
img_bytes.seek(0)

# Test via Next.js API (which should proxy to Django)
url = 'http://localhost:3000/api/search-image'
files = {'image': ('test.jpg', img_bytes, 'image/jpeg')}

print(f"Testing image upload via Next.js API: {url}")
print("=" * 60)

try:
    response = requests.post(url, files=files)
    
    print(f"✅ Status Code: {response.status_code}")
    print(f"✅ Response Headers: {dict(response.headers)}")
    
    try:
        data = response.json()
        print(f"✅ Response JSON:")
        print(f"   - success: {data.get('success')}")
        print(f"   - pins count: {len(data.get('pins', []))}")
        if data.get('pins'):
            print(f"   - First pin: {data['pins'][0].get('title')}")
    except:
        print(f"❌ Response Text: {response.text[:200]}")
        
except Exception as e:
    print(f"❌ Request failed: {e}")
