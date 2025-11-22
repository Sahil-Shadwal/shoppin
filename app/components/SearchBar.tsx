'use client';

import React, { useState } from 'react';
import { Search } from 'lucide-react';

interface SearchBarProps {
  onSearch: (query: string) => void;
  isLoading?: boolean;
}

export default function SearchBar({ onSearch, isLoading }: SearchBarProps) {
  const [query, setQuery] = useState('fashion');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query.trim());
    }
  };

  const popularSearches = [
    'fashion',
    'fashion model',
    'street style',
    'outfit ideas',
    'home decor',
    'recipes',
    'art',
    'architecture'
  ];

  return (
    <div className="w-full max-w-4xl mx-auto">
      <form onSubmit={handleSubmit} className="relative">
        <div className="relative">
          <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search for ideas..."
            className="w-full pl-12 pr-4 py-4 rounded-full border border-gray-300 focus:border-red-500 focus:outline-none focus:ring-2 focus:ring-red-500/20 text-lg transition-all"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading}
            className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-red-600 text-white px-6 py-2 rounded-full font-semibold hover:bg-red-700 transition-colors disabled:bg-gray-400"
          >
            {isLoading ? 'Loading...' : 'Search'}
          </button>
        </div>
      </form>

      {/* Popular searches */}
      <div className="mt-4 flex flex-wrap gap-2 justify-center">
        {popularSearches.map((search) => (
          <button
            key={search}
            onClick={() => {
              setQuery(search);
              onSearch(search);
            }}
            className="px-4 py-2 rounded-full bg-gray-100 hover:bg-gray-200 text-sm font-medium transition-colors"
            disabled={isLoading}
          >
            {search}
          </button>
        ))}
      </div>
    </div>
  );
}
