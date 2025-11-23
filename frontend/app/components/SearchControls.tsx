'use client';

import React from 'react';
import { Search, X } from 'lucide-react';
import { type } from 'os';

interface SearchControlsProps {
  uploadedImage: string | null;
  maxPrice: number;
  negativeQuery: string;
  textQuery: string;
  selectedCategory: string | null;
  onMaxPriceChange: (price: number) => void;
  onNegativeQueryChange: (query: string) => void;
  onTextQueryChange: (query: string) => void;
  onCategoryChange: (category: string | null) => void;
  onSearch: () => void;
  loading: boolean;
}

export default function SearchControls({
  uploadedImage,
  maxPrice,
  negativeQuery,
  textQuery,
  selectedCategory,
  onMaxPriceChange,
  onNegativeQueryChange,
  onTextQueryChange,
  onCategoryChange,
  onSearch,
  loading
}: SearchControlsProps) {
  const categories = [
    { id: 'tops', label: 'Tops' },
    { id: 'bottoms', label: 'Bottoms' },
    { id: 'footwear', label: 'Shoes' },
    { id: 'outerwear', label: 'Jackets' },
    { id: 'bags', label: 'Purse' },
    { id: 'bottles', label: 'Bottles' },
    { id: 'accessories', label: 'Accessories' },
  ];

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
          Style Description
        </label>
        <input
          type="text"
          value={textQuery}
          onChange={(e) => onTextQueryChange(e.target.value)}
          placeholder='e.g., "same vibe but blue"'
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent"
        />
        <p className="text-xs text-gray-500 mt-1">
          Describe the style you're looking for
        </p>
      </div>

      {/* Max Price Slider */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <label className="text-sm font-semibold text-gray-700">
            Budget Filter
          </label>
          <span className="text-sm font-mono text-gray-900">
            {maxPrice >= 500 ? 'Any' : `$${maxPrice}`}
          </span>
        </div>
        <input
          type="range"
          min="0"
          max="500"
          step="10"
          value={maxPrice}
          onChange={(e) => onMaxPriceChange(Number(e.target.value))}
          className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-black"
        />
        <div className="flex justify-between text-xs text-gray-500 mt-1">
          <span>$0</span>
          <span>$500+</span>
        </div>
      </div>

      {/* Negative Search */}
      <div>
        <label className="text-sm font-semibold text-gray-700 mb-2 block">
          Exclude Items
        </label>
        <div className="relative">
          <input
            type="text"
            value={negativeQuery}
            onChange={(e) => onNegativeQueryChange(e.target.value)}
            placeholder="e.g., sneakers, leather"
            className="w-full px-4 py-2 pr-10 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent"
          />
          {negativeQuery && (
            <button
              onClick={() => onNegativeQueryChange('')}
              className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
        <p className="text-xs text-gray-500 mt-1">
          Filter out unwanted styles
        </p>
      </div>

      {/* Category Filter */}
      <div>
        <label className="text-sm font-semibold text-gray-700 mb-2 block">
          Category
        </label>
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => onCategoryChange(null)}
            className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all ${
              selectedCategory === null
                ? 'bg-black text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            All
          </button>
          {categories.map((cat) => (
            <button
              key={cat.id}
              onClick={() => onCategoryChange(cat.id === selectedCategory ? null : cat.id)}
              className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all ${
                selectedCategory === cat.id
                  ? 'bg-black text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {cat.label}
            </button>
          ))}
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
