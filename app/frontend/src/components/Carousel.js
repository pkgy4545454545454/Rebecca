import React, { useRef } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';

const Carousel = ({ children, itemWidth = 400, gap = 24 }) => {
  const carouselRef = useRef(null);

  const scrollCarousel = (direction) => {
    if (carouselRef.current) {
      const scrollAmount = itemWidth + gap;
      const newScrollLeft = carouselRef.current.scrollLeft + (direction === 'left' ? -scrollAmount : scrollAmount);
      carouselRef.current.scrollTo({
        left: newScrollLeft,
        behavior: 'smooth'
      });
    }
  };

  return (
    <div className="relative">
      {/* Navigation Buttons */}
      <button
        onClick={() => scrollCarousel('left')}
        className="absolute left-0 top-1/2 -translate-y-1/2 z-10 bg-white hover:bg-gray-50 text-gray-700 p-3 rounded-full shadow-lg border border-gray-200 transition-all hover:scale-110 -ml-4"
        data-testid="carousel-prev"
      >
        <ChevronLeft className="w-6 h-6" />
      </button>
      
      <button
        onClick={() => scrollCarousel('right')}
        className="absolute right-0 top-1/2 -translate-y-1/2 z-10 bg-white hover:bg-gray-50 text-gray-700 p-3 rounded-full shadow-lg border border-gray-200 transition-all hover:scale-110 -mr-4"
        data-testid="carousel-next"
      >
        <ChevronRight className="w-6 h-6" />
      </button>

      {/* Carousel Container */}
      <div 
        ref={carouselRef}
        className="flex overflow-x-auto scrollbar-hide scroll-smooth pb-4 px-2"
        style={{ scrollbarWidth: 'none', msOverflowStyle: 'none', gap: `${gap}px` }}
      >
        {children}
      </div>
    </div>
  );
};

export default Carousel;
