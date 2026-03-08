import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { ArrowLeft, Star, MapPin, Clock, Truck, ShoppingCart, Heart, Share2, Phone, Mail, Globe, Check, AlertCircle } from 'lucide-react';
import { servicesProductsAPI, enterpriseAPI, reviewAPI, wishlistAPI } from '../services/api';
import { useCart } from '../context/CartContext';
import { toast } from 'sonner';

const ServiceProductDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { addItem } = useCart();
  
  const [item, setItem] = useState(null);
  const [enterprise, setEnterprise] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [relatedItems, setRelatedItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [quantity, setQuantity] = useState(1);
  const [selectedImage, setSelectedImage] = useState(0);
  const [isInWishlist, setIsInWishlist] = useState(false);
  const [wishlistLoading, setWishlistLoading] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        // Fetch the service/product
        const itemRes = await servicesProductsAPI.get(id);
        setItem(itemRes.data);
        
        // Check if item is in wishlist
        try {
          const wishlistCheck = await wishlistAPI.check(id);
          setIsInWishlist(wishlistCheck.data.in_wishlist);
        } catch (e) {
          // Not logged in or error - ignore
        }
        
        // Fetch the enterprise
        if (itemRes.data.enterprise_id) {
          const entRes = await enterpriseAPI.getById(itemRes.data.enterprise_id);
          setEnterprise(entRes.data);
          
          // Fetch reviews for the enterprise
          try {
            const reviewsRes = await reviewAPI.getByEnterprise(itemRes.data.enterprise_id);
            setReviews(reviewsRes.data.reviews || []);
          } catch (e) {
            console.error('Error fetching reviews:', e);
          }
          
          // Fetch related items from same enterprise
          try {
            const relatedRes = await servicesProductsAPI.list({ 
              enterprise_id: itemRes.data.enterprise_id,
              type: itemRes.data.type 
            });
            setRelatedItems(relatedRes.data.items.filter(i => i.id !== id).slice(0, 4));
          } catch (e) {
            console.error('Error fetching related items:', e);
          }
        }
      } catch (error) {
        console.error('Error fetching item:', error);
        setError('Ce service ou produit n\'existe pas ou a été supprimé.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, [id]);

  const handleToggleWishlist = async () => {
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
        toast.success('Retiré de votre liste de souhaits');
      } else {
        await wishlistAPI.add({
          item_id: id,
          item_type: item.type,
          item_name: item.name,
          item_price: item.price,
          item_image: item.images?.[0] || '',
          enterprise_id: enterprise?.id,
          enterprise_name: enterprise?.business_name
        });
        setIsInWishlist(true);
        toast.success('Ajouté à votre liste de souhaits !');
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

  const handleAddToCart = () => {
    if (item && enterprise) {
      for (let i = 0; i < quantity; i++) {
        addItem(item, enterprise);
      }
      toast.success(`${quantity}x ${item.name} ajouté au panier`);
    }
  };

  const handleShare = () => {
    if (navigator.share) {
      navigator.share({
        title: item?.name,
        text: item?.description,
        url: window.location.href,
      });
    } else {
      navigator.clipboard.writeText(window.location.href);
      toast.success('Lien copié !');
    }
  };

  const getCategoryLabel = (categoryId) => {
    const categories = {
      restauration: 'Restauration',
      soins_esthetiques: 'Soins esthétiques',
      coiffure_barber: 'Coiffure/Barber',
      cours_sport: 'Cours de sport',
      activites_loisirs: 'Loisirs & Événements',
      nettoyage: 'Nettoyage',
      multiservices: 'Multiservices',
      petits_travaux: 'Petits travaux',
      formation: 'Formation',
      sante: 'Santé',
      expert_tech: 'Technologie',
      expert_fiscal: 'Fiscalité',
      expert_juridique: 'Juridique',
      courses_alimentaires: 'Alimentaire',
      vetements_mode: 'Vêtements & Mode',
      maquillage_beaute: 'Beauté',
      sport: 'Sport',
      electronique: 'Électronique',
      ameublement_deco: 'Décoration',
      bricolage_jardinage: 'Bricolage',
    };
    return categories[categoryId] || categoryId;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#050505] pt-24 flex items-center justify-center">
        <div className="w-16 h-16 border-4 border-[#0047AB] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (error || !item) {
    return (
      <div className="min-h-screen bg-[#050505] pt-24 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h1 className="text-2xl font-bold text-white mb-4">Oups !</h1>
          <p className="text-gray-400 mb-8">{error || 'Ce contenu n\'est pas disponible.'}</p>
          <button onClick={() => navigate(-1)} className="btn-primary">
            Retour
          </button>
        </div>
      </div>
    );
  }

  const isService = item.type === 'service';
  const images = item.images?.length > 0 
    ? item.images 
    : ['https://images.unsplash.com/photo-1560066984-138dadb4c035?w=800'];

  return (
    <div className="min-h-screen bg-[#050505] pt-24" data-testid="service-product-detail-page">
      {/* Breadcrumb */}
      <div className="max-w-7xl mx-auto px-4 md:px-8 py-4">
        <div className="flex items-center gap-2 text-sm text-gray-400">
          <Link to="/" className="hover:text-white transition-colors">Accueil</Link>
          <span>/</span>
          <Link to={isService ? '/services' : '/products'} className="hover:text-white transition-colors">
            {isService ? 'Services' : 'Produits'}
          </Link>
          <span>/</span>
          <span className="text-white truncate max-w-[200px]">{item.name}</span>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 md:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-12">
          {/* Images */}
          <div className="space-y-4">
            <div className="aspect-square rounded-2xl overflow-hidden bg-white/5">
              <img 
                src={images[selectedImage]} 
                alt={item.name}
                className="w-full h-full object-cover"
              />
            </div>
            {images.length > 1 && (
              <div className="flex gap-2 overflow-x-auto pb-2">
                {images.map((img, idx) => (
                  <button
                    key={idx}
                    onClick={() => setSelectedImage(idx)}
                    className={`flex-shrink-0 w-20 h-20 rounded-lg overflow-hidden border-2 transition-all ${
                      selectedImage === idx ? 'border-[#0047AB]' : 'border-transparent opacity-60 hover:opacity-100'
                    }`}
                  >
                    <img src={img} alt={`${item.name} ${idx + 1}`} className="w-full h-full object-cover" />
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Details */}
          <div className="space-y-6">
            {/* Category & Type Badge */}
            <div className="flex items-center gap-3">
              <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                isService ? 'bg-[#0047AB]/20 text-[#0047AB]' : 'bg-[#D4AF37]/20 text-[#D4AF37]'
              }`}>
                {isService ? 'Service' : 'Produit'}
              </span>
              <span className="px-3 py-1 rounded-full text-xs font-medium bg-white/10 text-gray-300">
                {getCategoryLabel(item.category)}
              </span>
              {item.is_delivery && (
                <span className="px-3 py-1 rounded-full text-xs font-medium bg-green-500/20 text-green-400 flex items-center gap-1">
                  <Truck className="w-3 h-3" /> Livraison
                </span>
              )}
            </div>

            {/* Title */}
            <h1 className="text-3xl md:text-4xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
              {item.name}
            </h1>

            {/* Enterprise Link */}
           

            {/* Price */}
            <div className="flex items-baseline gap-2">
              <span className="text-4xl font-bold text-white">{item.price?.toFixed(2)}</span>
              <span className="text-xl text-gray-400">CHF</span>
            </div>

            {/* Description */}
            <div className="prose prose-invert max-w-none">
              <p className="text-gray-400 leading-relaxed">{item.description}</p>
            </div>

            {/* Features */}
            <div className="space-y-3">
              <div className="flex items-center gap-3 text-gray-400">
                <Check className="w-5 h-5 text-green-400" />
                <span>Vous recevrez dans l'heure qui suis sur whattsapp ou par email la vidéo selon votre choix</span>
                <span>Pour recevoir par email veuillez noter dans 'information supplémentaires' le mot "email"</span>

              </div>
              {item.is_delivery && (
                <div className="flex items-center gap-3 text-gray-400">
                  <Truck className="w-5 h-5 text-green-400" />
                  <span>Livraison disponible</span>
                </div>
              )}
              {isService && (
                <div className="flex items-center gap-3 text-gray-400">
                  <Clock className="w-5 h-5 text-[#0047AB]" />
                  <span>Sur rendez-vous</span>
                </div>
              )}
            </div>

            {/* Quantity & Add to Cart */}
            <div className="flex flex-col sm:flex-row gap-4 pt-4">
              <div className="flex items-center border border-white/10 rounded-xl overflow-hidden">
                <button 
                  onClick={() => setQuantity(Math.max(1, quantity - 1))}
                  className="px-4 py-3 text-white hover:bg-white/10 transition-colors"
                >
                  -
                </button>
                <span className="px-6 py-3 text-white font-medium bg-white/5">{quantity}</span>
                <button 
                  onClick={() => setQuantity(quantity + 1)}
                  className="px-4 py-3 text-white hover:bg-white/10 transition-colors"
                >
                  +
                </button>
              </div>
              <button 
                onClick={handleAddToCart}
                className="flex-1 btn-primary flex items-center justify-center gap-2"
                data-testid="add-to-cart-btn"
              >
                <ShoppingCart className="w-5 h-5" />
                Ajouter au panier
              </button>
            </div>

            {/* Actions */}
            <div className="flex gap-3 pt-2">
              <button 
                onClick={handleToggleWishlist}
                disabled={wishlistLoading}
                data-testid="wishlist-btn"
                className={`flex items-center gap-2 px-4 py-2 rounded-xl transition-colors ${
                  isInWishlist 
                    ? 'bg-red-500/20 text-red-400 hover:bg-red-500/30' 
                    : 'bg-white/5 text-gray-400 hover:text-white hover:bg-white/10'
                }`}
              >
                <Heart className={`w-5 h-5 ${isInWishlist ? 'fill-red-400' : ''}`} />
                {wishlistLoading ? '...' : isInWishlist ? 'Dans les favoris' : 'Favoris'}
              </button>
              <button 
                onClick={handleShare}
                className="flex items-center gap-2 px-4 py-2 bg-white/5 rounded-xl text-gray-400 hover:text-white hover:bg-white/10 transition-colors"
              >
                <Share2 className="w-5 h-5" />
                Partager
              </button>
            </div>
          </div>
        </div>

        {/* Enterprise Contact */}


        {/* Reviews */}
        {reviews.length > 0 && (
          <div className="mt-16">
            <h2 className="text-2xl font-bold text-white mb-8" style={{ fontFamily: 'Playfair Display, serif' }}>
              Avis clients ({reviews.length})
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {reviews.slice(0, 4).map((review) => (
                <div key={review.id} className="p-6 bg-white/5 rounded-xl text-center">
                  <div className="flex flex-col items-center gap-3 mb-4">
                    <div className="w-12 h-12 bg-gradient-to-br from-[#0047AB] to-[#D4AF37] rounded-full flex items-center justify-center text-white font-bold">
                      {review.user_name?.charAt(0) || 'A'}
                    </div>
                    <div>
                      <p className="text-white font-medium">{review.user_name || 'Anonyme'}</p>
                      <div className="flex items-center justify-center gap-1 mt-1">
                        {[1, 2, 3, 4, 5].map((star) => (
                          <Star 
                            key={star} 
                            className={`w-4 h-4 ${star <= review.rating ? 'text-[#D4AF37] fill-[#D4AF37]' : 'text-gray-600'}`} 
                          />
                        ))}
                      </div>
                    </div>
                  </div>
                  <p className="text-gray-400 text-center">{review.comment}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Related Items */}
        {relatedItems.length > 0 && (
          <div className="mt-16">
            <h2 className="text-2xl font-bold text-white mb-8" style={{ fontFamily: 'Playfair Display, serif' }}>
              Suggéstions pour vous
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              {relatedItems.map((relatedItem) => (
                <Link 
                  key={relatedItem.id} 
                  to={`/${relatedItem.type}/${relatedItem.id}`}
                  className="block bg-white/5 rounded-xl overflow-hidden hover:bg-white/10 transition-all group"
                >
                  <div className="aspect-video overflow-hidden">
                    <img 
                      src={relatedItem.images?.[0] || 'https://images.unsplash.com/photo-1560066984-138dadb4c035?w=400'} 
                      alt={relatedItem.name}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                    />
                  </div>
                  <div className="p-4">
                    <h3 className="text-white font-medium truncate">{relatedItem.name}</h3>
                    <p className="text-[#D4AF37] font-bold mt-1">{relatedItem.price?.toFixed(2)} CHF</p>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ServiceProductDetailPage;
