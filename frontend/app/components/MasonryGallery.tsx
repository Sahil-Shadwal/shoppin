'use client';

import React from 'react';
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
  const breakpointColumns = {
    default: 6,
    1536: 5,
    1280: 4,
    1024: 3,
    768: 2,
    640: 2
  };

  return (
    <Masonry
      breakpointCols={breakpointColumns}
      className="flex -ml-4 w-auto"
      columnClassName="pl-4 bg-clip-padding"
    >
      {pins.map((pin) => (
        <div
          key={pin.id}
          className="mb-4 group cursor-pointer relative overflow-hidden rounded-2xl transition-all duration-300 hover:scale-[1.02]"
          onClick={() => onPinClick?.(pin)}
        >
          <img
            src={pin.imageUrl}
            alt={pin.title}
            className="w-full h-auto block rounded-2xl"
            loading="lazy"
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
