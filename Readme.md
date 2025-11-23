# Vibe Search - Fashion Discovery Platform

A Pinterest-style fashion discovery app with AI-powered visual search, built with Next.js and Django.

## 🚀 Quick Start with Docker

**Run everything with one command:**

```bash
docker-compose up
```

That's it! The app will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Database**: PostgreSQL with pgvector on port 5432

## 📋 Prerequisites

- Docker & Docker Compose
- 4GB+ RAM recommended (for ML models)

## 🛠️ Manual Setup (Without Docker)

### Backend (Django + PostgreSQL)

1. Install PostgreSQL with pgvector extension
2. Create virtual environment:
```bash
cd vibe-search-backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure database in `vibesearch/settings.py`

5. Run migrations:
```bash
python manage.py migrate
```

6. Populate gallery:
```bash
python manage.py prepopulate_gallery
```

7. Start server:
```bash
python manage.py runserver
```

### Frontend (Next.js)

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Start development server:
```bash
npm run dev
```

3. Open http://localhost:3000

## ✨ Features

- **Visual Search**: Upload an image to find similar fashion items
- **Shop the Look**: AI-powered outfit detection with YOLO
- **Text Search**: Search by keywords with semantic matching
- **Advanced Filters**: Price range, categories, negative search
- **Pinterest-style UI**: Masonry gallery layout
- **Browser History**: Full back button support

## 🏗️ Tech Stack

### Frontend
- Next.js 16 with TypeScript
- Tailwind CSS
- Lucide Icons

### Backend
- Django REST Framework
- PostgreSQL with pgvector
- CLIP (OpenAI) for image embeddings
- YOLOv8 for object detection
- Sentence Transformers for text embeddings

### Search & Discovery
- ScrapingBee API for Pinterest scraping
- Vector similarity search (pgvector)
- Hybrid text + visual search

## 📁 Project Structure

```
pinterest/
├── docker-compose.yml          # One-command Docker setup
├── frontend/                   # Next.js app
│   ├── app/
│   │   ├── components/        # React components
│   │   ├── api/              # API routes
│   │   └── search/           # Search page
│   └── Dockerfile
└── vibe-search-backend/       # Django API
    ├── search/               # Main app
    │   ├── models.py        # Database models
    │   ├── views.py         # API endpoints
    │   └── ml_service.py    # ML models
    └── Dockerfile
```

## 🔑 Environment Variables

Create `.env` file in backend:
```
DATABASE_URL=postgresql://user:pass@localhost:5432/vibesearch
DEBUG=1
```

## 📝 API Endpoints

- `GET /api/gallery/` - Get gallery images
- `POST /api/search/image/` - Visual search
- `POST /api/search/text/` - Text search  
- `POST /api/search/shop-the-look/` - Outfit detection

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

MIT License - feel free to use this project for learning and building!

## 🙏 Credits

- CLIP by OpenAI
- YOLOv8 by Ultralytics
- Pinterest for inspiration