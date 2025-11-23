'use client';

import React, { useState } from 'react';
import { Search } from 'lucide-react';

interface SearchBarProps {
  onSearch: (query: string) => void;
  onImageSearch?: (file: File) => void;
  isLoading?: boolean;
}

export default function SearchBar({ onSearch, onImageSearch, isLoading }: SearchBarProps) {
  const [query, setQuery] = useState('Minimal Streetwear');
  const [isScraping, setIsScraping] = useState(false);
  const [message, setMessage] = useState('');
  const fileInputRef = React.useRef<HTMLInputElement>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query.trim());
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && onImageSearch) {
      onImageSearch(file);
    }
  };

  const suggestedQueries = [
    // Pinterest Boards
    'Minimal Streetwear',
    "Men's Streetwear Outfit Ideas",
    'Streetwear Outfit Ideas',
    'Streetwear Fashion Instagram',
    'Luxury Fashion – Roxx Inspire',
    'Luxury Classy Outfits',
    'Luxury Streetwear Brands'
  ];

  return (
    <div className="w-full max-w-4xl mx-auto">
      <form onSubmit={handleSubmit} className="relative">
        <div className="relative flex items-center">
          <Search className="absolute left-4 text-gray-400 w-5 h-5" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search for ideas..."
            className="w-full pl-12 pr-32 py-4 rounded-full border border-gray-300 focus:border-red-500 focus:outline-none focus:ring-2 focus:ring-red-500/20 text-lg transition-all"
            disabled={isLoading}
          />
          
          <div className="absolute right-2 flex items-center gap-2">
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              accept="image/*"
              className="hidden"
            />
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className="p-2 text-gray-500 hover:text-red-600 hover:bg-gray-100 rounded-full transition-colors"
              title="Search by image"
              disabled={isLoading}
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                <path strokeLinecap="round" strokeLinejoin="round" d="M6.827 6.175A2.31 2.31 0 015.186 7.23c-.38.054-.757.112-1.134.175C2.999 7.58 2.25 8.507 2.25 9.574V18a2.25 2.25 0 002.25 2.25h15A2.25 2.25 0 0021.75 18V9.574c0-1.067-.75-1.994-1.802-2.169a47.865 47.865 0 00-1.134-.175 2.31 2.31 0 01-1.64-1.055l-.822-1.316a2.192 2.192 0 00-1.736-1.039 48.774 48.774 0 00-5.232 0 2.192 2.192 0 00-1.736 1.039l-.821 1.316z" />
                <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 12.75a4.5 4.5 0 11-9 0 4.5 4.5 0 019 0zM18.75 10.5h.008v.008h-.008V10.5z" />
              </svg>
            </button>
            
            <button
              type="submit"
              disabled={isLoading}
              className="bg-red-600 text-white px-6 py-2 rounded-full font-semibold hover:bg-red-700 transition-colors disabled:bg-gray-400"
            >
              {isLoading ? 'Loading...' : 'Search'}
            </button>
          </div>
        </div>
      </form>

      {/* Popular searches */}
      <div className="mt-4 flex flex-wrap gap-2 justify-center max-w-2xl mx-auto">
        {suggestedQueries.map((search) => (
          <button
            key={search}
            onClick={() => {
              setQuery(search);
              onSearch(search);
            }}
            className="px-4 py-2 rounded-full bg-gray-100 hover:bg-gray-200 text-sm transition-colors"
          >
            {search}
          </button>
        ))}
      </div>
    </div>
  );
}
