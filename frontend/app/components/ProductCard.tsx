'use client';

import React from 'react';

interface ProductCardProps {
  id: string;
  imageUrl: string;
  title: string;
  brand: string;
  price: number;
  score: number;
  productUrl: string;
}

export default function ProductCard({
  imageUrl,
  title,
  brand,
  price,
  score,
  productUrl
}: ProductCardProps) {
  const matchPercentage = Math.round(score * 100);
  
  return (
    <a
      href={productUrl}
      target="_blank"
      rel="noopener noreferrer"
      className="block group"
    >
      <div className="bg-white rounded-2xl overflow-hidden shadow-md hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1">
        {/* Product Image */}
        <div className="relative aspect-square bg-gray-100">
          <img
            src={imageUrl}
            alt={title}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
          />
          {/* Match Badge */}
          <div className="absolute top-3 right-3 bg-white/95 backdrop-blur-sm px-3 py-1.5 rounded-full shadow-lg">
            <span className="text-sm font-bold text-gray-900">{matchPercentage}% Match</span>
          </div>
        </div>

        {/* Product Info */}
        <div className="p-4">
          <h3 className="font-bold text-gray-900 text-lg mb-1 line-clamp-1">
            {brand}
          </h3>
          <p className="text-gray-600 text-sm mb-3 line-clamp-2">
            {title}
          </p>
          <p className="text-2xl font-bold text-gray-900">
            ${price.toLocaleString()}
          </p>
        </div>
      </div>
    </a>
  );
}
