'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { ArrowLeft } from 'lucide-react';
import SearchControls from '../components/SearchControls';
import MasonryGallery from '../components/MasonryGallery';
import PinModal from '../components/PinModal';

interface Pin {
  id: string;
  imageUrl: string;
  thumbnailUrl: string;
  title: string;
  sourceUrl: string;
  query: string;
  price?: number;
  brand?: string;
  score?: number;
}

export default function SearchPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  
  const [uploadedImage, setUploadedImage] = useState<string | null>(null);
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [pins, setPins] = useState<Pin[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedPin, setSelectedPin] = useState<Pin | null>(null);
  
  // Search parameters
  const [maxPrice, setMaxPrice] = useState<number>(500);
  const [negativeQuery, setNegativeQuery] = useState<string>('');
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);

  // Load image from sessionStorage on mount
  useEffect(() => {
    const storedImageUrl = sessionStorage.getItem('searchImageUrl');
    const storedImageData = sessionStorage.getItem('searchImageFile');
    
    if (storedImageUrl) {
      setUploadedImage(storedImageUrl);
    }
    
    if (storedImageData) {
      // Reconstruct File from stored data
      const blob = dataURLtoBlob(storedImageData);
      const file = new File([blob], 'uploaded-image.jpg', { type: 'image/jpeg' });
      setImageFile(file);
      
      // Trigger initial search
      performSearch(file, maxPrice, negativeQuery, selectedCategory);
    }
  }, []);

  const dataURLtoBlob = (dataurl: string) => {
    const arr = dataurl.split(',');
    const mime = arr[0].match(/:(.*?);/)?.[1] || 'image/jpeg';
    const bstr = atob(arr[1]);
    let n = bstr.length;
    const u8arr = new Uint8Array(n);
    while (n--) {
      u8arr[n] = bstr.charCodeAt(n);
    }
    return new Blob([u8arr], { type: mime });
  };

  const performSearch = async (
    file: File | null,
    price: number,
    negative: string,
    category: string | null
  ) => {
    if (!file) return;
    
    setLoading(true);
    console.log(`🔍 Searching with: maxPrice=${price}, negative="${negative}", category=${category}`);
    
    try {
      const formData = new FormData();
      formData.append('image', file);
      formData.append('top_k', '30');
      
      if (price < 500) {
        formData.append('max_price', price.toString());
      }
      
      if (negative.trim()) {
        formData.append('negative_query', negative.trim());
      }
      
      if (category) {
        formData.append('category', category);
      }

      const response = await fetch('/api/search-image', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const data = await response.json();

      if (data.success && data.pins) {
        setPins(data.pins);
        console.log(`✅ Found ${data.pins.length} matches`);
      } else {
        setPins([]);
        console.error('❌ Search failed:', data.error);
      }
    } catch (error) {
      console.error('💥 Error searching:', error);
      setPins([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSearchUpdate = useCallback(() => {
    performSearch(imageFile, maxPrice, negativeQuery, selectedCategory);
  }, [imageFile, maxPrice, negativeQuery, selectedCategory]);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <button
            onClick={() => router.push('/')}
            className="flex items-center gap-2 text-gray-700 hover:text-black transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
            <span className="font-semibold">Back to Gallery</span>
          </button>
          <h1 className="text-xl font-bold text-gray-900">Visual Search</h1>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="flex gap-6">
          {/* Left Panel - Sticky */}
          <div className="w-80 flex-shrink-0">
            <div className="sticky top-24">
              <SearchControls
                uploadedImage={uploadedImage}
                maxPrice={maxPrice}
                negativeQuery={negativeQuery}
                selectedCategory={selectedCategory}
                onMaxPriceChange={setMaxPrice}
                onNegativeQueryChange={setNegativeQuery}
                onCategoryChange={setSelectedCategory}
                onSearch={handleSearchUpdate}
                loading={loading}
              />
            </div>
          </div>

          {/* Right Panel - Scrollable */}
          <div className="flex-1">
            {loading && pins.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-20">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-black mb-4"></div>
                <p className="text-gray-600">Searching for similar items...</p>
              </div>
            ) : pins.length > 0 ? (
              <>
                <div className="mb-4">
                  <p className="text-sm text-gray-600">
                    Found <span className="font-semibold text-gray-900">{pins.length}</span> matching items
                  </p>
                </div>
                <MasonryGallery 
                  pins={pins} 
                  onPinClick={(pin) => setSelectedPin(pin)} 
                />
              </>
            ) : (
              <div className="text-center py-20 bg-white rounded-xl border-2 border-dashed border-gray-300">
                <p className="text-gray-500 text-lg">No results found</p>
                <p className="text-gray-400 text-sm mt-2">Try adjusting your search filters</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Pin Modal */}
      <PinModal 
        pin={selectedPin} 
        onClose={() => setSelectedPin(null)} 
      />
    </div>
  );
}
