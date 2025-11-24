# Shoppin 🍓

**Shoppin** is an AI-powered fashion discovery platform that transforms visual inspiration into shoppable products. It combines the browsing experience of Pinterest with intelligent, computer-vision-powered product matching.

![Shoppin Homepage Placeholder](<!-- Add Homepage Screenshot Here -->)

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

---

## 🏗️ Architecture

Shoppin uses a modern split-stack architecture designed for performance and scalability.

![Architecture Diagram Placeholder](<!-- Add Architecture Diagram Here -->)

### **Frontend (Next.js + TypeScript)**
- **Framework**: Next.js 14 (App Router)
- **Styling**: Tailwind CSS
- **Performance**: Dual-layer caching (LocalStorage + In-memory) for instant navigation.

### **Backend (Django + Python)**
- **API**: Django REST Framework
- **AI/ML**: PyTorch, Ultralytics (YOLO), Sentence-Transformers
- **Database**: PostgreSQL with **pgvector** extension for vector similarity search.

---

## ✨ Key Features & How They Work

### 1. Shop the Look (YOLOv8 + Intelligent Cropping)

Click on any outfit, and Shoppin identifies the individual items (shoes, tops, pants) and finds matches.

![Shop the Look Demo Placeholder](<!-- Add Shop the Look Screenshot Here -->)

**How it works:**
1. **Detection**: We use **YOLOv8-Pose** to detect the person and 17 body keypoints (shoulders, knees, ankles, etc.).
2. **Precision Cropping**: Instead of generic bounding boxes, we use keypoints to crop exact regions (e.g., "Ankle to Floor" for shoes).
3. **Matching**: The cropped region is converted to a vector embedding and matched against our product catalog.

### 2. Visual Search (CLIP Embeddings)

Upload any image to find visually similar products. You can refine results with text ("no leather") or price filters.

![Visual Search Demo Placeholder](<!-- Add Visual Search Screenshot Here -->)

**The Tech Stack:**
- **CLIP Model**: Converts images into 512-dimensional vector embeddings.
- **pgvector**: Performs cosine similarity search in PostgreSQL to find the closest visual matches in milliseconds.
- **Hybrid Search**: Combines visual embeddings with text embeddings for refined queries.

### 3. Smart Caching ("More Ideas")

We scrape fresh inspiration from Pinterest while keeping costs low and performance high.

![Gallery/Caching Demo Placeholder](<!-- Add Gallery Screenshot Here -->)

**Optimization Strategy:**
- **Layer 1**: Client-side cache (Instant load for visited categories).
- **Layer 2**: Database cache (Fast retrieval of previously scraped items).
- **Layer 3**: Fresh Scraping (Only triggers when you click "Shuffle/More Ideas").
- **Result**: 90% reduction in scraping costs + instant UI interactions.

### 4. Semantic Shop Search (Spell Tolerant)

Search for products using natural language, even with typos or slang.

![Shop Search Demo Placeholder](<!-- Add Shop Search Screenshot Here -->)

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

## 📸 Screen Recordings / Demos

<!-- Add links to video demos or GIFs here -->

---

## 📝 License

[MIT](LICENSE)