'use client';

import React from 'react';
import { Shuffle } from 'lucide-react';

interface ShuffleButtonProps {
  onShuffle: () => void;
  isLoading?: boolean;
}

export default function ShuffleButton({ onShuffle, isLoading }: ShuffleButtonProps) {
  return (
    <button
      onClick={onShuffle}
      disabled={isLoading}
      className="fixed bottom-8 right-8 bg-red-600 text-white p-4 rounded-full shadow-2xl hover:bg-red-700 transition-all duration-300 hover:scale-110 disabled:bg-gray-400 disabled:cursor-not-allowed z-50 flex items-center gap-2"
      title="Get fresh pins"
    >
      <Shuffle className={`w-6 h-6 ${isLoading ? 'animate-spin' : ''}`} />
      <span className="font-semibold hidden md:inline">
        {isLoading ? 'Loading...' : 'Shuffle'}
      </span>
    </button>
  );
}
