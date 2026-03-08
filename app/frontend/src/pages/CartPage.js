import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { ShoppingCart, Trash2, Plus, Minus, ArrowLeft, CreditCard, Building2, User, Phone, MapPin, Mail, FileText, AlertCircle } from 'lucide-react';
import { useCart } from '../context/CartContext';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL || 'https://titelliv2back.onrender.com';

const CartPage = () => {
  const { items, removeItem, updateQuantity, clearCart, getTotal, getItemsByEnterprise } = useCart();
  const { isAuthenticated, user } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [loading, setLoading] = useState(false);
  
  // Formulaire checkout complet
  const [checkoutForm, setCheckoutForm] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    delivery_address: '',
    city: '',
    postal_code: '',
    additional_info: '',
    notes: ''
  });
  
  const [formErrors, setFormErrors] = useState({});

  const groupedItems = getItemsByEnterprise();
  const subtotal = getTotal();
  const transactionFee = Math.round(subtotal * 0.029 * 100) / 100; // 2.9%
  const total = Math.round((subtotal + transactionFee) * 100) / 100;

  // Pré-remplir avec les infos utilisateur
  useEffect(() => {
    if (user) {
      setCheckoutForm(prev => ({
        ...prev,
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        email: user.email || '',
        phone: user.phone || ''
      }));
    }
  }, [user]);

  // Vérifier si annulation
  useEffect(() => {
    if (searchParams.get('cancelled') === 'true') {
      toast.error('Paiement annulé');
    }
  }, [searchParams]);

  const validateForm = () => {
    const errors = {};
    
    if (!checkoutForm.first_name.trim()) errors.first_name = 'Prénom requis';
    if (!checkoutForm.last_name.trim()) errors.last_name = 'Nom requis';
    if (!checkoutForm.email.trim()) errors.email = 'Email requis';
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(checkoutForm.email)) errors.email = 'Email invalide';
    if (!checkoutForm.phone.trim()) errors.phone = 'Téléphone requis';
    if (!checkoutForm.delivery_address.trim()) errors.delivery_address = 'Adresse requise';
    if (!checkoutForm.city.trim()) errors.city = 'Ville requise';
    if (!checkoutForm.postal_code.trim()) errors.postal_code = 'Code postal requis';
    
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setCheckoutForm(prev => ({ ...prev, [name]: value }));
    // Effacer l'erreur quand l'utilisateur tape
    if (formErrors[name]) {
      setFormErrors(prev => ({ ...prev, [name]: null }));
    }
  };

  const handleCheckout = async () => {
    if (!isAuthenticated) {
      toast.error('Connectez-vous pour passer commande');
      navigate('/auth');
      return;
    }

    if (items.length === 0) {
      toast.error('Votre panier est vide');
      return;
    }

    if (!validateForm()) {
      toast.error('Veuillez remplir tous les champs obligatoires');
      return;
    }

    setLoading(true);
    
    try {
      const token = localStorage.getItem('titelli_token');
      
      if (!token) {
        toast.error('Session expirée, veuillez vous reconnecter');
        navigate('/auth');
        return;
      }
      
      // Créer une commande par entreprise
      for (const group of groupedItems) {
        const orderData = {
          enterprise_id: group.enterprise_id,
          items: group.items.map(item => ({
            service_product_id: item.id,
            name: item.name,
            price: item.price,
            quantity: item.quantity
          })),
          ...checkoutForm
        };

        const response = await axios.post(`${API_URL}/api/orders/checkout`, orderData, {
          headers: { 
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}` 
          }
        });

        if (response.data.checkout_url) {
          // Vider le panier et rediriger vers Stripe
          clearCart();
          window.location.href = response.data.checkout_url;
          return;
        }
      }

      toast.success('Commande créée avec succès !');
      clearCart();
      navigate('/dashboard/client?tab=orders');
    } catch (error) {
      console.error('Checkout error:', error);
      const errorMsg = error.response?.data?.detail || 'Erreur lors de la commande';
      toast.error(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  if (items.length === 0) {
    return (
      <div className="min-h-screen bg-[#050505] pt-24 px-4" data-testid="cart-page">
        <div className="max-w-4xl mx-auto py-16 text-center">
          <div className="w-24 h-24 bg-white/5 rounded-full flex items-center justify-center mx-auto mb-6">
            <ShoppingCart className="w-12 h-12 text-gray-500" />
          </div>
          <h1 className="text-3xl font-bold text-white mb-4" style={{ fontFamily: 'Playfair Display, serif' }}>
            Votre panier est vide
          </h1>
          <p className="text-gray-400 mb-8">
            Découvrez nos services et produits pour commencer vos achats
          </p>
          <div className="flex gap-4 justify-center">
            <Link to="/services" className="btn-primary">
              Voir les services
            </Link>
            <Link to="/products" className="btn-secondary">
              Voir les produits
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#050505] pt-24 px-4 pb-12" data-testid="cart-page">
      <div className="max-w-7xl mx-auto py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <Link to="/" className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors mb-2">
              <ArrowLeft className="w-4 h-4" />
              Continuer mes achats
            </Link>
            <h1 className="text-3xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
              Finaliser ma commande
            </h1>
          </div>
          <button 
            onClick={clearCart}
            className="text-red-400 hover:text-red-300 text-sm flex items-center gap-2"
          >
            <Trash2 className="w-4 h-4" />
            Vider le panier
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left: Cart Items + Form */}
          <div className="lg:col-span-2 space-y-6">
            
            {/* Cart Items */}
            {groupedItems.map((group) => (
              <div key={group.enterprise_id} className="card-service rounded-xl p-6">
                <div className="flex items-center gap-3 mb-4 pb-4 border-b border-white/10">
                  <Building2 className="w-5 h-5 text-[#0047AB]" />
                  <Link 
                    to={`/entreprise/${group.enterprise_id}`}
                    className="font-semibold text-white hover:text-[#0047AB] transition-colors"
                  >
                    {group.enterprise_name}
                  </Link>
                </div>

                <div className="space-y-4">
                  {group.items.map((item) => (
                    <div key={item.id} className="flex gap-4 p-4 bg-white/5 rounded-xl">
                      <div className="w-20 h-20 rounded-lg bg-white/10 overflow-hidden flex-shrink-0">
                        {item.image ? (
                          <img src={item.image} alt={item.name} className="w-full h-full object-cover" />
                        ) : (
                          <div className="w-full h-full flex items-center justify-center text-gray-500 text-xs">
                            Pas d'image
                          </div>
                        )}
                      </div>

                      <div className="flex-1">
                        <div className="flex justify-between">
                          <div>
                            <h3 className="font-medium text-white">{item.name}</h3>
                            <span className={`text-xs px-2 py-0.5 rounded-full ${
                              item.type === 'service' 
                                ? 'bg-[#0047AB]/20 text-[#0047AB]' 
                                : 'bg-[#D4AF37]/20 text-[#D4AF37]'
                            }`}>
                              {item.type === 'service' ? 'Service' : 'Produit'}
                            </span>
                          </div>
                          <button 
                            onClick={() => removeItem(item.id)}
                            className="text-gray-400 hover:text-red-400 transition-colors"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>

                        <div className="flex items-center justify-between mt-3">
                          <div className="flex items-center gap-2">
                            <button 
                              onClick={() => updateQuantity(item.id, item.quantity - 1)}
                              className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center text-white hover:bg-white/20 transition-colors"
                            >
                              <Minus className="w-4 h-4" />
                            </button>
                            <span className="w-8 text-center text-white font-medium">{item.quantity}</span>
                            <button 
                              onClick={() => updateQuantity(item.id, item.quantity + 1)}
                              className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center text-white hover:bg-white/20 transition-colors"
                            >
                              <Plus className="w-4 h-4" />
                            </button>
                          </div>

                          <p className="text-lg font-bold text-white">
                            {(item.price * item.quantity).toFixed(2)} CHF
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}

            {/* Checkout Form */}
            <div className="card-service rounded-xl p-6">
              <h2 className="text-xl font-semibold text-white mb-6 flex items-center gap-2" style={{ fontFamily: 'Playfair Display, serif' }}>
                <User className="w-5 h-5 text-[#D4AF37]" />
                Informations de livraison
              </h2>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Prénom */}
                <div>
                  <label className="block text-sm text-gray-400 mb-2">
                    Prénom <span className="text-red-400">*</span>
                  </label>
                  <div className="relative">
                    <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                    <input
                      type="text"
                      name="first_name"
                      value={checkoutForm.first_name}
                      onChange={handleInputChange}
                      placeholder="Votre prénom"
                      className={`input-dark w-full pl-10 ${formErrors.first_name ? 'border-red-500' : ''}`}
                      data-testid="checkout-firstname"
                    />
                  </div>
                  {formErrors.first_name && (
                    <p className="text-red-400 text-xs mt-1 flex items-center gap-1">
                      <AlertCircle className="w-3 h-3" /> {formErrors.first_name}
                    </p>
                  )}
                </div>

                {/* Nom */}
                <div>
                  <label className="block text-sm text-gray-400 mb-2">
                    Nom <span className="text-red-400">*</span>
                  </label>
                  <input
                    type="text"
                    name="last_name"
                    value={checkoutForm.last_name}
                    onChange={handleInputChange}
                    placeholder="Votre nom"
                    className={`input-dark w-full ${formErrors.last_name ? 'border-red-500' : ''}`}
                    data-testid="checkout-lastname"
                  />
                  {formErrors.last_name && (
                    <p className="text-red-400 text-xs mt-1 flex items-center gap-1">
                      <AlertCircle className="w-3 h-3" /> {formErrors.last_name}
                    </p>
                  )}
                </div>

                {/* Email */}
                <div>
                  <label className="block text-sm text-gray-400 mb-2">
                    Email <span className="text-red-400">*</span>
                  </label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                    <input
                      type="email"
                      name="email"
                      value={checkoutForm.email}
                      onChange={handleInputChange}
                      placeholder="votre@email.com"
                      className={`input-dark w-full pl-10 ${formErrors.email ? 'border-red-500' : ''}`}
                      data-testid="checkout-email"
                    />
                  </div>
                  {formErrors.email && (
                    <p className="text-red-400 text-xs mt-1 flex items-center gap-1">
                      <AlertCircle className="w-3 h-3" /> {formErrors.email}
                    </p>
                  )}
                </div>

                {/* Téléphone */}
                <div>
                  <label className="block text-sm text-gray-400 mb-2">
                    Téléphone <span className="text-red-400">*</span>
                  </label>
                  <div className="relative">
                    <Phone className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                    <input
                      type="tel"
                      name="phone"
                      value={checkoutForm.phone}
                      onChange={handleInputChange}
                      placeholder="+41 79 123 45 67"
                      className={`input-dark w-full pl-10 ${formErrors.phone ? 'border-red-500' : ''}`}
                      data-testid="checkout-phone"
                    />
                  </div>
                  {formErrors.phone && (
                    <p className="text-red-400 text-xs mt-1 flex items-center gap-1">
                      <AlertCircle className="w-3 h-3" /> {formErrors.phone}
                    </p>
                  )}
                </div>

                {/* Adresse */}
                <div className="md:col-span-2">
                  <label className="block text-sm text-gray-400 mb-2">
                    Adresse de livraison <span className="text-red-400">*</span>
                  </label>
                  <div className="relative">
                    <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                    <input
                      type="text"
                      name="delivery_address"
                      value={checkoutForm.delivery_address}
                      onChange={handleInputChange}
                      placeholder="Rue et numéro"
                      className={`input-dark w-full pl-10 ${formErrors.delivery_address ? 'border-red-500' : ''}`}
                      data-testid="checkout-address"
                    />
                  </div>
                  {formErrors.delivery_address && (
                    <p className="text-red-400 text-xs mt-1 flex items-center gap-1">
                      <AlertCircle className="w-3 h-3" /> {formErrors.delivery_address}
                    </p>
                  )}
                </div>

                {/* Code postal */}
                <div>
                  <label className="block text-sm text-gray-400 mb-2">
                    Code postal <span className="text-red-400">*</span>
                  </label>
                  <input
                    type="text"
                    name="postal_code"
                    value={checkoutForm.postal_code}
                    onChange={handleInputChange}
                    placeholder="1000"
                    className={`input-dark w-full ${formErrors.postal_code ? 'border-red-500' : ''}`}
                    data-testid="checkout-postalcode"
                  />
                  {formErrors.postal_code && (
                    <p className="text-red-400 text-xs mt-1 flex items-center gap-1">
                      <AlertCircle className="w-3 h-3" /> {formErrors.postal_code}
                    </p>
                  )}
                </div>

                {/* Ville */}
                <div>
                  <label className="block text-sm text-gray-400 mb-2">
                    Ville <span className="text-red-400">*</span>
                  </label>
                  <input
                    type="text"
                    name="city"
                    value={checkoutForm.city}
                    onChange={handleInputChange}
                    placeholder="Lausanne"
                    className={`input-dark w-full ${formErrors.city ? 'border-red-500' : ''}`}
                    data-testid="checkout-city"
                  />
                  {formErrors.city && (
                    <p className="text-red-400 text-xs mt-1 flex items-center gap-1">
                      <AlertCircle className="w-3 h-3" /> {formErrors.city}
                    </p>
                  )}
                </div>

                {/* Infos supplémentaires */}
                <div className="md:col-span-2">
                  <label className="block text-sm text-gray-400 mb-2">
                    Informations supplémentaires
                  </label>
                  <textarea
                    name="additional_info"
                    value={checkoutForm.additional_info}
                    onChange={handleInputChange}
                    placeholder="Appartement, étage, code d'entrée..."
                    className="input-dark w-full h-20 resize-none"
                    data-testid="checkout-additional"
                  />
                </div>

                {/* Notes */}
                <div className="md:col-span-2">
                  <label className="block text-sm text-gray-400 mb-2">
                    <FileText className="w-4 h-4 inline mr-1" />
                    Instructions spéciales
                  </label>
                  <textarea
                    name="notes"
                    value={checkoutForm.notes}
                    onChange={handleInputChange}
                    placeholder="Instructions pour la livraison ou remarques..."
                    className="input-dark w-full h-20 resize-none"
                    data-testid="checkout-notes"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Right: Order Summary */}
          <div className="lg:col-span-1">
            <div className="card-service rounded-xl p-6 sticky top-24">
              <h2 className="text-xl font-semibold text-white mb-6" style={{ fontFamily: 'Playfair Display, serif' }}>
                Récapitulatif
              </h2>

              {/* Items summary */}
              <div className="space-y-2 mb-6 pb-6 border-b border-white/10">
                {items.map((item) => (
                  <div key={item.id} className="flex justify-between text-sm">
                    <span className="text-gray-400">{item.name} x{item.quantity}</span>
                    <span className="text-white">{(item.price * item.quantity).toFixed(2)} CHF</span>
                  </div>
                ))}
              </div>

              {/* Price Breakdown */}
              <div className="space-y-3 mb-6 pb-6 border-b border-white/10">
                <div className="flex justify-between text-gray-400">
                  <span>Sous-total</span>
                  <span>{subtotal.toFixed(2)} CHF</span>
                </div>
                <div className="flex justify-between text-gray-400">
                  <span>Frais de service (2.9%)</span>
                  <span>{transactionFee.toFixed(2)} CHF</span>
                </div>
              </div>

              {/* Total */}
              <div className="flex justify-between mb-6">
                <span className="text-lg font-semibold text-white">Total</span>
                <span className="text-2xl font-bold text-[#D4AF37]">{total.toFixed(2)} CHF</span>
              </div>

              {/* Checkout Button */}
              <button
                onClick={handleCheckout}
                disabled={loading}
                className="btn-primary w-full py-4 flex items-center justify-center gap-2 text-lg"
                data-testid="checkout-btn"
              >
                {loading ? (
                  <div className="w-6 h-6 border-2 border-black border-t-transparent rounded-full animate-spin" />
                ) : (
                  <>
                    <CreditCard className="w-5 h-5" />
                    Payer {total.toFixed(2)} CHF
                  </>
                )}
              </button>

              {/* Security note */}
              <div className="mt-4 p-3 bg-white/5 rounded-lg">
                <p className="text-xs text-gray-400 text-center flex items-center justify-center gap-2">
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd" />
                  </svg>
                  Paiement sécurisé par Stripe
                </p>
              </div>

              {/* Accepted cards */}
              <div className="mt-3 flex items-center justify-center gap-2">
                <img src="https://js.stripe.com/v3/fingerprinted/img/visa-729c05c240c4bdb47b03ac81d9945bfe.svg" alt="Visa" className="h-6" />
                <img src="https://js.stripe.com/v3/fingerprinted/img/mastercard-4d8844094130711885b5e41b28c9848f.svg" alt="Mastercard" className="h-6" />
                <img src="https://js.stripe.com/v3/fingerprinted/img/amex-a49b82f46c5cd6a96a6e418a6ca1717c.svg" alt="Amex" className="h-6" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CartPage;
