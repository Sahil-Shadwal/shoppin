# Vibe Search Backend

Django backend for Vibe Search MVP, featuring CLIP-based visual search and Sentence-Transformer semantic search.

## Prerequisites

- Python 3.10+
- PostgreSQL 15+
- `pgvector` extension for PostgreSQL

## Setup

1.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Environment Variables:**
    Create a `.env` file in this directory:
    ```env
    DB_NAME=vibe_search
    DB_USER=postgres
    DB_PASSWORD=postgres
    DB_HOST=localhost
    DB_PORT=5432
    ALLOWED_HOSTS=localhost,127.0.0.1
    ```

4.  **Database Setup:**
    Make sure your PostgreSQL server is running and you have created the database:
    ```sql
    CREATE DATABASE vibe_search;
    \c vibe_search
    CREATE EXTENSION vector;
    ```

5.  **Run Migrations:**
    ```bash
    python manage.py makemigrations search
    python manage.py migrate
    ```

6.  **Run Server:**
    ```bash
    python manage.py runserver
    ```

## API Endpoints

- `POST /api/scraped-images/`: Store scraped images (called by frontend scraper).
- `GET /api/gallery/`: Get images for gallery.
- `POST /api/search/image/`: Visual search (find products similar to an image).
- `POST /api/search/text/`: Text search (find products by text query).

## Notes

- The first time you run the server or perform a search, it will download the CLIP and Sentence-Transformer models (approx. 1GB).
- Ensure your frontend is running on `http://localhost:3000` for CORS to work.
