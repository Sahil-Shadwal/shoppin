import requests
import os

# Create a dummy image
from PIL import Image
img = Image.new('RGB', (100, 100), color = 'red')
img.save('test_image.jpg')

url = 'http://127.0.0.1:8000/api/search/image/'
files = {'image': open('test_image.jpg', 'rb')}
data = {'top_k': 5}

try:
    print(f"Sending POST request to {url}...")
    response = requests.post(url, files=files, data=data)
    
    print(f"Status Code: {response.status_code}")
    try:
        print("Response JSON:", response.json())
    except:
        print("Response Text:", response.text)
        
except Exception as e:
    print(f"Request failed: {e}")
finally:
    if os.path.exists('test_image.jpg'):
        os.remove('test_image.jpg')
