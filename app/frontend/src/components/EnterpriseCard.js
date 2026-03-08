import React from 'react';
import { Link } from 'react-router-dom';
import { Star, MapPin } from 'lucide-react';

const EnterpriseCard = ({ enterprise, large = false }) => {
  const {
    id,
    business_name,
    name,
    slogan,
    description,
    category,
    city,
    rating,
    review_count,
    is_certified,
    is_labeled,
    is_premium,
    cover_image,
    logo,
    display_status,
    activation_status
  } = enterprise;

  const defaultImage = 'https://images.unsplash.com/photo-1497366216548-37526070297c?w=800';
  
  const [coverError, setCoverError] = React.useState(false);
  const [logoError, setLogoError] = React.useState(false);
  
  const isValidUrl = (url) => {
    if (!url) return false;
    if (url.includes('enterprise-media.preview.emergentagent.com')) return false;
    return true;
  };
  
  const actualCover = !coverError && isValidUrl(cover_image) ? cover_image : defaultImage;
  const actualLogo = !logoError && isValidUrl(logo) ? logo : null;
  
  const isActive = display_status === 'actif' || activation_status === 'active';
  const displayName = name || business_name;
  const displayRating = rating ? `${rating.toFixed(1)} / 5` : '4.5 / 5';

  const imageHeight = large ? 'h-44 sm:h-56' : 'h-36 sm:h-48';
  const cardPadding = large ? 'p-3 sm:p-5' : 'p-3 sm:p-4';
  const titleSize = large ? 'text-sm sm:text-xl' : 'text-sm sm:text-lg';

  return (
    <Link 
      to={`/entreprise/${id}`}
      className="bg-white border border-gray-100 shadow-sm hover:shadow-lg group block rounded-2xl overflow-hidden h-full transition-all"
      data-testid={`enterprise-card-${id}`}
    >
      {/* Image */}
      <div className={`relative ${imageHeight} overflow-hidden`}>
        <img
          src={actualCover}
          alt={displayName}
          className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
          onError={() => setCoverError(true)}
        />
        
        {/* Logo */}
        {actualLogo && (
          <div className={`absolute bottom-3 right-3 ${large ? 'w-12 h-12' : 'w-10 h-10'} rounded-full bg-white p-1 shadow-md`}>
            <img 
              src={actualLogo} 
              alt="" 
              className="w-full h-full object-cover rounded-full" 
              onError={() => setLogoError(true)}
            />
          </div>
        )}
      </div>

      {/* Content */}
      <div className={cardPadding}>
        {/* Category - Enterprise Name */}
        <h3 className={`${titleSize} font-semibold text-gray-900 group-hover:text-[#0047AB] transition-colors line-clamp-2 mb-2`}>
          <span className="text-[#D4AF37]">{category}</span>
          <span className="text-gray-400 mx-1">-</span>
          {displayName}
        </h3>

        {/* Rating - Full format */}
        <div className="flex items-center gap-1.5 mb-3">
          <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
          <span className="text-sm font-medium text-gray-700">{displayRating}</span>
          {review_count > 0 && (
            <span className="text-xs text-gray-400">({review_count} avis)</span>
          )}
        </div>

        <div className="flex items-center justify-end text-xs sm:text-sm gap-2">
          <div className="flex items-center gap-1 text-gray-400">
            <MapPin className="w-3.5 h-3.5" />
            <span className="line-clamp-1">{city}</span>
          </div>
        </div>

        {/* Reserve button */}
        <button 
          className={`w-full mt-4 py-2.5 rounded-xl text-sm font-medium transition-all ${
            isActive 
              ? 'bg-[#0047AB] text-white hover:bg-[#0047AB]/90' 
              : 'bg-gray-200 text-gray-500'
          }`}
        >
          {isActive ? 'Réserver' : 'Bientôt'}
        </button>
      </div>
    </Link>
  );
};

export default EnterpriseCard;
