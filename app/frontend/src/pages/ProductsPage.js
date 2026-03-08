import React, { useState, useEffect } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { Grid, List } from 'lucide-react';
import { categoryAPI, servicesProductsAPI, enterpriseAPI } from '../services/api';
import { useCart } from '../context/CartContext';
import ServiceProductCard from '../components/ServiceProductCard';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../components/ui/select';

const ProductsPage = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const { addItem } = useCart();
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [enterprises, setEnterprises] = useState({});
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [viewMode, setViewMode] = useState('grid');
  
  const selectedCategory = searchParams.get('category') || '';

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const response = await categoryAPI.products();
        setCategories(response.data);
      } catch (error) {
        console.error('Error fetching categories:', error);
      }
    };
    fetchCategories();
  }, []);

  useEffect(() => {
    const fetchProducts = async () => {
      setLoading(true);
      try {
        const params = { type: 'product' };
        if (selectedCategory) params.category = selectedCategory;
        
        const response = await servicesProductsAPI.list(params);
        setProducts(response.data.items);
        setTotal(response.data.total);

        // Fetch enterprises for products
        const enterpriseIds = [...new Set(response.data.items.map(p => p.enterprise_id))];
        const enterprisesMap = {};
        for (const eid of enterpriseIds) {
          try {
            const entRes = await enterpriseAPI.getById(eid);
            enterprisesMap[eid] = entRes.data;
          } catch (e) {
            console.error('Error fetching enterprise:', e);
          }
        }
        setEnterprises(enterprisesMap);
      } catch (error) {
        console.error('Error fetching products:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchProducts();
  }, [selectedCategory]);

  const handleCategoryChange = (value) => {
    if (value === 'all') {
      searchParams.delete('category');
    } else {
      searchParams.set('category', value);
    }
    setSearchParams(searchParams);
  };

  const handleAddToCart = (item) => {
    const enterprise = enterprises[item.enterprise_id];
    addItem(item, enterprise);
  };

const abo = 'https://esclavaescort.ch/vip.php';
const vid = 'bg.mp4'

  return (
    <div className="min-h-screen bg-[#050505]" data-testid="products-page">
      {/* Hero with Video Background - Generated with Sora 2 AI */}
      <div className="relative h-[40vh] min-h-[300px] overflow-hidden">
        {/* Video Background */}
        <div className="absolute inset-0">
          <video
            autoPlay
            muted
            loop
            playsInline
            className="w-full h-full object-cover"
            poster={vid}
            src={vid}
          >
            <source src={`${process.env.REACT_APP_BACKEND_URL}/api/uploads/video_produits_v2.mp4`} type="video/mp4" />
          </video>
          <div className="absolute inset-0 bg-gradient-to-b from-[#050505]/70 via-[#050505]/50 to-[#050505]" />
        </div>
       
        {/* Content */}
        <div className="relative h-full flex items-center">
          <div className="max-w-7xl mx-auto px-4 md:px-8 w-full">
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-white mb-4" style={{ fontFamily: 'Playfair Display, serif' }}>
             Mes Videos  <span style={{color: 'red'}}>X</span>
            </h1>
            <p className="text-lg md:text-xl text-gray-300 max-w-2xl">
              Les meilleurs videos de soumission de la région, à portée de clic.
            </p>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="max-w-7xl mx-auto px-4 md:px-8 py-6 flex items-center gap-4">
        <Select onValueChange={handleCategoryChange} defaultValue={selectedCategory || 'all'}>
          <SelectTrigger className="w-48">
            <SelectValue placeholder="Filtrer par catégorie" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Toutes les catégories</SelectItem>
            {categories.map((cat) => (
              <SelectItem key={cat.id} value={cat.id}>{cat.name}</SelectItem>
            ))}
          </SelectContent>
        </Select>

          {/* View Toggle & Count */}
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-400">{total} résultats</span>
            <div className="flex items-center gap-1 bg-white/5 rounded-lg p-1">
              <button
                onClick={() => setViewMode('grid')}
                className={`p-2 rounded-md transition-colors ${viewMode === 'grid' ? 'bg-white/10 text-white' : 'text-gray-400'}`}
              >
                <Grid className="w-4 h-4" />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`p-2 rounded-md transition-colors ${viewMode === 'list' ? 'bg-white/10 text-white' : 'text-gray-400'}`}
              >
                <List className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>

        {/* Products Grid */}
        {loading ? (
          <div className="grid grid-cols-1  lg:grid-cols-3 gap-6" >

            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div key={i} className="card-service rounded-xl h-80 animate-pulse" />
            ))}
          </div>
        ) : products.length > 0 ? (
          <div style={{maxWidth: '1200px !important'}} className={viewMode === 'grid' 
            ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6'
            : 'flex flex-col gap-4'
          }>
            {products.map((product, index) => (
              <div key={product.id} className={`animate-fade-in stagger-${(index % 6) + 1}`}>
                <ServiceProductCard item={product} onAddToCart={handleAddToCart} />
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-20">
            <p className="text-gray-400 text-lg mb-4">Aucun produit trouvé</p>
            <button 
              onClick={() => handleCategoryChange('all')}
              className="btn-secondary"
            >
              Voir tous les produits
            </button>
          </div>
        )}


   {/* All Categories */}
        <div className="mt-16 text-center">
          <h2 className="text-2xl font-bold text-white mb-8 justify-center" style={{ fontFamily: 'Playfair Display, serif' }}>
            Pour voir toutes les vidéos illimités , devenez VIP ! 
          </h2>
          <button>   <Link 
              to={abo}
              className="px-8 py-4 bg-gradient-to-r from-pink-500 to-red-500 text-black font-bold rounded-xl hover:from-yellow-600 hover:to-orange-600 transition-all flex items-center justify-center gap-2"
            >
              je Devien VIP ! <div className="w-5 h-5" />
            </Link></button>
        </div>


      </div>
    
  );
};

export default ProductsPage;
