🚀 Commands to Run the Backend
1. Navigate to Backend Directory

cd /Users/sahilshadwal/Desktop/pinterest/vibe-search-backend
2. Activate Virtual Environment

source venv/bin/activate
3. Install/Update Dependencies (if needed)

pip install -r requirements.txt
4. Run Database Migrations

python manage.py migrate
5. Import Products (load products from CSV into database)

python manage.py import_products
6. Start the Django Server 🎯

python manage.py runserver
The server will start at http://localhost:8000

📋 Quick Start Script (All-in-One)
Here's a single command that does everything:


cd /Users/sahilshadwal/Desktop/pinterest/vibe-search-backend && \
source venv/bin/activate && \
python manage.py migrate && \
python manage.py runserver
🔧 Useful Management Commands
Check if products are imported:

python manage.py shell -c "from search.models import Product; print(f'Products: {Product.objects.count()}')"
Re-import products (if needed):

python manage.py import_products
Create superuser (for Django admin):

python manage.py createsuperuser
🌐 API Endpoints (once running)
Gallery: http://localhost:8000/api/gallery/
Shop the Look: http://localhost:8000/api/search/shop-the-look/
Image Search: http://localhost:8000/api/search/image/
Text Search: http://localhost:8000/api/search/text/
Products: http://localhost:8000/api/products/


```
source venv/bin/activate && \
python manage.py migrate && \
python manage.py runserver

```