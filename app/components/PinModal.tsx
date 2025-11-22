'use client';

import React, { useState } from 'react';
import { X, Search, ShoppingBag } from 'lucide-react';

interface Pin {
  id: string;
  imageUrl: string;
  thumbnailUrl: string;
  title: string;
  sourceUrl: string;
  query: string;
}

interface Product {
  product_id: string;
  title: string;
  image_url: string;
  price: number;
  brand: string;
  visual_score: number;
}

interface PinModalProps {
  pin: Pin | null;
  onClose: () => void;
}

export default function PinModal({ pin, onClose }: PinModalProps) {
  const [similarProducts, setSimilarProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

  if (!pin) return null;

  const handleSearchSimilar = async () => {
    setLoading(true);
    setHasSearched(true);
    try {
      const response = await fetch('http://127.0.0.1:8000/api/search/image/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          external_image_url: pin.imageUrl,
          query_text: pin.title, // Send caption for hybrid search
          top_k: 6
        }),
      });
      
      const data = await response.json();
      if (data.matches) {
        setSimilarProducts(data.matches);
      }
    } catch (error) {
      console.error('Error searching similar products:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div 
      className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4"
      onClick={onClose}
    >
      <div 
        className="relative bg-white rounded-3xl max-w-6xl w-full max-h-[90vh] overflow-hidden shadow-2xl flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 z-10 bg-white/90 hover:bg-white rounded-full p-2 transition-colors"
        >
          <X className="w-6 h-6" />
        </button>

        <div className="flex flex-col md:flex-row flex-1 overflow-hidden">
          {/* Image section */}
          <div className="md:w-1/2 bg-gray-50 flex items-center justify-center p-8 overflow-y-auto">
            <img
              src={pin.imageUrl.replace('474x', '736x')}
              alt={pin.title}
              className="max-w-full h-auto object-contain rounded-xl"
            />
          </div>

          {/* Details & Search section */}
          <div className="md:w-1/2 p-8 overflow-y-auto bg-white">
            <div className="mb-8">
              <h3 className="text-xs font-semibold text-gray-500 uppercase mb-2">
                Inspiration
              </h3>
              <p className="text-xl font-medium leading-relaxed mb-4">
                {pin.title}
              </p>
              
              <div className="flex gap-3">
                <button className="flex-1 bg-red-600 text-white py-3 rounded-full font-semibold hover:bg-red-700 transition-colors">
                  Save Pin
                </button>
                <a
                  href={pin.sourceUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex-1 text-center border-2 border-gray-200 py-3 rounded-full font-semibold hover:bg-gray-50 transition-colors"
                >
                  Visit Source
                </a>
              </div>
            </div>

            <div className="border-t border-gray-100 pt-8">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-bold flex items-center gap-2">
                  <ShoppingBag className="w-5 h-5" />
                  Shop the Vibe
                </h3>
                <button 
                  onClick={handleSearchSimilar}
                  disabled={loading}
                  className="flex items-center gap-2 bg-black text-white px-4 py-2 rounded-full text-sm font-medium hover:bg-gray-800 disabled:opacity-50 transition-all"
                >
                  <Search className="w-4 h-4" />
                  {loading ? 'Analyzing Vibe...' : 'Find Similar Items'}
                </button>
              </div>

              {loading ? (
                <div className="flex justify-center py-12">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-black"></div>
                </div>
              ) : hasSearched && similarProducts.length === 0 ? (
                <div className="text-center py-12 text-gray-500 bg-gray-50 rounded-xl">
                  <p>No matching products found for this vibe.</p>
                </div>
              ) : (
                <div className="grid grid-cols-2 gap-4">
                  {similarProducts.map((product) => (
                    <div key={product.product_id} className="group cursor-pointer">
                      <div className="relative aspect-square overflow-hidden rounded-xl bg-gray-100 mb-2">
                        <img 
                          src={product.image_url} 
                          alt={product.title}
                          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                        />
                        <div className="absolute bottom-2 right-2 bg-white/90 px-2 py-1 rounded text-xs font-bold">
                          {Math.round(product.visual_score * 100)}% Match
                        </div>
                      </div>
                      <h4 className="font-medium text-sm line-clamp-1">{product.brand}</h4>
                      <p className="text-xs text-gray-500 line-clamp-1">{product.title}</p>
                      <p className="font-semibold mt-1">${product.price}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
