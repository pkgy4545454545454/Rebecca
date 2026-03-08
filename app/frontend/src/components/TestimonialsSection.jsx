import React, { useState, useRef } from 'react';
import { Play, Pause, Quote, Star, ChevronLeft, ChevronRight } from 'lucide-react';

const testimonials = [
  {
    id: 1,
    name: "Marie Dupont",
    role: "Propriétaire - Salon de coiffure",
    avatar: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=100&h=100&fit=crop",
    rating: 5,
    text: "Grâce à Titelli, j'ai augmenté ma clientèle de 40% en 3 mois. La publicité IA est incroyablement efficace !",
    videoUrl: null,
    type: "entreprise"
  },
  {
    id: 2,
    name: "Jean-Pierre Martin",
    role: "Client fidèle depuis 2025",
    avatar: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop",
    rating: 5,
    text: "Le cashback Titelli m'a permis d'économiser plus de 500 CHF cette année. Je recommande à tous mes amis !",
    videoUrl: null,
    type: "client"
  },
  {
    id: 3,
    name: "Sophie Berger",
    role: "Restauratrice - Le Petit Bistrot",
    avatar: "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=100&h=100&fit=crop",
    rating: 5,
    text: "La plateforme est intuitive et le support est excellent. J'ai pu digitaliser mon restaurant en quelques jours.",
    videoUrl: null,
    type: "entreprise"
  },
  {
    id: 4,
    name: "Thomas Weber",
    role: "Entrepreneur - Services IT",
    avatar: "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=100&h=100&fit=crop",
    rating: 5,
    text: "Titelli Pro++ a transformé ma relation avec mes clients B2B. Les livraisons récurrentes sont un game-changer.",
    videoUrl: null,
    type: "entreprise"
  },
  {
    id: 5,
    name: "Laura Schneider",
    role: "Cliente Premium",
    avatar: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&h=100&fit=crop",
    rating: 5,
    text: "J'adore le système de parrainage ! J'ai déjà parrainé 10 amis et gagné plein de cashback bonus.",
    videoUrl: null,
    type: "client"
  }
];

const TestimonialCard = ({ testimonial, isActive }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const videoRef = useRef(null);

  const togglePlay = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
      } else {
        videoRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  return (
    <div className={`transition-all duration-500 ${
      isActive ? 'scale-100 opacity-100' : 'scale-95 opacity-50'
    }`}>
      <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10 max-w-lg mx-auto">
        {/* Video or Quote */}
        {testimonial.videoUrl ? (
          <div className="relative aspect-video rounded-xl overflow-hidden mb-4">
            <video
              ref={videoRef}
              src={testimonial.videoUrl}
              className="w-full h-full object-cover"
              poster={testimonial.avatar}
            />
            <button
              onClick={togglePlay}
              className="absolute inset-0 flex items-center justify-center bg-black/30 hover:bg-black/40 transition-colors"
            >
              {isPlaying ? (
                <Pause className="w-12 h-12 text-white" />
              ) : (
                <Play className="w-12 h-12 text-white" />
              )}
            </button>
          </div>
        ) : (
          <div className="relative mb-4">
            <Quote className="absolute -top-2 -left-2 w-8 h-8 text-blue-500/30" />
            <p className="text-gray-300 text-lg leading-relaxed pl-6">
              "{testimonial.text}"
            </p>
          </div>
        )}

        {/* Rating */}
        <div className="flex gap-1 mb-4">
          {Array.from({ length: 5 }).map((_, i) => (
            <Star
              key={i}
              className={`w-5 h-5 ${
                i < testimonial.rating ? 'text-yellow-400 fill-yellow-400' : 'text-gray-600'
              }`}
            />
          ))}
        </div>

        {/* Author */}
        <div className="flex items-center gap-4">
          <img
            src={testimonial.avatar}
            alt={testimonial.name}
            className="w-12 h-12 rounded-full object-cover border-2 border-white/20"
          />
          <div>
            <h4 className="font-semibold text-white">{testimonial.name}</h4>
            <p className="text-sm text-gray-400">{testimonial.role}</p>
          </div>
          <span className={`ml-auto px-3 py-1 rounded-full text-xs font-medium ${
            testimonial.type === 'entreprise'
              ? 'bg-purple-500/20 text-purple-400'
              : 'bg-blue-500/20 text-blue-400'
          }`}>
            {testimonial.type === 'entreprise' ? 'Entreprise' : 'Client'}
          </span>
        </div>
      </div>
    </div>
  );
};

const TestimonialsSection = () => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [filter, setFilter] = useState('all');

  const filteredTestimonials = filter === 'all'
    ? testimonials
    : testimonials.filter(t => t.type === filter);

  const handlePrev = () => {
    setCurrentIndex((prev) =>
      prev === 0 ? filteredTestimonials.length - 1 : prev - 1
    );
  };

  const handleNext = () => {
    setCurrentIndex((prev) =>
      prev === filteredTestimonials.length - 1 ? 0 : prev + 1
    );
  };

  return (
    <section className="py-20 px-4 bg-gradient-to-b from-[#0a0a0f] to-[#111118]">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
            Ce que disent nos utilisateurs
          </h2>
          <p className="text-gray-400 max-w-2xl mx-auto">
            Découvrez les témoignages de nos clients et entreprises partenaires
          </p>
        </div>

        {/* Filters */}
        <div className="flex justify-center gap-4 mb-8">
          {['all', 'client', 'entreprise'].map((type) => (
            <button
              key={type}
              onClick={() => {
                setFilter(type);
                setCurrentIndex(0);
              }}
              className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
                filter === type
                  ? 'bg-blue-600 text-white'
                  : 'bg-white/10 text-gray-400 hover:bg-white/20'
              }`}
            >
              {type === 'all' ? 'Tous' : type === 'client' ? 'Clients' : 'Entreprises'}
            </button>
          ))}
        </div>

        {/* Testimonials Carousel */}
        <div className="relative">
          {/* Navigation Buttons */}
          <button
            onClick={handlePrev}
            className="absolute left-0 top-1/2 -translate-y-1/2 z-10 w-10 h-10 bg-white/10 hover:bg-white/20 rounded-full flex items-center justify-center transition-colors"
          >
            <ChevronLeft className="w-6 h-6 text-white" />
          </button>
          
          <button
            onClick={handleNext}
            className="absolute right-0 top-1/2 -translate-y-1/2 z-10 w-10 h-10 bg-white/10 hover:bg-white/20 rounded-full flex items-center justify-center transition-colors"
          >
            <ChevronRight className="w-6 h-6 text-white" />
          </button>

          {/* Cards */}
          <div className="overflow-hidden px-12">
            <div
              className="flex transition-transform duration-500 ease-out"
              style={{
                transform: `translateX(-${currentIndex * 100}%)`
              }}
            >
              {filteredTestimonials.map((testimonial, index) => (
                <div key={testimonial.id} className="w-full flex-shrink-0">
                  <TestimonialCard
                    testimonial={testimonial}
                    isActive={index === currentIndex}
                  />
                </div>
              ))}
            </div>
          </div>

          {/* Dots */}
          <div className="flex justify-center gap-2 mt-8">
            {filteredTestimonials.map((_, index) => (
              <button
                key={index}
                onClick={() => setCurrentIndex(index)}
                className={`w-2 h-2 rounded-full transition-all ${
                  index === currentIndex
                    ? 'w-6 bg-blue-500'
                    : 'bg-white/20 hover:bg-white/40'
                }`}
              />
            ))}
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-16">
          {[
            { value: '8,249+', label: 'Entreprises' },
            { value: '50,000+', label: 'Clients actifs' },
            { value: '4.9/5', label: 'Note moyenne' },
            { value: '99.9%', label: 'Satisfaction' }
          ].map((stat, index) => (
            <div key={index} className="text-center">
              <div className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400">
                {stat.value}
              </div>
              <div className="text-gray-400 text-sm mt-1">{stat.label}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default TestimonialsSection;
