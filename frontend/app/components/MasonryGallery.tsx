'use client';

import React, { useState, useEffect } from 'react';
import Masonry from 'react-masonry-css';

interface Pin {
  id: string;
  imageUrl: string;
  thumbnailUrl: string;
  title: string;
  sourceUrl: string;
  query: string;
}

interface MasonryGalleryProps {
  pins: Pin[];
  onPinClick?: (pin: Pin) => void;
}

export default function MasonryGallery({ pins, onPinClick }: MasonryGalleryProps) {
  const [visibleCount, setVisibleCount] = useState(10); // Start with 10 pins
  
  // Progressive loading: show more pins gradually
  useEffect(() => {
    setVisibleCount(10); // Reset when pins change
    
    if (pins.length > 10) {
      const timer = setTimeout(() => {
        setVisibleCount(Math.min(30, pins.length)); // Show 30 after 100ms
      }, 100);
      
      const timer2 = setTimeout(() => {
        setVisibleCount(pins.length); // Show all after 200ms
      }, 200);
      
      return () => {
        clearTimeout(timer);
        clearTimeout(timer2);
      };
    }
  }, [pins]);
  
  const breakpointColumns = {
    default: 6,
    1536: 5,
    1280: 4,
    1024: 3,
    768: 2,
    640: 2
  };

  const visiblePins = pins.slice(0, visibleCount);

  return (
    <Masonry
      breakpointCols={breakpointColumns}
      className="flex -ml-4 w-auto"
      columnClassName="pl-4 bg-clip-padding"
    >
      {visiblePins.map((pin, index) => (
        <div
          key={pin.id}
          className="mb-4 group cursor-pointer relative overflow-hidden rounded-2xl transition-all duration-300 hover:scale-[1.02] animate-fadeIn"
          onClick={() => onPinClick?.(pin)}
          style={{
            animationDelay: `${index * 20}ms` // Stagger animation
          }}
        >
          <img
            src={pin.imageUrl}
            alt={pin.title}
            className="w-full h-auto block rounded-2xl"
            loading={index < 10 ? 'eager' : 'lazy'} // Eager load first 10
          />
          
          {/* Overlay on hover */}
          <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-2xl flex flex-col justify-end p-4">
            <p className="text-white text-sm font-medium line-clamp-2">
              {pin.title}
            </p>
          </div>

          {/* Save button (Pinterest style) */}
          <button className="absolute top-4 right-4 bg-red-600 text-white px-4 py-2 rounded-full text-sm font-semibold opacity-0 group-hover:opacity-100 transition-opacity duration-300 hover:bg-red-700">
            Save
          </button>
        </div>
      ))}
    </Masonry>
  );
}
