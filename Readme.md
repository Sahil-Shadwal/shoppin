# Shoppin 🍓

**Shoppin** is an AI-powered fashion discovery platform that transforms visual inspiration into shoppable products. It combines the browsing experience of Pinterest with intelligent, computer-vision-powered product matching.

<img width="1469" height="801" alt="Screenshot 2025-11-24 at 4 06 17 PM" src="https://github.com/user-attachments/assets/e4c75255-3884-4925-967b-31aa2cc2128d" />

---

## 🚀 Quick Start

Run the entire stack (Frontend, Backend, Database) with a single command:

```bash
docker compose up --build
```

The application will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000

---

## 💡 What Problem Does It Solve?

Have you ever seen an amazing outfit online and wondered, *"Where can I buy that?"*

Traditional search engines fail here because fashion is visual. Describing a specific "vintage oversized beige trench coat" with keywords is difficult and often inaccurate.

**Shoppin solves this using AI.** We use computer vision to "see" the outfit, understand the style, and instantly find similar products you can actually buy.



## ✨ Key Features & How They Work

### 1. Shop the Look (YOLOv8 + Intelligent Cropping)

Click on any outfit, and Shoppin identifies the individual items (shoes, tops, pants) and finds matches.
<img width="1463" height="786" alt="Screenshot 2025-11-24 at 4 09 39 PM" src="https://github.com/user-attachments/assets/b735f044-74e2-479c-8cee-81a60d450d99" />



**How it works:**
1. **Detection**: We use **YOLOv8-Pose** to detect the person and 17 body keypoints (shoulders, knees, ankles, etc.).
2. **Precision Cropping**: Instead of generic bounding boxes, we use keypoints to crop exact regions (e.g., "Ankle to Floor" for shoes).
3. **Matching**: The cropped region is converted to a vector embedding and matched against our product catalog.

### 2. Visual Search (CLIP Embeddings)

Upload any image to find visually similar products. You can refine results with text ("no leather") or price filters.

<img width="1469" height="802" alt="Screenshot 2025-11-24 at 4 10 36 PM" src="https://github.com/user-attachments/assets/3ff551f5-27e6-4d04-9ede-41aed4618dbb" />


**The Tech Stack:**
- **CLIP Model**: Converts images into 512-dimensional vector embeddings.
- **pgvector**: Performs cosine similarity search in PostgreSQL to find the closest visual matches in milliseconds.
- **Hybrid Search**: Combines visual embeddings with text embeddings for refined queries.


### 3. Semantic Shop Search (Spell Tolerant)

Search for products using natural language, even with typos or slang.

<img width="1468" height="795" alt="Screenshot 2025-11-24 at 4 11 40 PM" src="https://github.com/user-attachments/assets/98d096cb-2623-4326-b272-893892bac8f6" />


**Example:**
- Query: *"micheal baskelball shoes"* (Typos included)
- Result: **Michael Jordan Basketball Shoes**

**Why?** We use **Sentence Transformers** to match the *meaning* (semantics) of your query rather than exact keywords. The vector for "micheal" is nearly identical to "michael," so the search just works.

---

## 🛠️ Technology Stack

- **Frontend**: Next.js, React, TailwindCSS, Lucide Icons
- **Backend**: Django, DRF, Gunicorn
- **Database**: PostgreSQL, pgvector
- **AI Models**:
  - `yolov8n-pose.pt` (Person & Keypoint Detection)
  - `CLIP` (Visual Embeddings)
  - `all-MiniLM-L6-v2` (Text Embeddings)
- **Infrastructure**: Docker, Docker Compose

---

## 📝 License

[MIT](LICENSE)
