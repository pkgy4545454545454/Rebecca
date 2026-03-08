import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams, useLocation } from 'react-router-dom';
import { 
  Video, 
  Sparkles, 
  ShoppingCart, 
  Check, 
  ArrowRight, 
  ArrowLeft,
  Palette,
  Type,
  Clock,
  Star,
  Filter,
  Grid,
  List,
  Eye,
  Download,
  Play,
  Pause,
  CreditCard,
  Wand2,
  ChevronRight,
  ExternalLink,
  AlertCircle,
  CheckCircle2,
  Lock,
  Film,
  Loader2
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Animated Header
const AnimatedHeader = () => (
  <div className="relative overflow-hidden bg-gradient-to-r from-purple-900 via-violet-800 to-indigo-900 py-16 mb-8">
    <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmYiIGZpbGwtb3BhY2l0eT0iMC4wNSI+PGNpcmNsZSBjeD0iMzAiIGN5PSIzMCIgcj0iMiIvPjwvZz48L2c+PC9zdmc+')] opacity-50"></div>
    
    <div className="container mx-auto px-4 relative z-10">
      <div className="flex flex-col md:flex-row items-center justify-between gap-8">
        <div className="text-center md:text-left">
          <div className="inline-flex items-center gap-2 bg-white/10 backdrop-blur-sm px-4 py-2 rounded-full mb-4">
            <Film className="w-5 h-5 text-violet-300" />
            <span className="text-violet-200 text-sm font-medium">Vidéo Pub IA</span>
          </div>
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4" style={{ fontFamily: 'Playfair Display, serif' }}>
            Commandez des Vidéos
            <span className="text-violet-400 block mt-2">Professionnelles</span>
          </h1>
          <p className="text-violet-200 text-lg max-w-xl">
            Commandez des vidéos publicitaires uniques avec l&apos;intelligence artificielle Titelli
          </p>
        </div>
        
        <div className="flex items-center gap-4">
          <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 text-center">
            <Video className="w-10 h-10 text-violet-300 mx-auto mb-2" />
            <p className="text-white font-bold text-2xl">15-30s</p>
            <p className="text-violet-300 text-sm">Durée vidéo</p>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 text-center">
            <Clock className="w-10 h-10 text-violet-300 mx-auto mb-2" />
            <p className="text-white font-bold text-2xl">~1h</p>
            <p className="text-violet-300 text-sm">Livraison</p>
          </div>
        </div>
      </div>
    </div>
    
    {/* Animated elements */}
    <div className="absolute top-10 left-10 w-20 h-20 bg-violet-500/20 rounded-full blur-xl animate-pulse"></div>
    <div className="absolute bottom-10 right-10 w-32 h-32 bg-indigo-500/20 rounded-full blur-xl animate-pulse delay-1000"></div>
  </div>
);

const VideoPubPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [searchParams] = useSearchParams();
  const enterpriseId = searchParams.get('enterprise_id');
  const sessionId = searchParams.get('session_id');
  const orderId = searchParams.get('order_id');
  const cancelled = searchParams.get('cancelled');
  
  const [templates, setTemplates] = useState([]);
  const [categories, setCategories] = useState([]);
  const [byCategory, setByCategory] = useState({});
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [viewMode, setViewMode] = useState('grid');
  const [loading, setLoading] = useState(true);
  const [orderStep, setOrderStep] = useState('browse');
  const [paymentError, setPaymentError] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [orderResult, setOrderResult] = useState(null);
  
  // Form data
  const [formData, setFormData] = useState({
    product_name: '',
    slogan: '',
    description: '',
    style: 'moderne et élégant',
    brand_colors: ['#8B5CF6', '#FFFFFF'],
    custom_prompt: '',
    additional_notes: ''
  });

  useEffect(() => {
    fetchTemplates();
  }, []);

  // Check payment status when returning from Stripe
  useEffect(() => {
    if (sessionId && orderId) {
      setOrderStep('payment_verification');
      pollPaymentStatus(sessionId, orderId);
    } else if (cancelled && orderId) {
      setPaymentError('Paiement annulé. Vous pouvez réessayer.');
      setOrderStep('browse');
    }
  }, [sessionId, orderId, cancelled]);

  const fetchTemplates = async () => {
    try {
      const response = await fetch(`${API_URL}/api/video-pub/templates`);
      const data = await response.json();
      setTemplates(data.templates || []);
      setCategories(data.categories || []);
      setByCategory(data.by_category || {});
    } catch (error) {
      console.error('Error fetching templates:', error);
    } finally {
      setLoading(false);
    }
  };

  const pollPaymentStatus = async (checkoutSessionId, orderIdParam, attempts = 0) => {
    const maxAttempts = 10;
    const pollInterval = 2000;

    if (attempts >= maxAttempts) {
      setPaymentError('Vérification du paiement expirée.');
      setOrderStep('browse');
      return;
    }

    try {
      const response = await fetch(
        `${API_URL}/api/video-pub/payment/status/${checkoutSessionId}?order_id=${orderIdParam}`
      );
      const data = await response.json();

      if (data.status === 'paid') {
        setOrderResult({ id: orderIdParam, status: 'generating' });
        setOrderStep('payment_success');
        window.history.replaceState({}, '', '/video-pub');
        return;
      }

      setTimeout(() => pollPaymentStatus(checkoutSessionId, orderIdParam, attempts + 1), pollInterval);
    } catch (error) {
      if (attempts < maxAttempts - 1) {
        setTimeout(() => pollPaymentStatus(checkoutSessionId, orderIdParam, attempts + 1), pollInterval);
      } else {
        setPaymentError('Erreur lors de la vérification.');
        setOrderStep('browse');
      }
    }
  };

  const handleSelectTemplate = (template) => {
    setSelectedTemplate(template);
    setFormData({
      ...formData,
      product_name: '',
      slogan: '',
      description: ''
    });
    setOrderStep(template.id === 'sur_mesure' ? 'sur_mesure' : 'customize');
  };

  const handlePayment = async () => {
    setSubmitting(true);
    setPaymentError(null);
    
    try {
      // Create order
      const orderData = {
        template_id: selectedTemplate.id,
        enterprise_id: enterpriseId || 'demo-enterprise',
        product_name: formData.product_name,
        slogan: formData.slogan,
        description: formData.description,
        style: formData.style,
        brand_colors: formData.brand_colors,
        custom_prompt: formData.custom_prompt,
        additional_notes: formData.additional_notes
      };

      const orderResponse = await fetch(`${API_URL}/api/video-pub/orders`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(orderData)
      });

      if (!orderResponse.ok) {
        throw new Error('Erreur création commande');
      }

      const orderResult = await orderResponse.json();

      // Create Stripe session
      const paymentResponse = await fetch(`${API_URL}/api/video-pub/payment/create-session`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          order_id: orderResult.id,
          origin_url: window.location.origin
        })
      });

      if (!paymentResponse.ok) {
        throw new Error('Erreur session paiement');
      }

      const paymentData = await paymentResponse.json();
      
      if (paymentData.checkout_url) {
        window.location.href = paymentData.checkout_url;
      }

    } catch (error) {
      console.error('Payment error:', error);
      setPaymentError(error.message);
      setSubmitting(false);
    }
  };

  const filteredTemplates = selectedCategory === 'all' 
    ? templates 
    : templates.filter(t => t.category === selectedCategory);

  // Browse Step
  const renderBrowseStep = () => (
    <div>
      {/* Category Filter */}
      <div className="flex flex-wrap gap-2 mb-8">
        <button
          onClick={() => setSelectedCategory('all')}
          className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
            selectedCategory === 'all'
              ? 'bg-violet-500 text-white'
              : 'bg-white/10 text-gray-300 hover:bg-white/20'
          }`}
        >
          Tous ({templates.length})
        </button>
        {categories.map(cat => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
              selectedCategory === cat
                ? 'bg-violet-500 text-white'
                : 'bg-white/10 text-gray-300 hover:bg-white/20'
            }`}
          >
            {cat} ({byCategory[cat]?.length || 0})
          </button>
        ))}
      </div>

      {/* Templates Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {filteredTemplates.map(template => (
          <div
            key={template.id}
            onClick={() => handleSelectTemplate(template)}
            data-testid={`template-${template.id}`}
            className="group bg-white/5 border border-white/10 rounded-2xl overflow-hidden cursor-pointer hover:border-violet-500/50 transition-all hover:scale-[1.02]"
          >
            <div className="relative aspect-video">
              <img
                src={template.preview_image}
                alt={template.name}
                className="w-full h-full object-cover"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent" />
              
              {/* Play icon overlay */}
              <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                <div className="w-16 h-16 bg-violet-500/80 rounded-full flex items-center justify-center">
                  <Play className="w-8 h-8 text-white ml-1" />
                </div>
              </div>
              
              {/* Duration badge */}
              <div className="absolute top-3 right-3 bg-black/60 px-2 py-1 rounded-full flex items-center gap-1">
                <Clock className="w-3 h-3 text-violet-400" />
                <span className="text-xs text-white">{template.duration}s</span>
              </div>
              
              {/* Category badge */}
              <div className="absolute top-3 left-3 bg-violet-500/80 px-2 py-1 rounded-full">
                <span className="text-xs text-white">{template.subcategory}</span>
              </div>
              
              {/* Info at bottom */}
              <div className="absolute bottom-0 left-0 right-0 p-4">
                <h3 className="font-semibold text-white mb-1">{template.name}</h3>
                <p className="text-sm text-gray-300 line-clamp-1">{template.description}</p>
              </div>
            </div>
            
            <div className="p-4 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Video className="w-4 h-4 text-violet-400" />
                <span className="text-gray-400 text-sm">{template.size}</span>
              </div>
              <span className="text-violet-400 font-bold">{template.price} CHF</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  // Customize Step
  const renderCustomizeStep = () => (
    <div className="max-w-4xl mx-auto">
      <button
        onClick={() => {
          setSelectedTemplate(null);
          setOrderStep('browse');
        }}
        className="flex items-center gap-2 text-gray-400 hover:text-white mb-6 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        Retour aux templates
      </button>

      <div className="grid lg:grid-cols-2 gap-8">
        {/* Preview */}
        <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <Eye className="w-5 h-5 text-violet-400" />
            Aperçu du template
          </h3>
          
          <div className="relative aspect-video rounded-xl overflow-hidden mb-4">
            <img
              src={selectedTemplate?.preview_image}
              alt={selectedTemplate?.name}
              className="w-full h-full object-cover"
            />
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-20 h-20 bg-violet-500/80 rounded-full flex items-center justify-center">
                <Play className="w-10 h-10 text-white ml-1" />
              </div>
            </div>
          </div>
          
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-400">Template</span>
              <span className="text-white">{selectedTemplate?.name}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Durée</span>
              <span className="text-white">{selectedTemplate?.duration} secondes</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Format</span>
              <span className="text-white">{selectedTemplate?.size}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Temps de génération</span>
              <span className="text-violet-400">~1 heure</span>
            </div>
          </div>
        </div>

        {/* Form */}
        <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <Wand2 className="w-5 h-5 text-violet-400" />
            Personnalisation
          </h3>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-gray-400 mb-2">Nom du produit/service *</label>
              <input
                type="text"
                name="product_name"
                value={formData.product_name}
                onChange={(e) => setFormData({...formData, product_name: e.target.value})}
                placeholder="Ex: Restaurant Le Gourmet"
                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-violet-500"
              />
            </div>
            
            <div>
              <label className="block text-sm text-gray-400 mb-2">Slogan / Message principal</label>
              <input
                type="text"
                name="slogan"
                value={formData.slogan}
                onChange={(e) => setFormData({...formData, slogan: e.target.value})}
                placeholder="Ex: L'excellence culinaire"
                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-violet-500"
              />
            </div>
            
            <div>
              <label className="block text-sm text-gray-400 mb-2">Style visuel</label>
              <select
                value={formData.style}
                onChange={(e) => setFormData({...formData, style: e.target.value})}
                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-violet-500"
              >
                <option value="moderne et élégant">Moderne et élégant</option>
                <option value="dynamique et énergique">Dynamique et énergique</option>
                <option value="luxueux et sophistiqué">Luxueux et sophistiqué</option>
                <option value="chaleureux et accueillant">Chaleureux et accueillant</option>
                <option value="minimaliste et épuré">Minimaliste et épuré</option>
                <option value="créatif et artistique">Créatif et artistique</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm text-gray-400 mb-2">Couleurs de marque</label>
              <div className="flex gap-4">
                <div className="flex items-center gap-2">
                  <input
                    type="color"
                    value={formData.brand_colors[0]}
                    onChange={(e) => setFormData({...formData, brand_colors: [e.target.value, formData.brand_colors[1]]})}
                    className="w-10 h-10 rounded cursor-pointer"
                  />
                  <span className="text-sm text-gray-400">Principale</span>
                </div>
                <div className="flex items-center gap-2">
                  <input
                    type="color"
                    value={formData.brand_colors[1]}
                    onChange={(e) => setFormData({...formData, brand_colors: [formData.brand_colors[0], e.target.value]})}
                    className="w-10 h-10 rounded cursor-pointer"
                  />
                  <span className="text-sm text-gray-400">Secondaire</span>
                </div>
              </div>
            </div>
            
            <div>
              <label className="block text-sm text-gray-400 mb-2">Notes additionnelles</label>
              <textarea
                value={formData.additional_notes}
                onChange={(e) => setFormData({...formData, additional_notes: e.target.value})}
                placeholder="Instructions spéciales pour la vidéo..."
                rows={3}
                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-violet-500 resize-none"
              />
            </div>
          </div>

          {/* Price and CTA */}
          <div className="mt-6 pt-6 border-t border-white/10">
            <div className="flex items-center justify-between mb-4">
              <span className="text-gray-400">Prix total</span>
              <span className="text-2xl font-bold text-violet-400">{selectedTemplate?.price} CHF</span>
            </div>
            
            <div className="bg-violet-900/30 border border-violet-700/50 rounded-lg p-3 mb-4">
              <div className="flex items-center gap-2 text-violet-300 text-sm">
                <Clock className="w-4 h-4" />
                <span>Temps de génération estimé: <strong>~1 heure</strong></span>
              </div>
            </div>

            <button
              onClick={handlePayment}
              disabled={!formData.product_name || submitting}
              className="w-full py-4 bg-gradient-to-r from-violet-600 to-purple-600 hover:from-violet-700 hover:to-purple-700 text-white font-bold rounded-xl flex items-center justify-center gap-2 disabled:opacity-50 transition-all"
              data-testid="proceed-to-payment"
            >
              {submitting ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Redirection vers Stripe...
                </>
              ) : (
                <>
                  <ExternalLink className="w-5 h-5" />
                  Payer {selectedTemplate?.price} CHF
                </>
              )}
            </button>
            
            <p className="text-center text-xs text-gray-500 mt-3 flex items-center justify-center gap-1">
              <Lock className="w-3 h-3" />
              Paiement sécurisé par Stripe
            </p>
          </div>
        </div>
      </div>
    </div>
  );

  // Sur Mesure Step
  const renderSurMesureStep = () => (
    <div className="max-w-2xl mx-auto">
      <button
        onClick={() => {
          setSelectedTemplate(null);
          setOrderStep('browse');
        }}
        className="flex items-center gap-2 text-gray-400 hover:text-white mb-6"
      >
        <ArrowLeft className="w-4 h-4" />
        Retour
      </button>

      <div className="bg-gradient-to-br from-violet-900/50 to-purple-900/50 border border-violet-500/30 rounded-2xl p-8">
        <div className="text-center mb-8">
          <div className="w-16 h-16 mx-auto mb-4 bg-violet-500/20 rounded-full flex items-center justify-center">
            <Wand2 className="w-8 h-8 text-violet-400" />
          </div>
          <h2 className="text-2xl font-bold text-white mb-2">Création Sur Mesure</h2>
          <p className="text-violet-200">Décrivez votre vidéo idéale et notre IA la créera pour vous</p>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm text-violet-300 mb-2">Nom du projet *</label>
            <input
              type="text"
              value={formData.product_name}
              onChange={(e) => setFormData({...formData, product_name: e.target.value})}
              placeholder="Ex: Vidéo anniversaire entreprise"
              className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-violet-500"
            />
          </div>

          <div>
            <label className="block text-sm text-violet-300 mb-2">Description détaillée de la vidéo *</label>
            <textarea
              value={formData.custom_prompt}
              onChange={(e) => setFormData({...formData, custom_prompt: e.target.value})}
              placeholder="Décrivez en détail ce que vous souhaitez voir dans la vidéo: scènes, ambiance, style, mouvements de caméra..."
              rows={6}
              className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-violet-500 resize-none"
            />
          </div>

          <div>
            <label className="block text-sm text-violet-300 mb-2">Style visuel souhaité</label>
            <input
              type="text"
              value={formData.style}
              onChange={(e) => setFormData({...formData, style: e.target.value})}
              placeholder="Ex: Cinématique, énergique, minimaliste..."
              className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-violet-500"
            />
          </div>
        </div>

        <div className="mt-8 pt-6 border-t border-violet-500/30">
          <div className="flex items-center justify-between mb-4">
            <span className="text-violet-300">Prix création sur mesure</span>
            <span className="text-3xl font-bold text-white">399.90 CHF</span>
          </div>
          
          <div className="bg-white/5 rounded-lg p-3 mb-4 text-sm text-violet-200">
            <p>✓ Vidéo 15 secondes HD</p>
            <p>✓ Format et style personnalisés</p>
            <p>✓ Livraison sous ~1 heure</p>
          </div>

          <button
            onClick={handlePayment}
            disabled={!formData.product_name || !formData.custom_prompt || submitting}
            className="w-full py-4 bg-gradient-to-r from-violet-600 to-purple-600 hover:from-violet-700 hover:to-purple-700 text-white font-bold rounded-xl flex items-center justify-center gap-2 disabled:opacity-50"
          >
            {submitting ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Redirection...
              </>
            ) : (
              <>
                <CreditCard className="w-5 h-5" />
                Commander 399.90 CHF
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );

  // Payment Verification
  const renderPaymentVerification = () => (
    <div className="max-w-md mx-auto text-center py-12">
      <div className="w-24 h-24 mx-auto mb-6 relative">
        <div className="absolute inset-0 border-4 border-violet-500/30 rounded-full"></div>
        <div className="absolute inset-0 border-4 border-violet-500 border-t-transparent rounded-full animate-spin"></div>
        <CreditCard className="absolute inset-0 m-auto w-10 h-10 text-violet-400" />
      </div>
      <h2 className="text-2xl font-bold text-white mb-2">Vérification du paiement...</h2>
      <p className="text-gray-400">Veuillez patienter</p>
    </div>
  );

  // Payment Success
  const renderPaymentSuccess = () => (
    <div className="max-w-md mx-auto text-center py-12">
      <div className="w-20 h-20 mx-auto mb-6 bg-green-500/20 rounded-full flex items-center justify-center">
        <CheckCircle2 className="w-10 h-10 text-green-400" />
      </div>
      <h2 className="text-2xl font-bold text-white mb-2">Paiement réussi !</h2>
      <p className="text-gray-400 mb-6">
        Votre vidéo est en cours de génération.<br/>
        <strong className="text-violet-400">Temps estimé: ~1 heure</strong>
      </p>
      
      {orderResult && (
        <div className="bg-gray-800/50 rounded-xl p-4 mb-6 text-left">
          <p className="text-sm text-gray-400">
            <span className="text-gray-500">N° commande:</span> {orderResult.id}
          </p>
          <p className="text-sm text-gray-400">
            <span className="text-gray-500">Statut:</span> 
            <span className="text-violet-400 ml-1">Génération en cours</span>
          </p>
        </div>
      )}

      <div className="flex flex-col gap-3">
        <button
          onClick={() => navigate('/dashboard/entreprise?tab=videos-titelli')}
          className="w-full py-3 bg-violet-600 hover:bg-violet-700 text-white font-medium rounded-lg transition-colors flex items-center justify-center gap-2"
        >
          <Video className="w-4 h-4" />
          Voir mes vidéos
        </button>
        <button
          onClick={() => {
            setOrderStep('browse');
            setSelectedTemplate(null);
          }}
          className="w-full py-3 bg-gray-700 hover:bg-gray-600 text-white font-medium rounded-lg"
        >
          Commander une autre vidéo
        </button>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="animate-spin w-12 h-12 border-4 border-violet-500 border-t-transparent rounded-full"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 via-gray-800 to-gray-900 text-white">
      {orderStep === 'browse' && <AnimatedHeader />}
      
      <div className="container mx-auto px-4 py-8">
        {paymentError && (
          <div className="max-w-lg mx-auto mb-6 bg-red-900/30 border border-red-700/50 rounded-xl p-4 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-400 mt-0.5" />
            <div>
              <p className="text-red-400">{paymentError}</p>
              <button onClick={() => setPaymentError(null)} className="text-sm text-red-400 mt-1">Fermer</button>
            </div>
          </div>
        )}
        
        {orderStep === 'browse' && renderBrowseStep()}
        {orderStep === 'customize' && renderCustomizeStep()}
        {orderStep === 'sur_mesure' && renderSurMesureStep()}
        {orderStep === 'payment_verification' && renderPaymentVerification()}
        {orderStep === 'payment_success' && renderPaymentSuccess()}
      </div>
    </div>
  );
};

export default VideoPubPage;
