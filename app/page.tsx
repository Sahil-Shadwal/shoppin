'use client';

import { useState, useEffect } from 'react';
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
  const [currentQuery, setCurrentQuery] = useState('fashion');

  const fetchPins = async (query: string, shuffle: boolean = false) => {
    setLoading(true);
    try {
      const shuffleParam = shuffle ? '&shuffle=true' : '';
      const response = await fetch(`/api/scrape?query=${encodeURIComponent(query)}${shuffleParam}`);
      const data = await response.json();
      
      if (data.success) {
        setPins(data.pins);
        setCurrentQuery(query);
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

  const handleShuffle = () => {
    // Fetch fresh pins with same query but shuffled
    fetchPins(currentQuery, true);
  };

  // Load initial pins on mount
  useEffect(() => {
    fetchPins('fashion');
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
          
          <SearchBar onSearch={(q) => fetchPins(q, false)} isLoading={loading} />
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-[2000px] mx-auto px-4 py-8">
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
          <p>Pinterest Clone - Built with Next.js & ScrapingBee</p>
          <p className="text-sm mt-2">For educational purposes only</p>
        </div>
      </footer>
    </div>
  );
}

