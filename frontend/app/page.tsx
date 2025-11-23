'use client';

import { useState, useEffect, useRef } from 'react';
import MasonryGallery from './components/MasonryGallery';
import SearchBar from './components/SearchBar';
import PinModal from './components/PinModal';
import ShuffleButton from './components/ShuffleButton';

interface Pin {
  id: string;
  imageUrl: string;
  thumbnailUrl: string;
  title: string;
  sourceUrl: string;
  query: string;
}

export default function Home() {
  const [pins, setPins] = useState<Pin[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedPin, setSelectedPin] = useState<Pin | null>(null);
  const [currentQuery, setCurrentQuery] = useState('Minimal Streetwear');
  const [uploadedImage, setUploadedImage] = useState<string | null>(null);
  
  // Client-side cache for instant category switching
  const pinsCache = useRef<Record<string, Pin[]>>({});

  const fetchPins = async (query: string, shuffle: boolean = false) => {
    // Check client-side cache first (unless shuffling)
    if (!shuffle && pinsCache.current[query]) {
      console.log('⚡ Loaded from CLIENT CACHE - instant!');
      setPins(pinsCache.current[query]);
      setCurrentQuery(query);
      setUploadedImage(null); // Clear uploaded image on text search
      return;
    }
    
    setLoading(true);
    try {
      const shuffleParam = shuffle ? '&shuffle=true' : '';
      // Use optimized route that checks DB first
      const response = await fetch(`/api/fetch-pins?query=${encodeURIComponent(query)}${shuffleParam}`);
      const data = await response.json();
      
      if (data.success) {
        setPins(data.pins);
        setCurrentQuery(query);
        setUploadedImage(null); // Clear uploaded image on text search
        
        // Store in client-side cache for instant re-access
        if (!shuffle) {
          pinsCache.current[query] = data.pins;
        }
        
        // Log if we're using cached data
        if (data.cached) {
          console.log('✅ Loaded from DB cache');
        } else {
          console.log('🔄 Scraped fresh content');
        }
      } else {
        console.error('Failed to fetch pins:', data.error);
        alert('Failed to load pins. Please try again.');
      }
    } catch (error) {
      console.error('Error fetching pins:', error);
      alert('Error loading pins. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleImageSearch = async (file: File) => {
    console.log(`📸 Uploading image: ${file.name} (${(file.size / 1024).toFixed(2)} KB)`);
    
    try {
      // Upload to temp storage endpoint
      const formData = new FormData();
      formData.append('image', file);
      
      const uploadResponse = await fetch('/api/upload-temp', {
        method: 'POST',
        body: formData,
      });
      
      if (!uploadResponse.ok) {
        throw new Error('Failed to upload image');
      }
      
      const uploadData = await uploadResponse.json();
      const imageUrl = uploadData.imageUrl;
      
      console.log('✅ Image cached at:', imageUrl);
      
      // Store permanent URL in sessionStorage
      sessionStorage.setItem('searchImageUrl', imageUrl);
      
      // Convert file to base64 for storage
      const reader = new FileReader();
      reader.onloadend = () => {
        sessionStorage.setItem('searchImageFile', reader.result as string);
        // Redirect to search page
        window.location.href = '/search';
      };
      reader.readAsDataURL(file);
    } catch (error) {
      console.error('❌ Failed to upload image:', error);
      alert('Failed to upload image. Please try again.');
    }
  };

  const handleShuffle = () => {
    // Fetch fresh pins with same query but shuffled
    fetchPins(currentQuery, true);
  };

  // Load initial pins on mount
  useEffect(() => {
    fetchPins('Minimal Streetwear');
  }, []);

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="sticky top-0 z-40 bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-[2000px] mx-auto px-4 py-4">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-8">
              <h1 className="text-2xl font-bold text-red-600">
                Sh🍓ppin
              </h1>
              <nav className="hidden md:flex gap-6">
                <button className="font-semibold hover:underline">Home</button>
                <button className="font-semibold hover:underline">Explore</button>
              </nav>
            </div>
          </div>
          
          <SearchBar 
            onSearch={(q) => fetchPins(q, false)} 
            onImageSearch={handleImageSearch}
            isLoading={loading} 
          />
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-[2000px] mx-auto px-4 py-8 relative">
        {/* Blur overlay during loading - FIXED to viewport */}
        {loading && pins.length > 0 && (
          <div className="fixed inset-0 bg-white/60 backdrop-blur-sm z-50 flex items-center justify-center">
            <div className="flex flex-col items-center gap-4">
              {/* Classic circular spinner */}
              <div className="relative w-16 h-16">
                <div className="absolute inset-0 border-4 border-gray-200 rounded-full"></div>
                <div className="absolute inset-0 border-4 border-red-600 rounded-full border-t-transparent animate-spin"></div>
              </div>
              <p className="text-gray-700 font-medium">Loading fresh pins...</p>
            </div>
          </div>
        )}
        
        {loading && pins.length === 0 ? (
          <div className="flex flex-col items-center justify-center min-h-[60vh]">
            <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-red-600 mb-4"></div>
            <p className="text-gray-600 text-lg">Loading amazing pins...</p>
          </div>
        ) : pins.length > 0 ? (
          <>
          <div className="mb-6 text-center">
            <h2 className="text-2xl font-bold text-gray-800">
              {currentQuery.charAt(0).toUpperCase() + currentQuery.slice(1)} Ideas
            </h2>
            
            {/* Show uploaded image reference if available */}
            {currentQuery === 'Visual Search' && uploadedImage && (
              <div className="mt-4 flex flex-col items-center">
                <p className="text-sm text-gray-500 mb-2">Based on your upload:</p>
                <div className="relative w-32 h-32 rounded-xl overflow-hidden shadow-md border-2 border-white">
                  <img 
                    src={uploadedImage} 
                    alt="Uploaded reference" 
                    className="w-full h-full object-cover"
                  />
                </div>
              </div>
            )}
            
            <p className="text-gray-600 mt-2">
              {pins.length} pins found
            </p>
          </div>
            
            <MasonryGallery 
              pins={pins} 
              onPinClick={setSelectedPin}
            />
          </>
        ) : (
          <div className="flex flex-col items-center justify-center min-h-[60vh]">
            <p className="text-gray-600 text-lg">No pins found. Try a different search!</p>
          </div>
        )}
      </main>

      {/* Pin Detail Modal */}
      <PinModal 
        pin={selectedPin} 
        onClose={() => setSelectedPin(null)} 
      />

      {/* Shuffle Button */}
      <ShuffleButton onShuffle={handleShuffle} isLoading={loading} />

      {/* Footer */}
      <footer className="border-t border-gray-200 mt-16 py-8">
        <div className="max-w-[2000px] mx-auto px-4 text-center text-gray-600">
          <p>Shoppin - Built with Next.js & Django </p>
          <p className="text-sm mt-2">For onboarding purpose only!</p>
        </div>
      </footer>
    </div>
  );
}

