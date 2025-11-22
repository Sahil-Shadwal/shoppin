import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
from sentence_transformers import SentenceTransformer
import requests
from io import BytesIO

class MLService:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MLService, cls).__new__(cls)
            cls._instance.initialize_models()
        return cls._instance
    
    def initialize_models(self):
        print("Loading CLIP model...")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(self.device)
        self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        
        print("Loading Sentence-Transformer model...")
        self.text_model = SentenceTransformer('all-MiniLM-L6-v2', device=self.device)
        print("Models loaded successfully.")

    def generate_image_embedding(self, image_url):
        try:
            response = requests.get(image_url, stream=True)
            response.raise_for_status()
            image = Image.open(response.raw)
            
            inputs = self.clip_processor(images=image, return_tensors="pt").to(self.device)
            with torch.no_grad():
                image_features = self.clip_model.get_image_features(**inputs)
            
            # Normalize
            image_features = image_features / image_features.norm(p=2, dim=-1, keepdim=True)
            return image_features.cpu().numpy()[0].tolist()
        except Exception as e:
            print(f"Error generating image embedding: {e}")
            return None

    def generate_text_embedding(self, text):
        try:
            embedding = self.text_model.encode(text)
            return embedding.tolist()
        except Exception as e:
            print(f"Error generating text embedding: {e}")
            return None

# Global instance
ml_service = MLService()
