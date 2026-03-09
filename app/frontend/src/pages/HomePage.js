import React, { useState, useEffect, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ChevronRight, ChevronLeft, Star, ArrowRight, Play, Briefcase, MapPin, Target, Clock, Filter, GraduationCap, Calendar, Pause, Volume2, VolumeX, Search, Sparkles, Gift, CheckCircle, Users, Send, X, FileText } from 'lucide-react';
import { featuredAPI, categoryAPI, enterpriseAPI, servicesProductsAPI, jobsAPI, clientDocumentsAPI, trainingsAPI } from '../services/api';
import EnterpriseCard from '../components/EnterpriseCard';
import ServiceProductCard from '../components/ServiceProductCard';
import ScrollingReviews from '../components/ScrollingReviews';
import { toast } from 'sonner';
import { Zap, Heart,  Shield, Award } from 'lucide-react';
// Carousel Component with light theme - Responsive
const Carousel = ({ children, itemWidth = 280 }) => {
  const carouselRef = useRef(null);

  const scrollCarousel = (direction) => {
    if (carouselRef.current) {
      const scrollAmount = itemWidth + 16;
      const newScrollLeft = carouselRef.current.scrollLeft + (direction === 'left' ? -scrollAmount : scrollAmount);
      carouselRef.current.scrollTo({
        left: newScrollLeft,
        behavior: 'smooth'
      });
    }
  };

  return (
    <div className="relative group">
      <button
        onClick={() => scrollCarousel('left')}
        className="absolute left-0 top-1/2 -translate-y-1/2 z-10 bg-white hover:bg-gray-50 text-gray-700 p-2 sm:p-3 rounded-full shadow-lg border border-gray-200 transition-all hover:scale-110 -ml-2 sm:-ml-4 opacity-0 group-hover:opacity-100 sm:opacity-100"
        data-testid="carousel-prev"
      >
        <ChevronLeft className="w-4 h-4 sm:w-6 sm:h-6" />
      </button>
      
      <button
        onClick={() => scrollCarousel('right')}
        className="absolute right-0 top-1/2 -translate-y-1/2 z-10 bg-white hover:bg-gray-50 text-gray-700 p-2 sm:p-3 rounded-full shadow-lg border border-gray-200 transition-all hover:scale-110 -mr-2 sm:-mr-4 opacity-0 group-hover:opacity-100 sm:opacity-100"
        data-testid="carousel-next"
      >
        <ChevronRight className="w-4 h-4 sm:w-6 sm:h-6" />
      </button>

      <div 
        ref={carouselRef}
        className="flex gap-4 sm:gap-6 overflow-x-auto scrollbar-hide scroll-smooth pb-4 px-1"
        style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
      >
        {children}
      </div>
    </div>
  );
};

const HomePage = () => {
  const navigate = useNavigate();
  const [allEnterprises, setAllEnterprises] = useState([]);
  const [tendances, setTendances] = useState([]);
  const [guests, setGuests] = useState([]);
  const [offres, setOffres] = useState([]);
  const [premium, setPremium] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [filteredJobs, setFilteredJobs] = useState([]);
  const [trainings, setTrainings] = useState([]);
  const [productCategories, setProductCategories] = useState([]);
  const [serviceCategories, setServiceCategories] = useState([]);
  const [jewelryWatchProducts, setJewelryWatchProducts] = useState([]);
  const [bestProducts, setBestProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  
  // Filter state
  const [jobFilters, setJobFilters] = useState({
    type: '',
    location: '',
    enterprise: ''
  });
  const [showFilters, setShowFilters] = useState(false);
  
  // Application Modal state
  const [showApplyModal, setShowApplyModal] = useState(false);
  const [selectedJob, setSelectedJob] = useState(null);
  const [userDocuments, setUserDocuments] = useState([]);
  const [applyForm, setApplyForm] = useState({
    resume_url: '',
    cover_letter: ''
  });
  const [applying, setApplying] = useState(false);
  
  // Training purchase state
  const [purchasingTraining, setPurchasingTraining] = useState(null);

  // Filter enterprises with real photos only (no unsplash/default images)
const hasRealPhoto = (enterprise) => {
  if (!enterprise) return false;

  const img = enterprise.cover_image || enterprise.image || '';

  if (!img) return false;

  if (
    img.includes('unsplash') ||
    img.includes('placeholder') ||
    img.includes('default')
  ) {
    return false;
  }

  return true;
};

  // Sort enterprises by profile completeness
  const sortByProfileCompleteness = (enterprises) => {
    return [...enterprises].sort((a, b) => {
      const getScore = (e) => {
        let score = 0;
        if (hasRealPhoto(e)) score += 5; // Priority to real photos
        if (e.logo) score += 2;
        if (e.description && e.description.length > 50) score += 2;
        if (e.slogan) score += 1;
        if (e.rating > 0) score += 2;
        if (e.review_count > 0) score += 1;
        if (e.is_certified) score += 2;
        if (e.is_labeled) score += 2;
        if (e.is_premium) score += 2;
        return score;
      };
      return getScore(b) - getScore(a);
    });
  };

   useEffect(() => {
    const fetchData = async () => {
      try {
        const [enterprisesRes, tendRes, guestRes, offreRes, premRes, prodCatRes, servCatRes, jobsRes, trainingsRes, jewelryProductsRes] = await Promise.all([
          enterpriseAPI.list({ limit: 100 }),
          featuredAPI.tendances(),
          featuredAPI.guests(),
          featuredAPI.offres(),
          featuredAPI.premium(),
          categoryAPI.products(),
          categoryAPI.services(),
          jobsAPI.listAll().catch(() => ({ data: [] })),
          trainingsAPI.listAll({ limit: 6 }).catch(() => ({ data: [] })),
          servicesProductsAPI.list({ type: 'product', limit: 50 }).catch(() => ({ data: [] }))
        ]);
        
        // Filter and sort all enterprises - only those with real photos, then ALPHABETICALLY
        const allEnts = enterprisesRes.data.enterprises || [];
        setAllEnterprises(allEnts);
        // Sort alphabetically by business_name or name
  
        
        // Filter featured enterprises too - also alphabetically
        const tendData = (tendRes.data || []).filter(hasRealPhoto).sort((a, b) => 
          (a.business_name || a.name || '').localeCompare(b.business_name || b.name || '')
        );
        const guestData = (guestRes.data || []).filter(hasRealPhoto).sort((a, b) => 
          (a.business_name || a.name || '').localeCompare(b.business_name || b.name || '')
        );
        const premData = (premRes.data || []).filter(hasRealPhoto).sort((a, b) => 
          (a.business_name || a.name || '').localeCompare(b.business_name || b.name || '')
        );
        
        setTendances(tendData);
        setGuests(guestData);
        setOffres(offreRes.data);
        setPremium(premData);
        setProductCategories(prodCatRes.data);
        setServiceCategories(servCatRes.data);
        const jobsData = jobsRes.data || [];
        setJobs(jobsData);
        setFilteredJobs(jobsData);
        setTrainings(trainingsRes.data || []);
        
        // Filter jewelry/watch products for the special section
        const allProducts = jewelryProductsRes.data?.items || jewelryProductsRes.data || [];
        const jewelryProducts = allProducts.filter(p => {
          const cat = (p.category || '').toLowerCase();
          const name = (p.name || '').toLowerCase();
          return cat.includes('bijou') || cat.includes('montre') || cat.includes('horlog') || 
                 cat.includes('joaill') || name.includes('montre') || name.includes('bijou');
        });
        setJewelryWatchProducts(jewelryProducts);
        
        // Filter best products with nice images and price
        const productsWithImages = allProducts.filter(p => {
          const images = p.images || [];
          const hasImage = images.length > 0 && images[0] && !images[0].includes('placeholder');
          const hasPrice = p.price && p.price > 0;
          return hasImage && hasPrice;
        });
        // Sort by those starting with 't' first, then alphabetically
        const sortedProducts = productsWithImages.sort((a, b) => {
          const nameA = (a.name || '').toLowerCase();
          const nameB = (b.name || '').toLowerCase();
          const startsWithTA = nameA.startsWith('t');
          const startsWithTB = nameB.startsWith('t');
          if (startsWithTA && !startsWithTB) return -1;
          if (!startsWithTA && startsWithTB) return 1;
          return nameA.localeCompare(nameB);
        });
        setBestProducts(sortedProducts.slice(0, 20));
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);
  
  // Apply filters
  useEffect(() => {
    let result = [...jobs];
    
    if (jobFilters.type) {
      result = result.filter(job => job.type === jobFilters.type);
    }
    
    if (jobFilters.location) {
      result = result.filter(job => 
        (job.location || '').toLowerCase().includes(jobFilters.location.toLowerCase())
      );
    }
    
    if (jobFilters.enterprise) {
      result = result.filter(job => 
        (job.enterprise_name || '').toLowerCase().includes(jobFilters.enterprise.toLowerCase())
      );
    }
    
    setFilteredJobs(result);
  }, [jobFilters, jobs]);
  
  // Handle search
  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQuery)}`);
    }
  };
  
  // Open apply modal
  const handleApplyClick = async (e, job) => {
    e.preventDefault();
    e.stopPropagation();
    
    const token = localStorage.getItem('titelli_token');
    if (!token) {
      toast.error('Connectez-vous pour postuler');
      return;
    }
    
    setSelectedJob(job);
    setApplyForm({ resume_url: '', cover_letter: '' });
    
    try {
      const res = await clientDocumentsAPI.list();
      const allDocs = res.data?.documents || res.data || [];
      const cvDocs = allDocs.filter(d => d.category === 'cv' || d.category === 'general' || d.file_type?.includes('pdf'));
      setUserDocuments(cvDocs.length > 0 ? cvDocs : allDocs);
    } catch (err) {
      console.error('Error fetching documents:', err);
      setUserDocuments([]);
    }
    
    setShowApplyModal(true);
  };
  
  // Submit application
  const handleSubmitApplication = async () => {
    if (!applyForm.resume_url) {
      toast.error('Veuillez sélectionner un CV');
      return;
    }
    
    setApplying(true);
    try {
      await jobsAPI.apply(selectedJob.id, {
        resume_url: applyForm.resume_url,
        cover_letter: applyForm.cover_letter
      });
      toast.success('Candidature envoyée avec succès !');
      setShowApplyModal(false);
    } catch (error) {
      const msg = error.response?.data?.detail || 'Erreur lors de l\'envoi';
      toast.error(msg);
    } finally {
      setApplying(false);
    }
  };

  // Handle training purchase
  const handlePurchaseTraining = async (training) => {
    const token = localStorage.getItem('titelli_token');
    if (!token) {
      toast.error('Connectez-vous pour acheter une formation');
      navigate('/auth');
      return;
    }
    
    setPurchasingTraining(training.id);
    try {
      const res = await trainingsAPI.purchase(training.id);
      if (res.data.url) {
        window.location.href = res.data.url;
      }
    } catch (error) {
      const msg = error.response?.data?.detail || 'Erreur lors de l\'achat';
      toast.error(msg);
    } finally {
      setPurchasingTraining(null);
    }
  };

  // Video state for panoramic hero
  const videoRef = useRef(null);
  const [isVideoPlaying, setIsVideoPlaying] = useState(true);
  const [isVideoMuted, setIsVideoMuted] = useState(true);

  const toggleVideoPlay = () => {
    if (videoRef.current) {
      if (isVideoPlaying) {
        videoRef.current.pause();
      } else {
        videoRef.current.play();
      }
      setIsVideoPlaying(!isVideoPlaying);
    }
  };

  const toggleVideoMute = () => {
    if (videoRef.current) {
      videoRef.current.muted = !isVideoMuted;
      setIsVideoMuted(!isVideoMuted);
    }
  };


  const enterprisesByCategory = allEnterprises.reduce((acc, enterprise) => {
    const category = enterprise.category || 'Autres';
    if (!acc[category]) acc[category] = [];
    acc[category].push(enterprise);
    return acc;
  }, {});



const advantages = [
  {
    title: "Services uniques",
    description: "Profitez de mes services unique en suisse.",
    icon: Zap
  },
  {
    title: "Video Xtreme",
    description: "Régalez vous avec mes meilleures vidoés X, Tournez depuis 2010",
    icon: Heart
  },
  {
    title: "Films X",
    description: "Régalez vous avec mes meilleures Films X, Tournez depuis 2017",
    icon: Users
  },
  {
    title: "Cashback",
    description: "Recevez du cashback lors de vos achats selon votre type d'abonnement .",
    icon: Gift
  },
  {
    title: "Particpation a mes vidéos",
    description: "Possibiliét de postuler pour tourner dans mes vidéos X.",
    icon: Shield
  },
  {
    title: "Récompenses",
    description: "Profitez de programmes de fidélité attractifs.",
    icon: Award
  },
];


  const panoramicVideoUrl = `20250821_034353.mp4`;
  const panoramicVideoUrll = `twerk.mp4`;
  const heroImage = 'https://images.unsplash.com/photo-1733950489642-bd1a7c3e69bb?w=1920&q=80';

  const mainCategories = [
    { id: 'services', label: 'Services', path: '/services', icon: Sparkles },
    { id: 'produits', label: 'Produits', path: '/products', icon: Gift },
    { id: 'certifies', label: 'Certifiés', path: '/certifies', icon: CheckCircle },
    { id: 'guests', label: 'Guests', path: '/guests', icon: Users },
  ];

return (

  <div className="min-h-screen bg-black">

    {/* Hero Section */}
    <section className="relative px-4 overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-b from-yellow-500/10 via-transparent to-transparent" />
      <div className="mx-auto relative z-10">
        <div className="text-center mb-16 z-10">
          <div className="absolute inset-0" style={{ zIndex: -38 }}>
            <video
              ref={videoRef}
              autoPlay
              muted
              loop
              playsInline
              className="w-full h-full object-cover"
         
              src={panoramicVideoUrl}
            >
              <source src={panoramicVideoUrl} type="video/mp4" />
            </video>
            <img
              src={panoramicVideoUrll}
              alt="Lausanne"
              className="absolute inset-0 w-full h-full object-cover -z-10 pt-0"
            />
          </div>
          <h1
            className="text-5xl md:text-6xl font-bold text-white mb-6 pt-3"
            style={{ fontFamily: 'Playfair Display, serif' }}
          >
            Bienvenue sur mon <span className="text-red-400">site</span>
          </h1>
        </div>




        {/* Vision & Mission */}
        <div className="grid md:grid-cols-2 mb-20">
          <div className="bg-yellow-700/10 rounded-2xl p-8 border border-yellow-500/20 meskiff" style={{ backgroundColor: 'pink', maxWidth: '500px', margin: '0 auto' }}>
            <Target className="w-12 h-12 text-yellow-800 mb-4" />
            <h2 className="text-2xl font-bold text-black mb-4">MES KIFFS ?</h2>
            <p className="text-black leading-relaxed">
              Rendre le client le plus heureux et satisfait en proposant mes services de soumission extreme, avec moi tu peut
              prendre tout le controle et evacuer tout ton stress sans limite, du soft aux services extremes je pratique de
              tout et avec passion.
            </p>
          </div>
          <div className="bg-gradient-to-br from-orange-500/10 to-red-500/10 rounded-2xl p-8 border border-orange-500/20 meskiff" style={{ backgroundColor: 'pink', maxWidth: '500px', margin: '0 auto' }}>
            <Sparkles className="w-12 h-12 text-orange-400 mb-4" />
            <h2 className="text-2xl font-bold text-black mb-4">QUE PROPOSE LE SITE ?</h2>
            <p className="text-black leading-relaxed">
              Je propose des services de soumission extreme, du soft au extreme, des vidéos tres cochonnes, du cashback, des
              offres de participations a mes vidéos et d'autre avantages !
            </p>
          </div>
        </div>




        {/* Slogan central */}
        <div className="text-center mb-20 py-12" style={{ backgroundColor: '#ffc0cb2e' }}>
          <blockquote className="text-3xl md:text-4xl font-bold text-white italic mb-4">
            "clairement la numero 1 de la Suisse Romande."
          </blockquote>
          <p className="text-white text-pink-400">« Ne cherchez plus une escort, tu l'a trouvéé ! »</p>
        </div>
      </div>
    </section>

    {/* Avantages Section */}
    <section className="pt-4 px-4 from-transparent via-gray-900/50 to-transparent">
      <div className="max-w-6xl mx-auto">
        <h2 className="text-3xl md:text-4xl font-bold text-white text-center mb-4">
          Liste <span className="text-pink-400">Avantages</span>
        </h2>
        <p className="text-gray-400 text-center mb-12 text-lg">
          Découvrez la liste complete de mes avantages et services exclusifs pour une expérience inoubliable.
        </p>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {advantages.map((adv, index) => (
            <div key={index} className="bg-gray-800/50 rounded-xl p-6 border border-gray-700 hover:border-yellow-500/50 transition-all group">
              <adv.icon className="w-10 h-10 text-pink-400 mb-4 group-hover:scale-110 transition-transform" />
              <h3 className="text-xl font-bold text-white mb-2">{adv.title}</h3>
              <p className="text-gray-400">{adv.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>

    {/* CTA Section */}
    <section className="py-20 px-4">
      <div className="max-w-4xl mx-auto text-center">
        <h2 className="text-3xl md:text-4xl font-bold text-white mb-6 pt-3">
          Prêt à rejoindre <span className="text-gradient-to-r from-pink-500 to-red-500">ma communauté</span> ?
        </h2>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            to="/auth"
            className="px-8 py-4 bg-gradient-to-r from-pink-500 to-red-500 text-black font-bold rounded-xl hover:from-yellow-600 hover:to-orange-600 transition-all flex items-center justify-center gap-2"
          >
            je te veut !
          </Link>
    
        </div>
      </div>
    </section>








  <section className="relative h-screen overflow-hidden pt-0" data-testid="hero-section" style={{height:'500px'}}>
        {/* Video Background - No overlay, no gradient */}
        <div className="absolute inset-0">
          <video
            ref={videoRef}
            autoPlay
            muted
            loop
            playsInline
            className="w-full h-full object-cover"
            poster={heroImage}
          >
            <source src={panoramicVideoUrll} type="video/mp4" />
          </video>
          <img 
            src={heroImage} 
            alt="Lausanne" 
            className="absolute inset-0 w-full h-full object-cover -z-10 pt-0"
          />
        </div>

        {/* Hero Content - Just title, no logo, no description */}
        <div className="absolute inset-0 flex flex-col justify-center items-center text-center px-4">
          <h1 className="text-4xl sm:text-5xl lg:text-7xl font-bold text-white mb-8 animate-fade-in drop-shadow-lg" style={{ fontFamily: 'Playfair Display, serif' }}>
            La meilleure soumise<br />
            <span style={{ color: 'pink' }}>de ta Région</span>
          </h1>
   {/* Category Buttons - 2 rows */}
          <div className="flex flex-col items-start gap-1 animate-fade-in stagger-2 min-w-[106px] max-w[400px] ">
            <div className="flex flex-wrap justify-start gap-2 min-w-[106px] divbout">
              {[
                { label: 'Vidéos', path: '/products' },
                { label: 'Scénarios', path: '/entreprises' },
                { label: 'Tendances', path: '/labellises' },
                { label: 'Tournages', path: '/emplois' },

              ].map((cat) => (
                <Link
                  key={cat.label}
                  to={cat.path}
                  className="px-4 py-2 bg-black/80 backdrop-blur-md border border-white/20 rounded-[10px] text-white text-sm hover:bg-white hover:text-black transition-all duration-300 min-w-[106px]"
                >
                  {cat.label}
                </Link>
              ))}
            </div>
     <div className="flex justify-center gap-2 min-w-[106px] mt-1 w-[100%] bout">
              {[
                { label: 'V.I.P', path: '/dashboard/client' },
              

              ].map((cat) => (
                <Link
                  key={cat.label}
                  to={cat.path}
                  className="px-4 py-2 bg-pink-400 backdrop-blur-md border border-white/20 rounded-[10px] text-white text-sm hover:bg-white hover:text-black transition-all duration-300 min-w-[100%]"
                >
                  {cat.label}
                </Link>
              ))}
            </div>
          </div>
      </div>
      </section>

      {/* Simple transition */}
      

      {/* Search Bar Section - Under Video */}
      <section className="py-4 sm:py-6 bg-pink-100" data-testid="search-section">
        <div className="max-w-2xl mx-auto px-4">
          <form onSubmit={handleSearch} className="relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Rechercher une vidéo, un film, un tournage..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-20 py-2.5 bg-gray-50 border border-gray-200 rounded-full text-sm text-gray-900 placeholder:text-gray-400 focus:outline-none focus:border-[#0047AB] focus:bg-white transition-all"
              data-testid="home-search-input"
            />
            <button 
              type="submit"
              className="absolute right-1.5 top-1/2 -translate-y-1/2 bg-[#0047AB] text-white px-4 py-1.5 rounded-full text-xs font-medium hover:bg-[#0047AB]/90 transition-colors"
            >
              Rechercher
            </button>
          </form>
        </div>
      </section>

      {/* Les meilleurs prestataires Section - Carousel */}
        {/* Les meilleurs prestataires Section - Grid 5 columns */}
      <section className="py-8 sm:py-12 bg-pink-100" data-testid="top-providers-section">
        <div className="max-w-7xl mx-auto px-4 md:px-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg sm:text-2xl md:text-3xl font-semibold text-gray-900">
              Scénarios <span className="text-[#dc3545]">X </span>
            </h2>
            <Link to="/entreprises" className="hidden md:flex items-center gap-2 text-[#0047AB] hover:text-[#2E74D6] font-medium transition-colors">
              Voir tout
              <ArrowRight className="w-5 h-5" />
            </Link>
          </div>


          {loading ? (
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 sm:gap-4">
              {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20].map((i) => (
                <div key={i} className="h-[240px] sm:h-[280px] bg-gray-100 rounded-xl animate-pulse" />
              ))}
            </div>
          ) : allEnterprises.length > 0 ? (
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 sm:gap-4">
        {allEnterprises.map((enterprise) => (
              <EnterpriseCard
                key={enterprise.id}
                enterprise={enterprise}
              />
            ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8 text-sm">Aucun prestataire avec photo disponible</p>
          )}

          <Link to="/entreprises" className="md:hidden flex items-center justify-center gap-2 mt-4 sm:mt-6 text-[#0047AB] font-medium text-sm">
            Voir tous les prestataires
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </section>
      

      {/* Les meilleurs produits - Real Product Cards */}
      <section className="py-8 sm:py-16 bg-pink-100" data-testid="products-section">
        <div className="max-w-7xl mx-auto px-4 md:px-8">
          <div className="flex items-center justify-between mb-6 sm:mb-8">
            <div>
              <h2 className="text-lg sm:text-2xl md:text-3xl font-semibold text-gray-900">
                Mes videos <span className="text-[#dc3545]">X </span>
              </h2>
            </div>
            <Link to="/products" className="hidden md:flex items-center gap-2 text-[#0047AB] hover:text-[#2E74D6] font-medium transition-colors">
              Voir tout
              <ArrowRight className="w-5 h-5" />
            </Link>
          </div>

          {loading ? (
            <div className="flex gap-4 sm:gap-6 overflow-hidden">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="flex-shrink-0 w-[260px] sm:w-[300px] h-[320px] bg-gray-100 rounded-xl animate-pulse" />
              ))}
            </div>
          ) : bestProducts.length > 0 ? (
            <Carousel itemWidth={260}>
              {bestProducts.map((product, index) => (
                <div 
                  key={product.id || product._id} 
                  className="flex-shrink-0 w-[260px] sm:w-[300px] animate-fade-in"
                  style={{ animationDelay: `${index * 0.05}s` }}
                >
                  <ServiceProductCard item={product} />
                </div>
              ))}
            </Carousel>
          ) : (
            /* Fallback to category cards if no products with images */
            <Carousel itemWidth={220}>
              {bestProducts.map((product, index) => (
                <Link
                  key={product.id}
                  to={`/products?category=${product.id}`}
                  className="flex-shrink-0 w-[200px] sm:w-[220px] group relative h-56 sm:h-64 rounded-2xl overflow-hidden shadow-md hover:shadow-xl transition-all"
                  data-testid={`product-cat-${product.id}`}
                >
                  <img 
                    src={product.image} 
                    alt={product.name}
                    className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/20 to-transparent" />
                  <div className="absolute bottom-0 left-0 right-0 p-4">
                    <span className="text-white font-semibold text-base">{product.name}</span>
                  </div>
                </Link>
              ))}
            </Carousel>
          )}

          <Link to="/products" className="md:hidden flex items-center justify-center gap-2 mt-4 sm:mt-6 text-[#0047AB] font-medium text-sm">
            Voir tous les produits
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </section>

      {/* Tendances Actuelles - Carousel */}
      {tendances.length > 0 && (
        <section className="py-8 sm:py-16 bg-pink-100" data-testid="tendances-section">
          <div className="max-w-7xl mx-auto px-4 md:px-8">
            <div className="flex items-center justify-between mb-6 sm:mb-8">
              <div>
                <h2 className="text-lg sm:text-2xl md:text-3xl font-semibold text-gray-900">
                  Scénarios les plus populaires <span className="text-[#dc3545]">X </span>
                </h2>
              </div>
              <Link to="/labellises" className="hidden md:flex items-center gap-2 text-[#0047AB] hover:text-[#2E74D6] font-medium transition-colors">
                Voir tout
                <ArrowRight className="w-5 h-5" />
              </Link>
            </div>

            <Carousel itemWidth={280}>
              {tendances.map((enterprise, index) => (
                <div key={enterprise.id} className="flex-shrink-0 w-[280px] sm:w-[320px]">
                  <EnterpriseCard enterprise={enterprise} />
                </div>
              ))}
            </Carousel>
          </div>
        </section>
      )}

   

      {/* Premium Section - Carousel */}


      {/* Job Offers Section - Carousel */}
      <section className="py-8 sm:py-16 bg-pink-100" data-testid="jobs-section">
        <div className="max-w-7xl mx-auto px-4 md:px-8">
          <div className="flex items-center justify-between mb-4 sm:mb-6">
            <div>
              <h2 className="text-lg sm:text-2xl md:text-3xl font-semibold text-gray-900">
                Offres de participations aux vidéos
              </h2>
            </div>
            <div className="flex items-center gap-2 sm:gap-3">
              <button 
                onClick={() => setShowFilters(!showFilters)}
                className={`flex items-center gap-1 sm:gap-2 px-2 sm:px-4 py-1.5 sm:py-2 rounded-lg text-xs sm:text-sm transition-colors ${showFilters ? 'bg-[#0047AB] text-white' : 'bg-white text-gray-700 border border-gray-200 hover:bg-gray-50'}`}
                data-testid="jobs-filter-btn"
              >
                <Filter className="w-3 h-3 sm:w-4 sm:h-4" />
                <span className="hidden sm:inline">Filtres</span>
              </button>
              <Link to="/emplois" className="hidden md:flex items-center gap-2 text-[#0047AB] hover:text-[#2E74D6] font-medium transition-colors">
                Voir tout
                <ArrowRight className="w-5 h-5" />
              </Link>
            </div>
          </div>
          
          {/* Filters */}
          {showFilters && (
            <div className="mb-4 sm:mb-6 p-3 sm:p-5 bg-white rounded-xl border border-gray-200 shadow-sm animate-fade-in" data-testid="jobs-filters">
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
                <div>
                  <label className="block text-xs sm:text-sm text-gray-600 mb-1.5 sm:mb-2">Type</label>
                  <select 
                    value={jobFilters.type}
                    onChange={(e) => setJobFilters({...jobFilters, type: e.target.value})}
                    className="w-full bg-gray-50 border border-gray-200 rounded-lg px-2 sm:px-4 py-2 text-xs sm:text-sm text-gray-900 focus:border-[#0047AB] outline-none"
                    data-testid="jobs-filter-type"
                  >
                    <option value="">Tous</option>
                    <option value="CDI">CDI</option>
                    <option value="CDD">CDD</option>
                    <option value="Stage">Stage</option>
                    <option value="Freelance">Freelance</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs sm:text-sm text-gray-600 mb-1.5 sm:mb-2">Ville</label>
                  <input 
                    type="text"
                    value={jobFilters.location}
                    onChange={(e) => setJobFilters({...jobFilters, location: e.target.value})}
                    placeholder="Lausanne..."
                    className="w-full bg-gray-50 border border-gray-200 rounded-lg px-2 sm:px-4 py-2 text-xs sm:text-sm text-gray-900 placeholder-gray-500 focus:border-[#0047AB] outline-none"
                    data-testid="jobs-filter-location"
                  />
                </div>
                <div className="col-span-2 lg:col-span-1">
                  <label className="block text-xs sm:text-sm text-gray-600 mb-1.5 sm:mb-2">Entreprise</label>
                  <input 
                    type="text"
                    value={jobFilters.enterprise}
                    onChange={(e) => setJobFilters({...jobFilters, enterprise: e.target.value})}
                    placeholder="Nom..."
                    className="w-full bg-gray-50 border border-gray-200 rounded-lg px-2 sm:px-4 py-2 text-xs sm:text-sm text-gray-900 placeholder-gray-500 focus:border-[#0047AB] outline-none"
                    data-testid="jobs-filter-enterprise"
                  />
                </div>
                <div className="flex items-end col-span-2 lg:col-span-1">
                  <button 
                    onClick={() => setJobFilters({ type: '', location: '', enterprise: '' })}
                    className="w-full px-3 sm:px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg text-xs sm:text-sm text-gray-700 hover:text-gray-900 transition-colors"
                  >
                    Réinitialiser
                  </button>
                </div>
              </div>
              {filteredJobs.length !== jobs.length && (
                <p className="mt-3 sm:mt-4 text-xs sm:text-sm text-[#0047AB]">{filteredJobs.length} résultat(s) sur {jobs.length}</p>
              )}
            </div>
          )}

          {filteredJobs.length > 0 ? (
            <Carousel itemWidth={280}>
              {filteredJobs.slice(0, 9).map((job, index) => (
                <div 
                  key={job.id} 
                  className="flex-shrink-0 w-[280px] sm:w-[320px] bg-white rounded-xl p-3 sm:p-5 border border-gray-200 shadow-sm hover:border-[#0047AB]/30 hover:shadow-md transition-all"
                  data-testid={`job-card-${job.id}`}
                >
                  <Link to={`/emploi/${job.id}`} className="block">
                    <div className="flex items-start justify-between mb-2 sm:mb-3 gap-2">
                      <div className="flex items-center gap-2 sm:gap-3 min-w-0">
                        <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-lg bg-[#0047AB]/10 flex items-center justify-center flex-shrink-0">
                          <Briefcase className="w-5 h-5 sm:w-6 sm:h-6 text-[#0047AB]" />
                        </div>
                        <div className="min-w-0">
                          <h3 className="text-gray-900 font-semibold text-xs sm:text-sm line-clamp-1">{job.title}</h3>
                          <p className="text-[#D4AF37] text-xs sm:text-sm font-medium line-clamp-1">{job.enterprise_name || 'Entreprise'}</p>
                        </div>
                      </div>
                      <span className={`text-[10px] sm:text-xs px-1.5 sm:px-2 py-0.5 sm:py-1 rounded-full flex-shrink-0 ${
                        job.type === 'CDI' ? 'bg-green-100 text-green-700' :
                        job.type === 'CDD' ? 'bg-orange-100 text-orange-700' :
                        job.type === 'Stage' ? 'bg-purple-100 text-purple-700' :
                        job.type === 'Freelance' ? 'bg-cyan-100 text-cyan-700' :
                        'bg-blue-100 text-blue-700'
                      }`}>
                        {job.type || 'CDI'}
                      </span>
                    </div>
                    <p className="text-gray-600 text-xs sm:text-sm line-clamp-2 mb-3 sm:mb-4">{job.description}</p>
                    <div className="flex items-center gap-3 sm:gap-4 text-[10px] sm:text-xs text-gray-500 mb-3 sm:mb-4">
                      <span className="flex items-center gap-1">
                        <MapPin className="w-3 h-3" /> {job.location || 'Lausanne'}
                      </span>
                    </div>
                  </Link>
                  <button
                    onClick={(e) => handleApplyClick(e, job)}
                    className="w-full bg-[#0047AB] hover:bg-[#0047AB]/80 text-white px-3 sm:px-4 py-1.5 sm:py-2 rounded-lg text-xs sm:text-sm font-medium transition-colors flex items-center justify-center gap-1.5 sm:gap-2"
                    data-testid={`job-apply-btn-${job.id}`}
                  >
                    <Send className="w-3 h-3 sm:w-4 sm:h-4" />
                    Postuler
                  </button>
                </div>
              ))}
            </Carousel>
          ) : (
            <div className="text-center py-8 sm:py-12">
              <Briefcase className="w-12 h-12 sm:w-16 sm:h-16 text-gray-300 mx-auto mb-3 sm:mb-4" />
              <p className="text-gray-600 text-sm">
                {jobs.length === 0 ? "Aucune offre pour le moment" : "Aucune offre ne correspond"}
              </p>
            </div>
          )}

          <Link to="/emplois" className="md:hidden flex items-center justify-center gap-2 mt-4 sm:mt-8 text-[#0047AB] font-medium text-sm">
            Voir toutes les offres
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </section>

      
      {/* Apply Modal */}
      {showApplyModal && selectedJob && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4" data-testid="apply-modal">
          <div className="bg-[#0A0A0A] rounded-2xl w-full max-w-lg border border-white/10 max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-white/10">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-bold text-white">Postuler à l'offre</h2>
                <button onClick={() => setShowApplyModal(false)} className="text-gray-400 hover:text-white">
                  <X className="w-6 h-6" />
                </button>
              </div>
            </div>
            
            <div className="p-6 space-y-6">
              <div className="bg-white/5 rounded-xl p-4">
                <h3 className="text-white font-semibold">{selectedJob.title}</h3>
                <p className="text-[#D4AF37] text-sm">{selectedJob.enterprise_name}</p>
                <div className="flex items-center gap-4 text-xs text-gray-400 mt-2">
                  <span>{selectedJob.type}</span>
                  <span>{selectedJob.location || 'Lausanne'}</span>
                </div>
              </div>
              
              <div>
                <label className="block text-sm text-gray-400 mb-2">
                  <FileText className="w-4 h-4 inline mr-2" />
                  Sélectionnez Une foto de vous face de devant (si possible nue) *
                </label>
                {userDocuments.length > 0 ? (
                  <div className="space-y-2">
                    {userDocuments.map((doc) => (
                      <label 
                        key={doc.id} 
                        className={`flex items-center gap-3 p-3 rounded-lg cursor-pointer transition-colors ${
                          applyForm.resume_url === doc.url 
                            ? 'bg-[#0047AB]/20 border border-[#0047AB]' 
                            : 'bg-white/5 border border-white/10 hover:bg-white/10'
                        }`}
                      >
                        <input
                          type="radio"
                          name="resume"
                          value={doc.url}
                          checked={applyForm.resume_url === doc.url}
                          onChange={(e) => setApplyForm({...applyForm, resume_url: e.target.value})}
                          className="accent-[#0047AB]"
                        />
                        <FileText className="w-5 h-5 text-[#0047AB]" />
                        <div className="flex-1">
                          <span className="text-white text-sm">{doc.name}</span>
                          <span className="text-xs text-gray-500 ml-2">({doc.category})</span>
                        </div>
                      </label>
                    ))}
                  </div>
                )
                : (
                  <div className="text-center p-6 bg-white/5 rounded-xl">
                    <FileText className="w-12 h-12 text-gray-500 mx-auto mb-3" />
                    <p className="text-gray-400 text-sm mb-3">Vous n'avez pas encore de CV enregistré</p>
                    <Link 
                      to={`/dashboard/client?tab=documents&returnToJob=${selectedJob.id}`}
                      className="text-[#0047AB] hover:underline text-sm"
                      onClick={() => setShowApplyModal(false)}
                    >
                      Ajouter un CV dans mon espace
                    </Link>
                  </div>
                )}
              </div>
              
              <div>
                <label className="block text-sm text-gray-400 mb-2">Petite présentation ? (optionnel)</label>
                <textarea
                  value={applyForm.cover_letter}
                  onChange={(e) => setApplyForm({...applyForm, cover_letter: e.target.value})}
                  placeholder="Présentez-vous brièvement et expliquez votre motivation..."
                  className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:border-[#0047AB] outline-none h-32 resize-none"
                  data-testid="apply-cover-letter"
                />
              </div>
              
              <div className="flex gap-3">
                <button
                  onClick={() => setShowApplyModal(false)}
                  className="flex-1 px-4 py-3 rounded-xl bg-white/10 text-white hover:bg-white/20 transition-colors"
                >
                  Annuler
                </button>
                <button
                  onClick={handleSubmitApplication}
                  disabled={applying || !applyForm.resume_url}
                  className="flex-1 px-4 py-3 rounded-xl bg-[#0047AB] text-white hover:bg-[#0047AB]/80 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                  data-testid="apply-submit-btn"
                >
                  {applying ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      Envoi...
                    </>
                  ) : (
                    <>
                      <Send className="w-4 h-4" />
                      Envoyer ma candidature
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Scrolling Reviews Section */}
      <ScrollingReviews 
        title="Ce que pense mes clients !"
        speed={35}
      />


      {/* CTA Section */}
      <section className="py-12 sm:py-20 md:py-28 bg-[pink]" data-testid="cta-section">
        <div className="max-w-4xl mx-auto px-4 md:px-8 text-center">
          <h2 className="text-xl sm:text-3xl md:text-4xl font-bold text-black mb-4 sm:mb-6" style={{ fontFamily: 'Playfair Display, serif' }}>
            Tu veut tourner une vidéo X avec moi ?  </h2>
          <p className="text-sm sm:text-lg text-black/80 mb-6 sm:mb-10 max-w-2xl mx-auto">
            Rejoignez Titelli et développez votre activité avec une visibilité premium.
          </p>
          <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 justify-center">
            <Link to="/auth?type=entreprise" className="bg-white text-[#0047AB] text-sm sm:text-lg px-6 sm:px-10 py-3 sm:py-4 rounded-lg font-semibold hover:bg-gray-100 transition-colors" data-testid="cta-register-btn">
              Inscription
            </Link>
  
          </div>
        </div>
      </section>
    </div>
  );
};

export default HomePage;
