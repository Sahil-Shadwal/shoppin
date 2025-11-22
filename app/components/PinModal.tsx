'use client';

import React from 'react';
import { X } from 'lucide-react';

interface Pin {
  id: string;
  imageUrl: string;
  thumbnailUrl: string;
  title: string;
  sourceUrl: string;
  query: string;
}

interface PinModalProps {
  pin: Pin | null;
  onClose: () => void;
}

export default function PinModal({ pin, onClose }: PinModalProps) {
  if (!pin) return null;

  return (
    <div 
      className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4"
      onClick={onClose}
    >
      <div 
        className="relative bg-white rounded-3xl max-w-6xl max-h-[90vh] overflow-hidden shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 z-10 bg-white/90 hover:bg-white rounded-full p-2 transition-colors"
        >
          <X className="w-6 h-6" />
        </button>

        <div className="flex flex-col md:flex-row max-h-[90vh]">
          {/* Image section */}
          <div className="md:w-2/3 bg-gray-50 flex items-center justify-center p-8">
            <img
              src={pin.imageUrl.replace('474x', '736x')} // Get even higher resolution
              alt={pin.title}
              className="max-w-full max-h-[80vh] object-contain rounded-xl"
            />
          </div>

          {/* Details section */}
          <div className="md:w-1/3 p-8 overflow-y-auto">
            <div className="mb-6">
              <button className="w-full bg-red-600 text-white py-3 rounded-full font-semibold hover:bg-red-700 transition-colors mb-3">
                Save
              </button>
              <a
                href={pin.sourceUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="block w-full text-center border-2 border-gray-300 py-3 rounded-full font-semibold hover:bg-gray-50 transition-colors"
              >
                View on Pinterest
              </a>
            </div>

            <div className="space-y-4">
              <div>
                <h3 className="text-xs font-semibold text-gray-500 uppercase mb-2">
                  Description
                </h3>
                <p className="text-lg leading-relaxed">
                  {pin.title}
                </p>
              </div>

              <div>
                <h3 className="text-xs font-semibold text-gray-500 uppercase mb-2">
                  Category
                </h3>
                <span className="inline-block bg-gray-100 px-4 py-2 rounded-full text-sm font-medium">
                  {pin.query}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
