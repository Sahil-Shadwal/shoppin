'use client';

import { Search, Camera } from 'lucide-react';
import { useState, useRef } from 'react';

interface SearchBarProps {
  onSearch: (query: string) => void;
  onImageSearch: (file: File) => void;
  isLoading?: boolean;
}

const SUGGESTIONS = [
  'Minimal Streetwear',
  'Men\'s Streetwear Outfit Ideas',
  'Streetwear Outfit Ideas',
  'Streetwear Fashion Instagram',
  'Luxury Fashion – Roxx Inspire',
  'Luxury Classy Outfits',
  'Luxury Streetwear Brands',
];

export default function SearchBar({ onSearch, onImageSearch, isLoading }: SearchBarProps) {
  const [query, setQuery] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query.trim());
      setShowSuggestions(false);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setQuery(suggestion);
    onSearch(suggestion);
    setShowSuggestions(false);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      onImageSearch(file);
    }
  };

  return (
    <div className="relative w-full max-w-2xl mx-auto">
      <form onSubmit={handleSubmit} className="relative">
        <div className="flex items-center gap-2 bg-white rounded-full shadow-lg px-6 py-4 border-2 border-transparent focus-within:border-black transition-all">
          <Search className="w-6 h-6 text-gray-400" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onFocus={() => setShowSuggestions(true)}
            placeholder="Search fashion styles..."
            className="flex-1 outline-none text-lg"
            disabled={isLoading}
          />
          
          {/* Camera Button */}
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className="flex items-center gap-2 bg-black text-white px-4 py-2 rounded-full hover:bg-gray-800 transition-colors"
          >
            <Camera className="w-5 h-5" />
            <span className="text-sm font-medium">Upload</span>
          </button>
          
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleFileChange}
            className="hidden"
          />
        </div>
      </form>

      {/* Suggestions Dropdown */}
      {showSuggestions && (
        <>
          {/* Backdrop to close dropdown */}
          <div 
            className="fixed inset-0 z-10" 
            onClick={() => setShowSuggestions(false)}
          />
          
          {/* Suggestions List */}
          <div className="absolute top-full left-0 right-0 mt-2 bg-white rounded-2xl shadow-xl border border-gray-200 overflow-hidden z-20">
            <div className="p-3">
              <p className="text-xs font-semibold text-gray-500 uppercase px-3 py-2">
                Popular Styles
              </p>
              {SUGGESTIONS.map((suggestion) => (
                <button
                  key={suggestion}
                  onClick={() => handleSuggestionClick(suggestion)}
                  className="w-full text-left px-3 py-2.5 hover:bg-gray-100 rounded-lg transition-colors text-gray-700"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
