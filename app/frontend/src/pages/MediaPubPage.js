import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate, useSearchParams, useLocation } from 'react-router-dom';
import { 
  Image, 
  Sparkles, 
  ShoppingCart, 
  Check, 
  ArrowRight, 
  ArrowLeft,
  Palette,
  Type,
  FileText,
  Clock,
  Star,
  Filter,
  Grid,
  List,
  Eye,
  Download,
  Layers,
  ZoomIn,
  ZoomOut,
  RotateCcw,
  Lock,
  Unlock,
  Bold,
  Italic,
  AlignLeft,
  AlignCenter,
  AlignRight,
  CreditCard,
  Wand2,
  Settings,
  Copy,
  MousePointer,
  Trash2,
  Plus,
  Play,
  ChevronRight,
  ExternalLink,
  AlertCircle,
  CheckCircle2
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Images de pubs pour le header animé
const SAMPLE_ADS = [
  "https://images.unsplash.com/photo-1557804506-669a67965ba0?w=300&h=400&fit=crop",
  "https://images.unsplash.com/photo-1607083206869-4c7672e72a8a?w=300&h=400&fit=crop",
  "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=300&h=400&fit=crop",
  "https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=300&h=400&fit=crop",
  "https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=300&h=400&fit=crop",
  "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=300&h=400&fit=crop",
  "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=300&h=400&fit=crop",
  "https://images.unsplash.com/photo-1611532736597-de2d4265fba3?w=300&h=400&fit=crop",
];

// Header animé avec défilement de pubs
const AnimatedHeader = () => {
  return (
    <div className="relative overflow-hidden bg-gradient-to-b from-gray-900 via-gray-800 to-transparent py-12 mb-8">
      {/* Overlay gradient */}
      <div className="absolute inset-0 bg-gradient-to-r from-gray-900 via-transparent to-gray-900 z-10" />
      
      {/* Animated ads row 1 - scrolling left */}
      <div className="flex gap-4 mb-4 animate-scroll-left">
        {[...SAMPLE_ADS, ...SAMPLE_ADS, ...SAMPLE_ADS].map((src, i) => (
          <div 
            key={`row1-${i}`}
            className="flex-shrink-0 w-48 h-64 rounded-xl overflow-hidden shadow-2xl transform hover:scale-105 transition-transform"
            style={{ 
              transform: `rotate(${(i % 5 - 2) * 3}deg)`,
              opacity: 0.8 
            }}
          >
            <img src={src} alt="" className="w-full h-full object-cover" />
          </div>
        ))}
      </div>
      
      {/* Animated ads row 2 - scrolling right */}
      <div className="flex gap-4 animate-scroll-right">
        {[...SAMPLE_ADS.reverse(), ...SAMPLE_ADS, ...SAMPLE_ADS].map((src, i) => (
          <div 
            key={`row2-${i}`}
            className="flex-shrink-0 w-48 h-64 rounded-xl overflow-hidden shadow-2xl transform hover:scale-105 transition-transform"
            style={{ 
              transform: `rotate(${(i % 5 - 2) * -3}deg)`,
              opacity: 0.7 
            }}
          >
            <img src={src} alt="" className="w-full h-full object-cover" />
          </div>
        ))}
      </div>
      
      {/* Title overlay */}
      <div className="absolute inset-0 flex flex-col items-center justify-center z-20">
        <div className="bg-black/60 backdrop-blur-sm px-12 py-8 rounded-2xl text-center">
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="w-12 h-12 rounded-full bg-gradient-to-r from-yellow-400 to-orange-500 flex items-center justify-center">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <h1 className="text-4xl font-bold text-white">
              Commande Pub Média
            </h1>
          </div>
          <p className="text-gray-300 text-lg max-w-xl">
            Créez vos publicités professionnelles avec l'intelligence artificielle Titelli
          </p>
          <div className="flex items-center justify-center gap-6 mt-6 text-sm text-gray-400">
            <span className="flex items-center gap-2">
              <Check className="w-4 h-4 text-green-400" />
              Génération IA
            </span>
            <span className="flex items-center gap-2">
              <Check className="w-4 h-4 text-green-400" />
              Haute qualité
            </span>
            <span className="flex items-center gap-2">
              <Check className="w-4 h-4 text-green-400" />
              Livraison rapide
            </span>
          </div>
        </div>
      </div>

      {/* CSS for animation */}
      <style>{`
        @keyframes scroll-left {
          0% { transform: translateX(0); }
          100% { transform: translateX(-50%); }
        }
        @keyframes scroll-right {
          0% { transform: translateX(-50%); }
          100% { transform: translateX(0); }
        }
        .animate-scroll-left {
          animation: scroll-left 40s linear infinite;
        }
        .animate-scroll-right {
          animation: scroll-right 45s linear infinite;
        }
      `}</style>
    </div>
  );
};

// Élément draggable sur le canvas
const DraggableElement = ({ element, isSelected, onSelect, onUpdate, onDelete }) => {
  const elementRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });

  const handleMouseDown = (e) => {
    if (element.locked) return;
    e.stopPropagation();
    onSelect(element.id);
    setIsDragging(true);
    const rect = elementRef.current.getBoundingClientRect();
    setDragOffset({
      x: e.clientX - rect.left,
      y: e.clientY - rect.top
    });
  };

  const handleMouseMove = useCallback((e) => {
    if (!isDragging || element.locked) return;
    const parent = elementRef.current.parentElement;
    const parentRect = parent.getBoundingClientRect();
    const newX = e.clientX - parentRect.left - dragOffset.x;
    const newY = e.clientY - parentRect.top - dragOffset.y;
    onUpdate(element.id, { x: Math.max(0, newX), y: Math.max(0, newY) });
  }, [isDragging, dragOffset, element.id, element.locked, onUpdate]);

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  useEffect(() => {
    if (isDragging) {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
      return () => {
        window.removeEventListener('mousemove', handleMouseMove);
        window.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [isDragging, handleMouseMove, handleMouseUp]);

  const style = {
    position: 'absolute',
    left: element.x,
    top: element.y,
    cursor: element.locked ? 'not-allowed' : (isDragging ? 'grabbing' : 'grab'),
    userSelect: 'none',
    zIndex: isSelected ? 100 : element.zIndex || 1,
    border: isSelected ? '2px dashed #F59E0B' : 'none',
    padding: '4px',
    borderRadius: '4px',
    backgroundColor: isSelected ? 'rgba(245, 158, 11, 0.1)' : 'transparent'
  };

  const textStyle = {
    fontSize: element.fontSize || 24,
    fontWeight: element.fontWeight || 'bold',
    fontStyle: element.fontStyle || 'normal',
    textAlign: element.textAlign || 'center',
    color: element.color || '#FFFFFF',
    textShadow: '2px 2px 4px rgba(0,0,0,0.8)',
    whiteSpace: 'nowrap',
    maxWidth: '400px',
    overflow: 'hidden',
    textOverflow: 'ellipsis'
  };

  return (
    <div
      ref={elementRef}
      style={style}
      onMouseDown={handleMouseDown}
      data-testid={`canvas-element-${element.id}`}
    >
      <div style={textStyle}>
        {element.text || element.content}
      </div>
      {element.locked && (
        <Lock className="absolute -top-2 -right-2 w-4 h-4 text-yellow-400" />
      )}
    </div>
  );
};

const MediaPubPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [searchParams] = useSearchParams();
  const enterpriseId = searchParams.get('enterprise_id');
  const sessionId = searchParams.get('session_id');
  const orderId = searchParams.get('order_id');
  const cancelled = searchParams.get('cancelled');
  const canvasRef = useRef(null);
  
  const [templates, setTemplates] = useState([]);
  const [categories, setCategories] = useState([]);
  const [byCategory, setByCategory] = useState({});
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedSubcategory, setSelectedSubcategory] = useState('all');
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [viewMode, setViewMode] = useState('grid');
  const [loading, setLoading] = useState(true);
  const [orderStep, setOrderStep] = useState('browse');
  const [previewZoom, setPreviewZoom] = useState(100);
  const [paymentError, setPaymentError] = useState(null);
  const [paymentProcessing, setPaymentProcessing] = useState(false);
  
  const [canvasElements, setCanvasElements] = useState([]);
  const [selectedElementId, setSelectedElementId] = useState(null);
  
  const [surMesureData, setSurMesureData] = useState({
    customRequest: '',
    wantedColors: '',
    wantedStyle: '',
    additionalInfo: ''
  });
  
  const [formData, setFormData] = useState({
    slogan: '',
    product_name: '',
    description: '',
    brand_colors: ['#F59E0B', '#FFFFFF'],
    additional_notes: ''
  });
  
  const [orderResult, setOrderResult] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [isPaid, setIsPaid] = useState(false);

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

  // Poll payment status function
  const pollPaymentStatus = async (checkoutSessionId, orderIdParam, attempts = 0) => {
    const maxAttempts = 10;
    const pollInterval = 2000;

    if (attempts >= maxAttempts) {
      setPaymentError('Vérification du paiement expirée. Veuillez vérifier vos commandes.');
      setOrderStep('browse');
      return;
    }

    try {
      const response = await fetch(
        `${API_URL}/api/media-pub/payment/status/${checkoutSessionId}?order_id=${orderIdParam}`
      );
      
      if (!response.ok) {
        throw new Error('Erreur vérification paiement');
      }

      const data = await response.json();

      if (data.status === 'paid') {
        setIsPaid(true);
        setOrderResult({ id: orderIdParam, status: 'paid' });
        setOrderStep('payment_success');
        // Clean URL
        window.history.replaceState({}, '', '/media-pub');
        return;
      } else if (data.status === 'expired') {
        setPaymentError('Session de paiement expirée. Veuillez réessayer.');
        setOrderStep('browse');
        window.history.replaceState({}, '', '/media-pub');
        return;
      }

      // Continue polling
      setTimeout(() => pollPaymentStatus(checkoutSessionId, orderIdParam, attempts + 1), pollInterval);
    } catch (error) {
      console.error('Payment status check error:', error);
      if (attempts < maxAttempts - 1) {
        setTimeout(() => pollPaymentStatus(checkoutSessionId, orderIdParam, attempts + 1), pollInterval);
      } else {
        setPaymentError('Erreur lors de la vérification. Vérifiez vos commandes.');
        setOrderStep('browse');
      }
    }
  };

  const fetchTemplates = async () => {
    try {
      const response = await fetch(`${API_URL}/api/media-pub/templates`);
      const data = await response.json();
      setTemplates(data.templates);
      setCategories(['Sur Mesure', ...data.categories]);
      setByCategory(data.by_category);
    } catch (error) {
      console.error('Erreur chargement templates:', error);
    } finally {
      setLoading(false);
    }
  };

  const initializeCanvasElements = (template) => {
    const baseElements = [
      {
        id: 'product_name',
        type: 'text',
        text: 'Nom du produit',
        x: 50,
        y: 80,
        fontSize: 28,
        fontWeight: 'bold',
        color: '#FFFFFF',
        locked: false,
        zIndex: 3
      },
      {
        id: 'slogan',
        type: 'text',
        text: 'Votre slogan ici',
        x: 50,
        y: 130,
        fontSize: 42,
        fontWeight: 'bold',
        color: formData.brand_colors[0],
        locked: false,
        zIndex: 4
      },
      {
        id: 'description',
        type: 'text',
        text: 'Description...',
        x: 50,
        y: 190,
        fontSize: 18,
        fontWeight: 'normal',
        color: '#CCCCCC',
        locked: false,
        zIndex: 2
      }
    ];
    setCanvasElements(baseElements);
    setSelectedElementId(null);
  };

  const getSubcategories = () => {
    if (selectedCategory === 'all' || selectedCategory === 'Sur Mesure') return [];
    const categoryTemplates = templates.filter(t => t.category === selectedCategory);
    const subs = [...new Set(categoryTemplates.map(t => t.subcategory).filter(Boolean))];
    return subs;
  };

  const filteredTemplates = templates.filter(t => {
    if (selectedCategory === 'Sur Mesure') return false;
    if (selectedCategory !== 'all' && t.category !== selectedCategory) return false;
    if (selectedSubcategory !== 'all' && t.subcategory !== selectedSubcategory) return false;
    return true;
  });

  const handleSelectTemplate = (template) => {
    setSelectedTemplate(template);
    setOrderStep('customize');
    initializeCanvasElements(template);
    setFormData({
      slogan: '',
      product_name: '',
      description: '',
      brand_colors: ['#F59E0B', '#FFFFFF'],
      additional_notes: ''
    });
    setIsPaid(false);
  };

  const handleSurMesure = () => {
    setOrderStep('sur_mesure');
    setSelectedTemplate({
      id: 'sur_mesure',
      name: 'Création Sur Mesure',
      category: 'Sur Mesure',
      format: 'Selon vos besoins',
      price: 149.90,
      description: 'Création personnalisée par nos experts IA'
    });
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    
    if (name === 'slogan') {
      updateElement('slogan', { text: value || 'Votre slogan ici' });
    } else if (name === 'product_name') {
      updateElement('product_name', { text: value || 'Nom du produit' });
    } else if (name === 'description') {
      updateElement('description', { text: value || 'Description...' });
    }
  };

  const handleColorChange = (index, color) => {
    const newColors = [...formData.brand_colors];
    newColors[index] = color;
    setFormData(prev => ({ ...prev, brand_colors: newColors }));
    
    if (index === 0) {
      updateElement('slogan', { color: color });
    }
  };

  const updateElement = (id, updates) => {
    setCanvasElements(prev => prev.map(el => 
      el.id === id ? { ...el, ...updates } : el
    ));
  };

  const deleteElement = (id) => {
    setCanvasElements(prev => prev.filter(el => el.id !== id));
    setSelectedElementId(null);
  };

  const addNewElement = () => {
    const newElement = {
      id: `custom_${Date.now()}`,
      type: 'text',
      text: 'Nouveau texte',
      x: 100,
      y: 250,
      fontSize: 20,
      fontWeight: 'normal',
      color: '#FFFFFF',
      locked: false,
      zIndex: canvasElements.length + 1
    };
    setCanvasElements(prev => [...prev, newElement]);
    setSelectedElementId(newElement.id);
  };

  const duplicateElement = (id) => {
    const element = canvasElements.find(el => el.id === id);
    if (element) {
      const newElement = {
        ...element,
        id: `${element.id}_copy_${Date.now()}`,
        x: element.x + 20,
        y: element.y + 20
      };
      setCanvasElements(prev => [...prev, newElement]);
      setSelectedElementId(newElement.id);
    }
  };

  const toggleElementLock = (id) => {
    updateElement(id, { locked: !canvasElements.find(el => el.id === id)?.locked });
  };

  const selectedElement = canvasElements.find(el => el.id === selectedElementId);

  const handleProceedToPayment = () => {
    if (!formData.slogan || !formData.product_name) {
      alert('Veuillez remplir le slogan et le nom du produit');
      return;
    }
    setOrderStep('payment');
  };

  const handlePayment = async () => {
    setSubmitting(true);
    setPaymentError(null);
    
    try {
      // First create the order if not already created
      let currentOrderId = orderResult?.id;
      
      if (!currentOrderId) {
        // Create order first
        const orderData = orderStep === 'sur_mesure' || selectedTemplate?.id === 'sur_mesure' ? {
          template_id: 'sur_mesure',
          enterprise_id: enterpriseId || 'demo-enterprise',
          slogan: surMesureData.customRequest,
          product_name: 'Création Sur Mesure',
          description: `Couleurs: ${surMesureData.wantedColors}\nStyle: ${surMesureData.wantedStyle}\nInfos: ${surMesureData.additionalInfo}`,
          brand_colors: formData.brand_colors,
          additional_notes: surMesureData.additionalInfo
        } : {
          template_id: selectedTemplate.id,
          enterprise_id: enterpriseId || 'demo-enterprise',
          slogan: formData.slogan,
          product_name: formData.product_name,
          description: formData.description,
          brand_colors: formData.brand_colors,
          additional_notes: formData.additional_notes,
          canvas_elements: canvasElements
        };

        const orderResponse = await fetch(`${API_URL}/api/media-pub/orders`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(orderData)
        });

        if (!orderResponse.ok) {
          throw new Error('Erreur création commande');
        }

        const orderResult = await orderResponse.json();
        currentOrderId = orderResult.id;
        setOrderResult(orderResult);
      }

      // Create Stripe checkout session
      const paymentResponse = await fetch(`${API_URL}/api/media-pub/payment/create-session`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          order_id: currentOrderId,
          origin_url: window.location.origin
        })
      });

      if (!paymentResponse.ok) {
        const errorData = await paymentResponse.json();
        throw new Error(errorData.detail || 'Erreur création session de paiement');
      }

      const paymentData = await paymentResponse.json();
      
      // Redirect to Stripe Checkout
      if (paymentData.checkout_url) {
        window.location.href = paymentData.checkout_url;
      } else {
        throw new Error('URL de paiement non reçue');
      }

    } catch (error) {
      console.error('Payment error:', error);
      setPaymentError(error.message || 'Erreur lors du paiement');
      setSubmitting(false);
    }
  };

  const handleSubmitOrder = async () => {
    setSubmitting(true);
    setOrderStep('processing');

    try {
      const orderData = orderStep === 'sur_mesure' ? {
        template_id: 'sur_mesure',
        enterprise_id: enterpriseId || 'demo-enterprise',
        slogan: surMesureData.customRequest,
        product_name: 'Création Sur Mesure',
        description: `Couleurs: ${surMesureData.wantedColors}\nStyle: ${surMesureData.wantedStyle}\nInfos: ${surMesureData.additionalInfo}`,
        brand_colors: formData.brand_colors,
        additional_notes: surMesureData.additionalInfo
      } : {
        template_id: selectedTemplate.id,
        enterprise_id: enterpriseId || 'demo-enterprise',
        slogan: formData.slogan,
        product_name: formData.product_name,
        description: formData.description,
        brand_colors: formData.brand_colors,
        additional_notes: formData.additional_notes,
        canvas_elements: canvasElements
      };

      const response = await fetch(`${API_URL}/api/media-pub/orders`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(orderData)
      });

      const result = await response.json();
      setOrderResult(result);
      setOrderStep('confirm');
    } catch (error) {
      console.error('Erreur commande:', error);
      alert('Erreur lors de la commande');
      setOrderStep('customize');
    } finally {
      setSubmitting(false);
    }
  };

  // Watermark Component
  const Watermark = () => (
    <div 
      className="absolute inset-0 pointer-events-none overflow-hidden rounded-lg"
      style={{ zIndex: 1000 }}
    >
      <div className="absolute inset-0 bg-black/10" />
      <div className="absolute inset-0 flex flex-wrap justify-center items-center">
        {[...Array(9)].map((_, i) => (
          <div 
            key={i}
            className="text-2xl font-black transform -rotate-45 mx-8 my-4"
            style={{
              color: 'rgba(255,255,255,0.35)',
              textShadow: '2px 2px 4px rgba(0,0,0,0.5)',
              letterSpacing: '4px'
            }}
          >
            TITELLI
          </div>
        ))}
      </div>
      <div className="absolute inset-0 flex items-center justify-center">
        <div 
          className="text-5xl md:text-6xl font-black transform -rotate-12"
          style={{
            color: 'rgba(255,255,255,0.5)',
            textShadow: '3px 3px 6px rgba(0,0,0,0.7)',
            letterSpacing: '8px',
            WebkitTextStroke: '1px rgba(0,0,0,0.3)'
          }}
        >
          TITELLI
        </div>
      </div>
      <div 
        className="absolute inset-0"
        style={{
          backgroundImage: `repeating-linear-gradient(
            45deg,
            transparent,
            transparent 30px,
            rgba(255,255,255,0.05) 30px,
            rgba(255,255,255,0.05) 60px
          )`
        }}
      />
    </div>
  );

  // Live Preview Component
  const LivePreview = () => {
    if (!selectedTemplate) return null;

    return (
      <div className="relative bg-gray-900 rounded-xl overflow-hidden border border-gray-700" data-testid="live-preview">
        {/* Zoom Controls */}
        <div className="absolute top-3 right-3 z-20 flex items-center gap-2 bg-black/50 rounded-lg p-1">
          <button 
            onClick={() => setPreviewZoom(Math.max(50, previewZoom - 10))}
            className="p-1 hover:bg-white/20 rounded"
          >
            <ZoomOut className="w-4 h-4" />
          </button>
          <span className="text-xs min-w-[40px] text-center">{previewZoom}%</span>
          <button 
            onClick={() => setPreviewZoom(Math.min(150, previewZoom + 10))}
            className="p-1 hover:bg-white/20 rounded"
          >
            <ZoomIn className="w-4 h-4" />
          </button>
          <button 
            onClick={() => setPreviewZoom(100)}
            className="p-1 hover:bg-white/20 rounded"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
        </div>

        {!isPaid && (
          <div className="absolute top-3 left-3 z-20 bg-yellow-500 text-black text-xs font-bold px-3 py-1.5 rounded-lg flex items-center gap-2">
            <Lock className="w-3 h-3" />
            Filigrane - Payez pour télécharger sans
          </div>
        )}

        <div 
          className="relative overflow-auto"
          style={{ 
            maxHeight: '500px',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            padding: '20px'
          }}
        >
          <div 
            ref={canvasRef}
            className="relative shadow-2xl select-none"
            style={{ 
              transform: `scale(${previewZoom / 100})`,
              transformOrigin: 'center center',
              transition: 'transform 0.2s ease',
              minWidth: '400px',
              minHeight: '400px'
            }}
            onClick={() => setSelectedElementId(null)}
            data-testid="canvas-container"
          >
            <img
              src={selectedTemplate.preview_url}
              alt={selectedTemplate.name}
              className="max-w-full rounded-lg"
              draggable={false}
            />
            
            {canvasElements.map(element => (
              <DraggableElement
                key={element.id}
                element={element}
                isSelected={selectedElementId === element.id}
                onSelect={setSelectedElementId}
                onUpdate={updateElement}
                onDelete={deleteElement}
              />
            ))}

            <div 
              className="absolute inset-0 pointer-events-none mix-blend-overlay opacity-20 rounded-lg"
              style={{ backgroundColor: formData.brand_colors[0] }}
            />

            {!isPaid && <Watermark />}
          </div>
        </div>

        <div className="p-3 bg-gray-800/50 border-t border-gray-700 flex items-center justify-between">
          <div className="text-sm text-gray-400">
            <span className="text-gray-500">Format:</span> {selectedTemplate.format}
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <MousePointer className="w-4 h-4 text-yellow-400" />
              <span className="text-sm text-gray-400">Cliquez et déplacez</span>
            </div>
            <div className="flex items-center gap-2">
              <Eye className="w-4 h-4 text-gray-500" />
              <span className="text-sm text-gray-400">Aperçu</span>
            </div>
          </div>
        </div>
      </div>
    );
  };

  // Element Editor Panel
  const ElementEditor = () => {
    if (!selectedElement) return (
      <div className="bg-gray-800/30 rounded-lg p-4 text-center text-gray-500 border border-dashed border-gray-700">
        <MousePointer className="w-8 h-8 mx-auto mb-2 opacity-50" />
        <p className="text-sm">Sélectionnez un élément pour le modifier</p>
      </div>
    );

    return (
      <div className="bg-gray-800/50 rounded-lg p-4 space-y-4 border border-gray-700" data-testid="element-editor">
        <div className="flex items-center justify-between">
          <h4 className="font-medium text-white flex items-center gap-2">
            <Settings className="w-4 h-4 text-yellow-400" />
            Modifier l'élément
          </h4>
          <div className="flex gap-1">
            <button
              onClick={() => toggleElementLock(selectedElement.id)}
              className={`p-1.5 rounded ${selectedElement.locked ? 'bg-yellow-500/20 text-yellow-400' : 'bg-gray-700 text-gray-400 hover:text-white'}`}
            >
              {selectedElement.locked ? <Lock className="w-4 h-4" /> : <Unlock className="w-4 h-4" />}
            </button>
            <button
              onClick={() => duplicateElement(selectedElement.id)}
              className="p-1.5 rounded bg-gray-700 text-gray-400 hover:text-white"
            >
              <Copy className="w-4 h-4" />
            </button>
            <button
              onClick={() => deleteElement(selectedElement.id)}
              className="p-1.5 rounded bg-red-500/20 text-red-400 hover:bg-red-500/30"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </div>

        <div>
          <label className="block text-xs text-gray-400 mb-1">Texte</label>
          <input
            type="text"
            value={selectedElement.text}
            onChange={(e) => updateElement(selectedElement.id, { text: e.target.value })}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm"
            disabled={selectedElement.locked}
          />
        </div>

        <div>
          <label className="block text-xs text-gray-400 mb-1">Taille ({selectedElement.fontSize}px)</label>
          <input
            type="range"
            min="12"
            max="72"
            value={selectedElement.fontSize}
            onChange={(e) => updateElement(selectedElement.id, { fontSize: parseInt(e.target.value) })}
            className="w-full accent-yellow-500"
            disabled={selectedElement.locked}
          />
        </div>

        <div className="flex gap-2">
          <button
            onClick={() => updateElement(selectedElement.id, { fontWeight: selectedElement.fontWeight === 'bold' ? 'normal' : 'bold' })}
            className={`flex-1 p-2 rounded ${selectedElement.fontWeight === 'bold' ? 'bg-yellow-500 text-black' : 'bg-gray-700'}`}
            disabled={selectedElement.locked}
          >
            <Bold className="w-4 h-4 mx-auto" />
          </button>
          <button
            onClick={() => updateElement(selectedElement.id, { fontStyle: selectedElement.fontStyle === 'italic' ? 'normal' : 'italic' })}
            className={`flex-1 p-2 rounded ${selectedElement.fontStyle === 'italic' ? 'bg-yellow-500 text-black' : 'bg-gray-700'}`}
            disabled={selectedElement.locked}
          >
            <Italic className="w-4 h-4 mx-auto" />
          </button>
        </div>

        <div className="flex gap-2">
          <button
            onClick={() => updateElement(selectedElement.id, { textAlign: 'left' })}
            className={`flex-1 p-2 rounded ${selectedElement.textAlign === 'left' ? 'bg-yellow-500 text-black' : 'bg-gray-700'}`}
            disabled={selectedElement.locked}
          >
            <AlignLeft className="w-4 h-4 mx-auto" />
          </button>
          <button
            onClick={() => updateElement(selectedElement.id, { textAlign: 'center' })}
            className={`flex-1 p-2 rounded ${(!selectedElement.textAlign || selectedElement.textAlign === 'center') ? 'bg-yellow-500 text-black' : 'bg-gray-700'}`}
            disabled={selectedElement.locked}
          >
            <AlignCenter className="w-4 h-4 mx-auto" />
          </button>
          <button
            onClick={() => updateElement(selectedElement.id, { textAlign: 'right' })}
            className={`flex-1 p-2 rounded ${selectedElement.textAlign === 'right' ? 'bg-yellow-500 text-black' : 'bg-gray-700'}`}
            disabled={selectedElement.locked}
          >
            <AlignRight className="w-4 h-4 mx-auto" />
          </button>
        </div>

        <div>
          <label className="block text-xs text-gray-400 mb-1">Couleur</label>
          <div className="flex items-center gap-2">
            <input
              type="color"
              value={selectedElement.color}
              onChange={(e) => updateElement(selectedElement.id, { color: e.target.value })}
              className="w-10 h-10 rounded cursor-pointer border border-gray-600"
              disabled={selectedElement.locked}
            />
            <input
              type="text"
              value={selectedElement.color}
              onChange={(e) => updateElement(selectedElement.id, { color: e.target.value })}
              className="flex-1 px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm"
              disabled={selectedElement.locked}
            />
          </div>
        </div>
      </div>
    );
  };

  // Browse Templates
  const renderBrowseStep = () => (
    <div className="space-y-6">
      {/* Category Filters */}
      <div className="bg-gray-800/50 p-4 rounded-xl space-y-3 border border-gray-700">
        <div className="flex items-center gap-2 flex-wrap">
          <Filter className="w-5 h-5 text-yellow-400" />
          <button
            onClick={() => { setSelectedCategory('all'); setSelectedSubcategory('all'); }}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              selectedCategory === 'all'
                ? 'bg-yellow-500 text-black'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            Tous ({templates.length})
          </button>
          
          <button
            onClick={() => { setSelectedCategory('Sur Mesure'); setSelectedSubcategory('all'); }}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all flex items-center gap-2 ${
              selectedCategory === 'Sur Mesure'
                ? 'bg-gradient-to-r from-yellow-500 to-orange-500 text-black'
                : 'bg-gradient-to-r from-yellow-500/20 to-orange-500/20 text-yellow-400 hover:from-yellow-500/30 hover:to-orange-500/30 border border-yellow-500/30'
            }`}
          >
            <Wand2 className="w-4 h-4" />
            Sur Mesure
          </button>
          
          {categories.filter(c => c !== 'Sur Mesure').map(cat => (
            <button
              key={cat}
              onClick={() => { setSelectedCategory(cat); setSelectedSubcategory('all'); }}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                selectedCategory === cat
                  ? 'bg-yellow-500 text-black'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              {cat} ({templates.filter(t => t.category === cat).length})
            </button>
          ))}
        </div>

        {getSubcategories().length > 0 && (
          <div className="flex items-center gap-2 flex-wrap pl-7 pt-2 border-t border-gray-700">
            <Layers className="w-4 h-4 text-gray-500" />
            <button
              onClick={() => setSelectedSubcategory('all')}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                selectedSubcategory === 'all'
                  ? 'bg-orange-500 text-black'
                  : 'bg-gray-600 text-gray-300 hover:bg-gray-500'
              }`}
            >
              Tous les types
            </button>
            {getSubcategories().map(sub => (
              <button
                key={sub}
                onClick={() => setSelectedSubcategory(sub)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                  selectedSubcategory === sub
                    ? 'bg-orange-500 text-black'
                    : 'bg-gray-600 text-gray-300 hover:bg-gray-500'
                }`}
              >
                {sub}
              </button>
            ))}
          </div>
        )}
        
        <div className="flex items-center justify-end gap-2">
          <button
            onClick={() => setViewMode('grid')}
            className={`p-2 rounded-lg ${viewMode === 'grid' ? 'bg-yellow-500 text-black' : 'bg-gray-700'}`}
          >
            <Grid className="w-5 h-5" />
          </button>
          <button
            onClick={() => setViewMode('list')}
            className={`p-2 rounded-lg ${viewMode === 'list' ? 'bg-yellow-500 text-black' : 'bg-gray-700'}`}
          >
            <List className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Sur Mesure Section */}
      {selectedCategory === 'Sur Mesure' && (
        <div className="bg-gradient-to-br from-yellow-900/30 to-orange-900/30 rounded-2xl p-8 border border-yellow-500/30">
          <div className="text-center max-w-2xl mx-auto">
            <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-gradient-to-r from-yellow-500 to-orange-500 flex items-center justify-center">
              <Wand2 className="w-10 h-10 text-white" />
            </div>
            <h2 className="text-2xl font-bold text-white mb-3">Création Sur Mesure</h2>
            <p className="text-gray-300 mb-6">
              Décrivez exactement ce que vous voulez et notre IA créera une publicité unique basée sur vos instructions. 
              Couleurs, style, slogan, tout est personnalisable selon vos envies.
            </p>
            <div className="bg-black/30 rounded-xl p-4 mb-6 text-left">
              <h4 className="font-medium text-yellow-400 mb-2">Ce que vous pouvez demander :</h4>
              <ul className="text-sm text-gray-400 space-y-1">
                <li className="flex items-center gap-2"><Check className="w-4 h-4 text-green-400" /> Modifier les couleurs, polices et style</li>
                <li className="flex items-center gap-2"><Check className="w-4 h-4 text-green-400" /> Ajouter votre slogan et description</li>
                <li className="flex items-center gap-2"><Check className="w-4 h-4 text-green-400" /> Choisir le positionnement des éléments</li>
                <li className="flex items-center gap-2"><Check className="w-4 h-4 text-green-400" /> Demander un style spécifique</li>
              </ul>
            </div>
            <button
              onClick={handleSurMesure}
              className="px-8 py-4 bg-gradient-to-r from-yellow-500 to-orange-500 hover:from-yellow-600 hover:to-orange-600 text-black font-bold rounded-xl flex items-center gap-2 mx-auto shadow-lg shadow-yellow-500/30 transition-all"
              data-testid="sur-mesure-button"
            >
              <Sparkles className="w-5 h-5" />
              Commencer ma création - 149.90 CHF
            </button>
          </div>
        </div>
      )}

      {selectedCategory !== 'Sur Mesure' && (
        <>
          <div className="text-sm text-gray-400">
            {filteredTemplates.length} modèle{filteredTemplates.length > 1 ? 's' : ''} trouvé{filteredTemplates.length > 1 ? 's' : ''}
          </div>

          <div className={`grid gap-6 ${viewMode === 'grid' ? 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4' : 'grid-cols-1'}`}>
            {filteredTemplates.map(template => (
              <div
                key={template.id}
                className="bg-gray-800/50 rounded-xl overflow-hidden border border-gray-700 hover:border-yellow-500/50 transition-all group cursor-pointer"
                onClick={() => handleSelectTemplate(template)}
                data-testid={`template-${template.id}`}
              >
                <div className="relative aspect-square">
                  <img
                    src={template.preview_url}
                    alt={template.name}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                  />
                  {template.popular && (
                    <span className="absolute top-3 right-3 bg-yellow-500 text-black text-xs font-bold px-2 py-1 rounded-full flex items-center gap-1">
                      <Star className="w-3 h-3" /> Populaire
                    </span>
                  )}
                  {template.subcategory && (
                    <span className="absolute top-3 left-3 bg-orange-500/80 text-white text-xs px-2 py-1 rounded">
                      {template.subcategory}
                    </span>
                  )}
                  <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex items-end justify-center pb-4">
                    <button className="bg-yellow-500 text-black px-6 py-2 rounded-lg font-medium flex items-center gap-2 shadow-lg">
                      Personnaliser <ArrowRight className="w-4 h-4" />
                    </button>
                  </div>
                </div>
                
                <div className="p-4">
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <h3 className="font-semibold text-white text-sm">{template.name}</h3>
                      <p className="text-xs text-gray-500">{template.category}</p>
                    </div>
                    <span className="text-lg font-bold text-yellow-400">{template.price} CHF</span>
                  </div>
                  <p className="text-xs text-gray-500 line-clamp-2">{template.description}</p>
                  <div className="mt-2 flex items-center gap-2">
                    <span className="text-xs bg-gray-700 px-2 py-0.5 rounded text-gray-400">
                      {template.format}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );

  // Sur Mesure Step
  const renderSurMesureStep = () => (
    <div className="max-w-4xl mx-auto">
      <button
        onClick={() => setOrderStep('browse')}
        className="text-gray-400 hover:text-white mb-6 flex items-center gap-2"
      >
        <ArrowLeft className="w-4 h-4" /> Retour aux modèles
      </button>

      <div className="bg-gradient-to-br from-yellow-900/30 to-orange-900/30 rounded-2xl p-8 border border-yellow-500/20">
        <div className="text-center mb-8">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-r from-yellow-500 to-orange-500 flex items-center justify-center">
            <Wand2 className="w-8 h-8 text-white" />
          </div>
          <h2 className="text-2xl font-bold text-white mb-2">Création Sur Mesure</h2>
          <p className="text-gray-400">Décrivez exactement ce que vous voulez</p>
        </div>

        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              <FileText className="inline w-4 h-4 mr-1" />
              Décrivez votre publicité idéale *
            </label>
            <textarea
              value={surMesureData.customRequest}
              onChange={(e) => setSurMesureData(prev => ({ ...prev, customRequest: e.target.value }))}
              placeholder="Ex: Je veux une publicité pour mon restaurant italien avec une ambiance chaleureuse..."
              rows={5}
              className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-xl text-white placeholder-gray-500 focus:ring-2 focus:ring-yellow-500 focus:border-transparent resize-none"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              <Palette className="inline w-4 h-4 mr-1" />
              Couleurs souhaitées
            </label>
            <input
              type="text"
              value={surMesureData.wantedColors}
              onChange={(e) => setSurMesureData(prev => ({ ...prev, wantedColors: e.target.value }))}
              placeholder="Ex: Rouge bordeaux, doré, noir élégant..."
              className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-xl text-white placeholder-gray-500 focus:ring-2 focus:ring-yellow-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              <Sparkles className="inline w-4 h-4 mr-1" />
              Style souhaité
            </label>
            <input
              type="text"
              value={surMesureData.wantedStyle}
              onChange={(e) => setSurMesureData(prev => ({ ...prev, wantedStyle: e.target.value }))}
              placeholder="Ex: Moderne et minimaliste, Luxueux, Chaleureux..."
              className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-xl text-white placeholder-gray-500 focus:ring-2 focus:ring-yellow-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Informations supplémentaires
            </label>
            <textarea
              value={surMesureData.additionalInfo}
              onChange={(e) => setSurMesureData(prev => ({ ...prev, additionalInfo: e.target.value }))}
              placeholder="Tout autre détail important..."
              rows={3}
              className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-xl text-white placeholder-gray-500 focus:ring-2 focus:ring-yellow-500 focus:border-transparent resize-none"
            />
          </div>

          <div className="bg-yellow-900/30 border border-yellow-700/50 rounded-xl p-4">
            <h4 className="font-medium text-yellow-400 mb-2 flex items-center gap-2">
              <Lock className="w-4 h-4" />
              Protection anti-screenshot
            </h4>
            <p className="text-sm text-yellow-200/80">
              Un filigrane "TITELLI" sera présent sur l'aperçu. Après paiement, vous recevrez l'image finale sans filigrane.
            </p>
          </div>

          <button
            onClick={() => setOrderStep('payment')}
            disabled={!surMesureData.customRequest}
            className="w-full py-4 bg-gradient-to-r from-yellow-500 to-orange-500 hover:from-yellow-600 hover:to-orange-600 text-black font-bold rounded-xl flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg shadow-yellow-500/30"
            data-testid="sur-mesure-submit"
          >
            <CreditCard className="w-5 h-5" />
            Procéder au paiement - 149.90 CHF
          </button>
        </div>
      </div>
    </div>
  );

  // Customize Step
  const renderCustomizeStep = () => (
    <div className="max-w-7xl mx-auto">
      <button
        onClick={() => setOrderStep('browse')}
        className="text-gray-400 hover:text-white mb-6 flex items-center gap-2"
      >
        <ArrowLeft className="w-4 h-4" /> Retour aux modèles
      </button>

      <div className="grid lg:grid-cols-5 gap-6">
        <div className="lg:col-span-3 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <Eye className="text-yellow-400" />
              Aperçu en direct
            </h2>
            <span className="text-sm text-gray-400">{selectedTemplate?.name}</span>
          </div>
          
          <LivePreview />
          <ElementEditor />
          
          <button
            onClick={addNewElement}
            className="w-full py-3 bg-gray-800 hover:bg-gray-700 border-2 border-dashed border-gray-600 rounded-xl text-gray-400 hover:text-white flex items-center justify-center gap-2 transition-colors"
          >
            <Plus className="w-5 h-5" />
            Ajouter un élément texte
          </button>
        </div>

        <div className="lg:col-span-2 space-y-4">
          <div className="bg-gray-800/50 rounded-xl p-6 border border-gray-700">
            <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
              <Palette className="text-yellow-400" />
              Personnalisation
            </h2>

            <div className="space-y-5">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  <Type className="inline w-4 h-4 mr-1" />
                  Slogan / Accroche *
                </label>
                <input
                  type="text"
                  name="slogan"
                  value={formData.slogan}
                  onChange={handleInputChange}
                  placeholder="Ex: Qualité suisse, prix imbattable"
                  className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-yellow-500 focus:border-transparent"
                  maxLength={50}
                />
                <p className="text-xs text-gray-500 mt-1">{formData.slogan.length}/50</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  <FileText className="inline w-4 h-4 mr-1" />
                  Nom du produit/service *
                </label>
                <input
                  type="text"
                  name="product_name"
                  value={formData.product_name}
                  onChange={handleInputChange}
                  placeholder="Ex: Collection Printemps 2026"
                  className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-yellow-500 focus:border-transparent"
                  maxLength={40}
                />
                <p className="text-xs text-gray-500 mt-1">{formData.product_name.length}/40</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Description (optionnel)
                </label>
                <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleInputChange}
                  placeholder="Détails supplémentaires..."
                  rows={2}
                  className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-yellow-500 focus:border-transparent resize-none"
                  maxLength={100}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-3">
                  <Palette className="inline w-4 h-4 mr-1" />
                  Couleurs de marque
                </label>
                <div className="grid grid-cols-2 gap-4">
                  <div className="flex items-center gap-2">
                    <input
                      type="color"
                      value={formData.brand_colors[0]}
                      onChange={(e) => handleColorChange(0, e.target.value)}
                      className="w-12 h-12 rounded-lg cursor-pointer border-2 border-gray-600"
                    />
                    <div>
                      <p className="text-sm text-white">Principale</p>
                      <p className="text-xs text-gray-500">{formData.brand_colors[0]}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <input
                      type="color"
                      value={formData.brand_colors[1]}
                      onChange={(e) => handleColorChange(1, e.target.value)}
                      className="w-12 h-12 rounded-lg cursor-pointer border-2 border-gray-600"
                    />
                    <div>
                      <p className="text-sm text-white">Secondaire</p>
                      <p className="text-xs text-gray-500">{formData.brand_colors[1]}</p>
                    </div>
                  </div>
                </div>
                
                <div className="mt-3 flex items-center gap-2 flex-wrap">
                  <span className="text-xs text-gray-500">Rapide:</span>
                  {['#F59E0B', '#EF4444', '#3B82F6', '#10B981', '#8B5CF6', '#EC4899', '#1F2937'].map(color => (
                    <button
                      key={color}
                      onClick={() => handleColorChange(0, color)}
                      className="w-6 h-6 rounded-full border-2 border-gray-600 hover:scale-110 transition-transform"
                      style={{ backgroundColor: color }}
                    />
                  ))}
                </div>
              </div>
            </div>
          </div>

          <div className="bg-yellow-900/30 border border-yellow-700 rounded-xl p-4">
            <h4 className="font-medium text-yellow-400 mb-2 flex items-center gap-2">
              <Lock className="w-4 h-4" />
              Protection
            </h4>
            <ul className="text-sm text-yellow-200/80 space-y-1">
              <li>• Filigrane visible jusqu'au paiement</li>
              <li>• Image HD sans filigrane après achat</li>
            </ul>
          </div>

          <div className="bg-gray-800/50 rounded-xl p-4 border border-gray-700">
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div>
                <span className="text-gray-500">Catégorie:</span>
                <span className="text-white ml-2">{selectedTemplate?.category}</span>
              </div>
              <div>
                <span className="text-gray-500">Format:</span>
                <span className="text-white ml-2">{selectedTemplate?.format}</span>
              </div>
            </div>
          </div>

          <button
            onClick={handleProceedToPayment}
            disabled={submitting || !formData.slogan || !formData.product_name}
            className="w-full py-4 bg-gradient-to-r from-yellow-500 to-orange-500 hover:from-yellow-600 hover:to-orange-600 text-black font-bold rounded-xl flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg"
            data-testid="proceed-to-payment"
          >
            <CreditCard className="w-5 h-5" />
            Commander - {selectedTemplate?.price} CHF
          </button>
        </div>
      </div>
    </div>
  );

  // Payment Step
  const renderPaymentStep = () => (
    <div className="max-w-lg mx-auto">
      <button
        onClick={() => setOrderStep(selectedTemplate?.id === 'sur_mesure' ? 'sur_mesure' : 'customize')}
        className="text-gray-400 hover:text-white mb-6 flex items-center gap-2"
      >
        <ArrowLeft className="w-4 h-4" /> Retour
      </button>

      <div className="bg-gray-800/50 rounded-2xl p-8 border border-gray-700">
        <div className="text-center mb-8">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-yellow-500/20 flex items-center justify-center">
            <CreditCard className="w-8 h-8 text-yellow-400" />
          </div>
          <h2 className="text-2xl font-bold text-white mb-2">Paiement</h2>
          <p className="text-gray-400">Finalisez votre commande</p>
        </div>

        <div className="bg-gray-900/50 rounded-xl p-4 mb-6">
          <h4 className="font-medium text-white mb-3">Récapitulatif</h4>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-400">Template:</span>
              <span className="text-white">{selectedTemplate?.name}</span>
            </div>
            <div className="border-t border-gray-700 pt-2 mt-2 flex justify-between">
              <span className="text-gray-300 font-medium">Total:</span>
              <span className="text-yellow-400 font-bold text-lg">{selectedTemplate?.price} CHF</span>
            </div>
          </div>
        </div>

        <div className="bg-green-900/30 border border-green-700/50 rounded-xl p-4 mb-6">
          <div className="flex items-start gap-3">
            <Unlock className="w-5 h-5 text-green-400 mt-0.5" />
            <div>
              <h4 className="font-medium text-green-400 mb-1">Après paiement</h4>
              <p className="text-sm text-green-200/80">
                Image HD <strong>sans filigrane</strong> disponible dans "Commandes Titelli"
              </p>
            </div>
          </div>
        </div>

        {/* Stripe Badge */}
        <div className="flex items-center justify-center gap-2 mb-4 text-gray-500 text-sm">
          <Lock className="w-4 h-4" />
          <span>Paiement sécurisé par</span>
          <span className="font-bold text-white">Stripe</span>
        </div>

        {paymentError && (
          <div className="bg-red-900/30 border border-red-700/50 rounded-xl p-3 mb-4">
            <p className="text-sm text-red-400 flex items-center gap-2">
              <AlertCircle className="w-4 h-4" />
              {paymentError}
            </p>
          </div>
        )}

        <button
          onClick={handlePayment}
          disabled={submitting}
          className="w-full py-4 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white font-bold rounded-xl flex items-center justify-center gap-2 disabled:opacity-50 transition-all shadow-lg"
          data-testid="confirm-payment"
        >
          {submitting ? (
            <>
              <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              Redirection vers Stripe...
            </>
          ) : (
            <>
              <ExternalLink className="w-5 h-5" />
              Payer {selectedTemplate?.price} CHF via Stripe
            </>
          )}
        </button>
      </div>
    </div>
  );

  // Processing Step
  const renderProcessingStep = () => (
    <div className="max-w-md mx-auto text-center py-12">
      <div className="w-24 h-24 mx-auto mb-6 relative">
        <div className="absolute inset-0 border-4 border-yellow-500/30 rounded-full"></div>
        <div className="absolute inset-0 border-4 border-yellow-500 border-t-transparent rounded-full animate-spin"></div>
        <Sparkles className="absolute inset-0 m-auto w-10 h-10 text-yellow-400" />
      </div>
      <h2 className="text-2xl font-bold text-white mb-2">Création en cours...</h2>
      <p className="text-gray-400 mb-6">
        Notre IA génère votre publicité personnalisée
      </p>
      <div className="flex items-center justify-center gap-2 text-sm text-gray-500">
        <Clock className="w-4 h-4" />
        Temps estimé: 2-5 minutes
      </div>
    </div>
  );

  // Confirm Step
  const renderConfirmStep = () => (
    <div className="max-w-md mx-auto text-center py-12">
      <div className="w-20 h-20 mx-auto mb-6 bg-green-500/20 rounded-full flex items-center justify-center">
        <Check className="w-10 h-10 text-green-400" />
      </div>
      <h2 className="text-2xl font-bold text-white mb-2">Commande confirmée !</h2>
      <p className="text-gray-400 mb-6">
        Votre publicité <strong>sans filigrane</strong> sera disponible dans
        <span className="text-yellow-400 font-medium"> "Commandes Titelli"</span>
      </p>
      
      {orderResult && (
        <div className="bg-gray-800/50 rounded-xl p-4 mb-6 text-left">
          <p className="text-sm text-gray-400">
            <span className="text-gray-500">N° commande:</span> {orderResult.id}
          </p>
          <p className="text-sm text-gray-400">
            <span className="text-gray-500">Statut:</span> 
            <span className="text-yellow-400 ml-1">En cours de création</span>
          </p>
        </div>
      )}

      <div className="flex flex-col gap-3">
        <button
          onClick={() => navigate('/dashboard/entreprise?tab=commandes-titelli')}
          className="w-full py-3 bg-yellow-500 hover:bg-yellow-600 text-black font-medium rounded-lg transition-colors flex items-center justify-center gap-2"
        >
          <Download className="w-4 h-4" />
          Voir mes commandes
        </button>
        <button
          onClick={() => {
            setOrderStep('browse');
            setSelectedTemplate(null);
            setCanvasElements([]);
            setIsPaid(false);
          }}
          className="w-full py-3 bg-gray-700 hover:bg-gray-600 text-white font-medium rounded-lg transition-colors"
        >
          Créer une autre publicité
        </button>
      </div>
    </div>
  );

  // Payment Verification Step (when returning from Stripe)
  const renderPaymentVerificationStep = () => (
    <div className="max-w-md mx-auto text-center py-12">
      <div className="w-24 h-24 mx-auto mb-6 relative">
        <div className="absolute inset-0 border-4 border-green-500/30 rounded-full"></div>
        <div className="absolute inset-0 border-4 border-green-500 border-t-transparent rounded-full animate-spin"></div>
        <CreditCard className="absolute inset-0 m-auto w-10 h-10 text-green-400" />
      </div>
      <h2 className="text-2xl font-bold text-white mb-2">Vérification du paiement...</h2>
      <p className="text-gray-400 mb-6">
        Nous confirmons votre paiement, veuillez patienter.
      </p>
      <div className="flex items-center justify-center gap-2 text-sm text-gray-500">
        <Clock className="w-4 h-4" />
        Quelques secondes...
      </div>
    </div>
  );

  // Payment Success Step
  const renderPaymentSuccessStep = () => (
    <div className="max-w-md mx-auto text-center py-12">
      <div className="w-20 h-20 mx-auto mb-6 bg-green-500/20 rounded-full flex items-center justify-center">
        <CheckCircle2 className="w-10 h-10 text-green-400" />
      </div>
      <h2 className="text-2xl font-bold text-white mb-2">Paiement réussi !</h2>
      <p className="text-gray-400 mb-6">
        Votre commande est confirmée. L'image HD <strong className="text-green-400">sans filigrane</strong> sera
        disponible dans vos commandes une fois générée.
      </p>
      
      {orderResult && (
        <div className="bg-gray-800/50 rounded-xl p-4 mb-6 text-left">
          <p className="text-sm text-gray-400">
            <span className="text-gray-500">N° commande:</span> {orderResult.id}
          </p>
          <p className="text-sm text-gray-400">
            <span className="text-gray-500">Paiement:</span> 
            <span className="text-green-400 ml-1">Confirmé ✓</span>
          </p>
        </div>
      )}

      <div className="flex flex-col gap-3">
        <button
          onClick={() => navigate('/dashboard/entreprise?tab=commandes-titelli')}
          className="w-full py-3 bg-green-600 hover:bg-green-700 text-white font-medium rounded-lg transition-colors flex items-center justify-center gap-2"
          data-testid="view-orders-after-payment"
        >
          <Download className="w-4 h-4" />
          Voir mes commandes
        </button>
        <button
          onClick={() => {
            setOrderStep('browse');
            setSelectedTemplate(null);
            setCanvasElements([]);
            setIsPaid(false);
            setOrderResult(null);
          }}
          className="w-full py-3 bg-gray-700 hover:bg-gray-600 text-white font-medium rounded-lg transition-colors"
        >
          Créer une autre publicité
        </button>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="animate-spin w-12 h-12 border-4 border-yellow-500 border-t-transparent rounded-full"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 via-gray-800 to-gray-900 text-white">
      {orderStep === 'browse' && <AnimatedHeader />}
      
      <div className="container mx-auto px-4 py-8">
        {/* Payment Error Alert */}
        {paymentError && (
          <div className="max-w-lg mx-auto mb-6 bg-red-900/30 border border-red-700/50 rounded-xl p-4 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-400 mt-0.5 flex-shrink-0" />
            <div>
              <h4 className="font-medium text-red-400 mb-1">Erreur de paiement</h4>
              <p className="text-sm text-red-200/80">{paymentError}</p>
              <button 
                onClick={() => setPaymentError(null)}
                className="text-sm text-red-400 hover:text-red-300 mt-2"
              >
                Fermer
              </button>
            </div>
          </div>
        )}
        
        {orderStep === 'browse' && renderBrowseStep()}
        {orderStep === 'customize' && renderCustomizeStep()}
        {orderStep === 'sur_mesure' && renderSurMesureStep()}
        {orderStep === 'payment' && renderPaymentStep()}
        {orderStep === 'processing' && renderProcessingStep()}
        {orderStep === 'confirm' && renderConfirmStep()}
        {orderStep === 'payment_verification' && renderPaymentVerificationStep()}
        {orderStep === 'payment_success' && renderPaymentSuccessStep()}
      </div>
    </div>
  );
};

export default MediaPubPage;
