from django.urls import path
from . import views

urlpatterns = [
    # Scraped images
    path('scraped-images/', views.store_scraped_images, name='store_scraped_images'),
    path('gallery/', views.get_gallery, name='get_gallery'),
    
    # Products
    path('products/', views.get_products, name='get_products'),
    
    # Search endpoints (placeholders for now)
    path('search/image/', views.search_by_image, name='search_by_image'),
    path('shop/search/', views.shop_search, name='shop_search'),
    path('shop/categories/', views.get_categories, name='get_categories'),
    path('search/text/', views.search_by_text, name='search_by_text'),
    path('search/shop-the-look/', views.shop_the_look, name='shop_the_look'),
]
