FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    gcc \
    g++ \
    libjpeg-dev \
    zlib1g-dev \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Pre-download ML models to cache them in the image
RUN python -c "from transformers import CLIPProcessor, CLIPModel; \
    CLIPModel.from_pretrained('openai/clip-vit-base-patch32'); \
    CLIPProcessor.from_pretrained('openai/clip-vit-base-patch32')" && \
    python -c "from sentence_transformers import SentenceTransformer; \
    SentenceTransformer('all-MiniLM-L6-v2')" && \
    python -c "from ultralytics import YOLO; \
    YOLO('yolov8n.pt')"

# Copy project files
COPY . .

# Expose port
EXPOSE 8000

# Create entrypoint script
RUN echo '#!/bin/sh\n\
echo "Running migrations..."\n\
python manage.py migrate --noinput\n\
echo "Starting Django development server..."\n\
python manage.py runserver 0.0.0.0:8000\n\
' > /entrypoint.sh && chmod +x /entrypoint.sh

# Run entrypoint
CMD ["/entrypoint.sh"]
