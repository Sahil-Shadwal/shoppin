'use client';

import React from 'react';
import { Search, X } from 'lucide-react';
import { type } from 'os';

interface SearchControlsProps {
  uploadedImage: string | null;
  maxPrice: number;
  textQuery: string;
  onMaxPriceChange: (price: number) => void;
  onTextQueryChange: (query: string) => void;
  onSearch: () => void;
  loading: boolean;
}

export default function SearchControls({
  uploadedImage,
  maxPrice,
  textQuery,
  onMaxPriceChange,
  onTextQueryChange,
  onSearch,
  loading
}: SearchControlsProps) {
  return (
    <div className="bg-white rounded-2xl shadow-lg p-6 space-y-6">
      {/* Uploaded Image Preview */}
      {uploadedImage && (
        <div>
          <h3 className="text-sm font-semibold text-gray-700 mb-3">Your Image</h3>
          <div className="relative aspect-square rounded-xl overflow-hidden border-2 border-gray-200">
            <img 
              src={uploadedImage} 
              alt="Uploaded" 
              className="w-full h-full object-cover"
            />
          </div>
        </div>
      )}

      {/* Text Search Input */}
      <div>
        <label className="text-sm font-semibold text-gray-700 mb-2 block">
          Refine Search
        </label>
        <input
          type="text"
          value={textQuery}
          onChange={(e) => onTextQueryChange(e.target.value)}
          placeholder='e.g., "white shoes no leather"'
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent"
        />
        <p className="text-xs text-gray-500 mt-1">
          Describe what you want (color, style, exclusions)
        </p>
      </div>

      {/* Max Price Slider */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <label className="text-sm font-semibold text-gray-700">
            Budget Filter
          </label>
          <span className="text-sm font-mono text-gray-900">
            {maxPrice >= 50000 ? 'Any' : `$${maxPrice.toLocaleString()}`}
          </span>
        </div>
        <input
          type="range"
          min="0"
          max="50000"
          step="100"
          value={maxPrice}
          onChange={(e) => onMaxPriceChange(Number(e.target.value))}
          className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-black"
        />
        <div className="flex justify-between text-xs text-gray-500 mt-1">
          <span>$0</span>
          <span>$50k+</span>
        </div>
      </div>

      {/* Search Button */}
      <button
        onClick={onSearch}
        disabled={loading}
        className="w-full flex items-center justify-center gap-2 bg-black text-white px-6 py-3 rounded-xl font-semibold hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
      >
        <Search className="w-5 h-5" />
        {loading ? 'Searching...' : 'Update Results'}
      </button>
    </div>
  );
}
