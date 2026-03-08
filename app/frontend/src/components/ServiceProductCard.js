import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Star } from 'lucide-react';
import { wishlistAPI } from '../services/api';
import { toast } from 'sonner';

const ServiceProductCard = ({ item, onAddToCart }) => {
  const navigate = useNavigate();
  const [isInWishlist, setIsInWishlist] = useState(false);
  const [wishlistLoading, setWishlistLoading] = useState(false);
  
  const {
    id,
    name,
    description,
    price,
    currency,
    type,
    images,
    is_premium,
    is_delivery,
    enterprise_id,
    enterprise_name,
    rating,
    review_count,
    available = true
  } = item;

  const handleToggleWishlist = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    const token = localStorage.getItem('titelli_token');
    if (!token) {
      toast.error('Connectez-vous pour ajouter aux favoris');
      navigate('/auth');
      return;
    }
    
    setWishlistLoading(true);
    try {
      if (isInWishlist) {
        await wishlistAPI.remove(id);
        setIsInWishlist(false);
        toast.success('Retiré des favoris');
      } else {
        await wishlistAPI.add({
          item_id: id,
          item_type: type,
          item_name: name,
          item_price: price,
          item_image: images?.[0] || '',
          enterprise_id: enterprise_id,
          enterprise_name: enterprise_name
        });
        setIsInWishlist(true);
        toast.success('Ajouté aux favoris !');
      }
    } catch (error) {
      const errorMsg = error.response?.data?.detail;
      if (typeof errorMsg === 'string') {
        toast.error(errorMsg);
      } else if (Array.isArray(errorMsg)) {
        toast.error(errorMsg[0]?.msg || 'Erreur de validation');
      } else {
        toast.error('Erreur lors de l\'ajout aux favoris');
      }
    } finally {
      setWishlistLoading(false);
    }
  };

  const defaultImage = type === 'service' 
    ? 'https://images.unsplash.com/photo-1521737711867-e3b97375f902?w=800'
    : 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800';

  // Format rating display
  const displayRating = rating ? `${rating.toFixed(1)} / 5` : '4.5 / 5';
  const displayReviews = review_count || 0;

  return (
    <div 
      className="bg-white border border-gray-100 shadow-sm hover:shadow-lg group rounded-2xl overflow-hidden transition-all"
      data-testid={`item-card-${id}`}
    >
      {/* Image - Clean without overlays */}
      <Link to={`/${type}/${id}`} className="block relative h-44 sm:h-52 overflow-hidden">
        <img
          src={images?.[0] || defaultImage}
          alt={name}
          className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
        />
      </Link>

      {/* Content */}
      <div className="p-4">
        <Link to={`/${type}/${id}`}>
          <h3 className="text-base font-semibold text-gray-900 group-hover:text-[#0047AB] transition-colors mb-1 line-clamp-1">
            {name}
          </h3>
        </Link>

        <p className="text-sm text-gray-500 mb-3 line-clamp-2">
          {description}
        </p>

        {/* Rating */}
        <div className="flex items-center gap-1 mb-3 justify-center">
          <Star className="w-4 h-4 text-yellow-400 fill-yellow-400" />
          <span className="text-sm text-gray-700 font-medium">{displayRating}</span>
          {displayReviews > 0 && (
            <span className="text-xs text-gray-400">({displayReviews} avis)</span>
          )}
        </div>

        {/* Price - smaller */}
        <p className="text-sm font-medium text-gray-900 mb-4 justify-center m-auto" style={{textAlign:'center', color: is_premium ? '#D4AF37' : '#0047AB'}}>
          {(price || 0).toFixed(2)} {currency}
        </p>

        {/* Action buttons below */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => onAddToCart?.(item)}
            disabled={!available}
            className={`flex-1 py-2.5 rounded-xl text-sm font-medium transition-all ${
              available 
                ? 'bg-[#0047AB] text-white hover:bg-[#0047AB]/90' 
                : 'bg-gray-200 text-gray-400 cursor-not-allowed'
            }`}
            data-testid={`add-to-cart-${id}`}
          >
            {available ? (type === 'product' ? 'Ajouter au panier' : 'Réserver') : 'Bientôt'}
          </button>
          
          <button
            onClick={handleToggleWishlist}
            disabled={wishlistLoading}
            className={`px-4 py-2.5 rounded-xl text-sm font-medium border transition-all ${
              isInWishlist 
                ? 'bg-red-50 text-red-500 border-red-200' 
                : 'bg-gray-50 text-gray-600 border-gray-200 hover:bg-gray-100'
            }`}
            data-testid={`wishlist-btn-${id}`}
          >
            {isInWishlist ? '♥' : '♡'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ServiceProductCard;
