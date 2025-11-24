'use client';

import React, { useState, useEffect } from 'react';
import { ArrowLeft, Search, ShoppingBag } from 'lucide-react';
import { useRouter } from 'next/navigation';
import ProductCard from '../components/ProductCard';

interface Product {
  product_id: string;
  title: string;
  brand: string;
  price: number;
  category: string;
  image_url: string;
  pdp_url: string;
  similarity_score?: number;
}

interface Category {
  name: string;
  display_name: string;
  count: number;
  sample: { image_url: string; title: string };
}

export default function ShopPage() {
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState('');
  const [categories, setCategories] = useState<Category[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [hasSearched, setHasSearched] = useState(false);

  // Fetch categories on load with caching
  useEffect(() => {
    const fetchCategories = async () => {
      // Try to load from cache first for instant display
      const cached = localStorage.getItem('shop_categories');
      if (cached) {
        try {
          const cachedData = JSON.parse(cached);
          setCategories(cachedData);
          console.log('✅ Loaded categories from cache - instant!');
        } catch (e) {
          console.error('Failed to parse cached categories');
        }
      }

      // Fetch fresh data in background
      try {
        const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';
        const response = await fetch(`${backendUrl}/api/shop/categories/`);
        const data = await response.json();
        if (data.success) {
          setCategories(data.categories);
          // Update cache
          localStorage.setItem('shop_categories', JSON.stringify(data.categories));
          console.log('📦 Updated categories cache');
        }
      } catch (error) {
        console.error('Failed to fetch categories:', error);
        // If fetch fails but we have cache, that's okay - already displayed
      }
    };

    fetchCategories();
  }, []);

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;

    setLoading(true);
    setHasSearched(true);

    try {
      const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';
      const response = await fetch(`${backendUrl}/api/shop/search/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: searchQuery,
          category: selectedCategory,
          top_k: 24  // Reduced for faster loading
        })
      });

      const data = await response.json();
      if (data.success) {
        setProducts(data.products);
      }
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCategoryClick = async (categoryName: string) => {
    setSelectedCategory(categoryName);
    setSearchQuery(categoryName);
    setLoading(true);
    setHasSearched(true);

    try {
      const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';
      const response = await fetch(`${backendUrl}/api/shop/search/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: categoryName,
          category: categoryName,
          top_k: 24  // Reduced for faster loading
        })
      });

      const data = await response.json();
      if (data.success) {
        setProducts(data.products);
      }
    } catch (error) {
      console.error('Category search failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between mb-4">
            <button
              onClick={() => router.push('/')}
              className="flex items-center gap-2 text-gray-700 hover:text-black transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
              <span className="font-semibold">Back to Gallery</span>
            </button>
            <h1 className="text-xl font-bold text-gray-900 flex items-center gap-2">
              <ShoppingBag className="w-6 h-6" />
              Shop
            </h1>
          </div>

          {/* Search Bar */}
          <div className="relative">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="Search for products... (e.g., white shoes, blck jcket)"
              className="w-full px-6 py-4 pr-14 text-lg border-2 border-gray-300 rounded-2xl focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent"
            />
            <button
              onClick={handleSearch}
              disabled={loading}
              className="absolute right-2 top-1/2 -translate-y-1/2 bg-black text-white p-3 rounded-xl hover:bg-gray-800 disabled:opacity-50 transition-all"
            >
              <Search className="w-5 h-5" />
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {!hasSearched ? (
          // Category Grid (Bento Layout)
          <>
            <h2 className="text-2xl font-bold mb-6">Browse by Category</h2>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-6">
              {categories.map((category) => (
                <button
                  key={category.name}
                  onClick={() => handleCategoryClick(category.name)}
                  className="group relative aspect-[3/4] rounded-2xl overflow-hidden bg-white shadow-md hover:shadow-2xl transition-all border-2 border-transparent hover:border-black"
                >
                  {/* Single large category image */}
                  {category.sample && (
                    <img
                      src={category.sample.image_url}
                      alt={category.sample.title}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                    />
                  )}

                  {/* Category label */}
                  <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black via-black/80 to-transparent p-4">
                    <h3 className="text-white font-bold text-lg">{category.display_name}</h3>
                    <p className="text-white/90 text-sm">{category.count} items</p>
                  </div>
                </button>
              ))}
            </div>
          </>
        ) : loading ? (
          // Loading state
          <div className="flex flex-col items-center justify-center py-20">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-black mb-4"></div>
            <p className="text-gray-600">Searching products...</p>
          </div>
        ) : products.length > 0 ? (
          // Products Grid
          <>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold">
                {selectedCategory ? `${selectedCategory.charAt(0).toUpperCase() + selectedCategory.slice(1)}` : 'Search Results'}
              </h2>
              <button
                onClick={() => {
                  setHasSearched(false);
                  setProducts([]);
                  setSearchQuery('');
                  setSelectedCategory(null);
                }}
                className="text-sm text-gray-600 hover:text-black"
              >
                ← Browse categories
              </button>
            </div>
            <p className="text-sm text-gray-600 mb-6">
              Found <span className="font-semibold text-gray-900">{products.length}</span> products
            </p>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {products.map((product) => (
                <ProductCard
                  key={product.product_id}
                  id={product.product_id}
                  imageUrl={product.image_url}
                  title={product.title}
                  brand={product.brand || 'Unknown Brand'}
                  price={product.price}
                  score={product.similarity_score || 0}
                  productUrl={product.pdp_url}
                />
              ))}
            </div>
          </>
        ) : (
          // No results
          <div className="text-center py-20 bg-white rounded-xl border-2 border-dashed border-gray-300">
            <p className="text-gray-500 text-lg">No products found</p>
            <p className="text-gray-400 text-sm mt-2">Try a different search term</p>
            <button
              onClick={() => {
                setHasSearched(false);
                setProducts([]);
                setSearchQuery('');
                setSelectedCategory(null);
              }}
              className="mt-4 text-sm text-black hover:underline"
            >
              Browse categories
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
