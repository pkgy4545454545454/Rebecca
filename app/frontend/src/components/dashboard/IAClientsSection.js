import React, { useState, useEffect } from 'react';
import { Target, Trash2, Users, Send, Search, Filter, MessageSquare, ShoppingCart, User, CheckCircle, X } from 'lucide-react';
import { iaCampaignsAPI, enterpriseCustomersAPI, servicesProductsAPI } from '../../services/api';
import { toast } from 'sonner';

const IAClientsSection = () => {
  const [targetAudience, setTargetAudience] = useState({
    name: '',
    age_range: '25-45',
    gender: 'all',
    interests: [],
    location: 'lausanne',
    budget: 'medium',
    behavior: []
  });
  const [campaigns, setCampaigns] = useState([]);
  const [stats, setStats] = useState({ total_reach: 0, total_engagement: 0, total_conversions: 0, engagement_rate: 0, real_customers: 0 });
  const [showCreate, setShowCreate] = useState(false);
  const [loading, setLoading] = useState(true);
  
  // Real customer targeting
  const [customers, setCustomers] = useState([]);
  const [customerStats, setCustomerStats] = useState({});
  const [selectedCustomers, setSelectedCustomers] = useState([]);
  const [showQuestionModal, setShowQuestionModal] = useState(false);
  const [question, setQuestion] = useState('');
  const [sendingQuestion, setSendingQuestion] = useState(false);
  
  // Filters
  const [customerFilter, setCustomerFilter] = useState({
    type: 'all',
    search: '',
    productId: '',
    serviceId: ''
  });
  const [services, setServices] = useState([]);

  const interests = [
    'Bien-être', 'Mode', 'Gastronomie', 'Sport', 'Technologie', 
    'Voyage', 'Art & Culture', 'Famille', 'Business', 'Écologie'
  ];

  const behaviors = [
    'Acheteurs fréquents', 'Nouveaux clients', 'Clients fidèles',
    'Abandons de panier', 'Visiteurs réguliers', 'Clients premium'
  ];

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    fetchCustomers();
  }, [customerFilter]);

  const fetchData = async () => {
    try {
      const [campaignsRes, servicesRes] = await Promise.all([
        iaCampaignsAPI.list(),
        servicesProductsAPI.list({}).catch(() => ({ data: { items: [] } }))
      ]);
      setCampaigns(campaignsRes.data.campaigns || []);
      setStats(campaignsRes.data.stats || {});
      setServices(servicesRes.data.items || []);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchCustomers = async () => {
    try {
      const params = {};
      if (customerFilter.type !== 'all') params.filter_type = customerFilter.type;
      if (customerFilter.search) params.search = customerFilter.search;
      if (customerFilter.productId) params.product_id = customerFilter.productId;
      if (customerFilter.serviceId) params.service_id = customerFilter.serviceId;
      
      const response = await enterpriseCustomersAPI.list(params);
      setCustomers(response.data.customers || []);
      setCustomerStats(response.data.stats || {});
    } catch (error) {
      console.error('Error fetching customers:', error);
    }
  };

  const handleInterestToggle = (interest) => {
    setTargetAudience(prev => ({
      ...prev,
      interests: prev.interests.includes(interest)
        ? prev.interests.filter(i => i !== interest)
        : [...prev.interests, interest]
    }));
  };

  const handleBehaviorToggle = (behavior) => {
    setTargetAudience(prev => ({
      ...prev,
      behavior: prev.behavior.includes(behavior)
        ? prev.behavior.filter(b => b !== behavior)
        : [...prev.behavior, behavior]
    }));
  };

  const createCampaign = async () => {
    if (!targetAudience.name) {
      toast.error('Veuillez donner un nom à votre campagne');
      return;
    }
    try {
      const response = await iaCampaignsAPI.create(targetAudience);
      setCampaigns([response.data, ...campaigns]);
      setShowCreate(false);
      setTargetAudience({ name: '', age_range: '25-45', gender: 'all', interests: [], location: 'lausanne', budget: 'medium', behavior: [] });
      toast.success('Campagne IA créée avec succès');
      fetchData();
    } catch (error) {
      toast.error('Erreur lors de la création de la campagne');
    }
  };

  const toggleCampaign = async (campaignId) => {
    try {
      await iaCampaignsAPI.toggle(campaignId);
      fetchData();
      toast.success('Statut de la campagne mis à jour');
    } catch (error) {
      toast.error('Erreur lors de la mise à jour');
    }
  };

  const deleteCampaign = async (campaignId) => {
    try {
      await iaCampaignsAPI.delete(campaignId);
      setCampaigns(campaigns.filter(c => c.id !== campaignId));
      toast.success('Campagne supprimée');
    } catch (error) {
      toast.error('Erreur lors de la suppression');
    }
  };

  const toggleCustomerSelection = (customerId) => {
    setSelectedCustomers(prev => 
      prev.includes(customerId)
        ? prev.filter(id => id !== customerId)
        : [...prev, customerId]
    );
  };

  const selectAllCustomers = () => {
    if (selectedCustomers.length === customers.length) {
      setSelectedCustomers([]);
    } else {
      setSelectedCustomers(customers.map(c => c.id));
    }
  };

  const sendQuestion = async () => {
    if (!question.trim()) {
      toast.error('Veuillez entrer une question');
      return;
    }
    if (selectedCustomers.length === 0) {
      toast.error('Veuillez sélectionner au moins un client');
      return;
    }
    
    setSendingQuestion(true);
    try {
      const response = await enterpriseCustomersAPI.sendQuestion({
        question: question,
        customer_ids: selectedCustomers
      });
      toast.success(response.data.message);
      setShowQuestionModal(false);
      setQuestion('');
      setSelectedCustomers([]);
    } catch (error) {
      toast.error('Erreur lors de l\'envoi');
    } finally {
      setSendingQuestion(false);
    }
  };

  const formatNumber = (num) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num?.toString() || '0';
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return 'N/A';
    return new Date(dateStr).toLocaleDateString('fr-CH', { day: 'numeric', month: 'short', year: 'numeric' });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="w-10 h-10 border-4 border-[#0047AB] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="ia-clients-section">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
            IA Ciblage Clients
          </h1>
          <p className="text-gray-400 mt-1">Ciblez vos vrais clients basé sur leurs achats</p>
        </div>
        <div className="flex gap-2">
          <button 
            onClick={() => setShowQuestionModal(true)} 
            disabled={selectedCustomers.length === 0}
            className="btn-secondary flex items-center gap-2 disabled:opacity-50"
          >
            <MessageSquare className="w-4 h-4" /> 
            Envoyer question ({selectedCustomers.length})
          </button>
          <button onClick={() => setShowCreate(true)} className="btn-primary flex items-center gap-2">
            <Target className="w-4 h-4" /> Nouveau ciblage
          </button>
        </div>
      </div>

      {/* Real Stats from Database */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div className="card-service rounded-xl p-4">
          <p className="text-sm text-gray-400">Clients réels</p>
          <p className="text-2xl font-bold text-[#0047AB]">{customerStats.total_customers || 0}</p>
        </div>
        <div className="card-service rounded-xl p-4">
          <p className="text-sm text-gray-400">Clients fidèles</p>
          <p className="text-2xl font-bold text-green-400">{customerStats.frequent_customers || 0}</p>
        </div>
        <div className="card-service rounded-xl p-4">
          <p className="text-sm text-gray-400">Conversions</p>
          <p className="text-2xl font-bold text-[#D4AF37]">{stats.total_conversions || 0}</p>
        </div>
        <div className="card-service rounded-xl p-4">
          <p className="text-sm text-gray-400">Revenu total</p>
          <p className="text-2xl font-bold text-purple-400">{formatNumber(customerStats.total_revenue || 0)} CHF</p>
        </div>
        <div className="card-service rounded-xl p-4">
          <p className="text-sm text-gray-400">Campagnes actives</p>
          <p className="text-2xl font-bold text-cyan-400">{stats.active_campaigns || 0}</p>
        </div>
      </div>

      {/* Customer Targeting Section */}
      <div className="card-service rounded-xl p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-white flex items-center gap-2">
            <Users className="w-5 h-5 text-[#0047AB]" />
            Mes Clients (Ciblage Réel)
          </h2>
          <div className="flex items-center gap-2">
            <button 
              onClick={selectAllCustomers}
              className="text-sm text-[#0047AB] hover:underline"
            >
              {selectedCustomers.length === customers.length ? 'Désélectionner tout' : 'Sélectionner tout'}
            </button>
          </div>
        </div>

        {/* Filters */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-3 mb-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
            <input
              type="text"
              placeholder="Rechercher par nom..."
              value={customerFilter.search}
              onChange={(e) => setCustomerFilter({...customerFilter, search: e.target.value})}
              className="w-full pl-10 pr-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-500"
            />
          </div>
          <select
            value={customerFilter.type}
            onChange={(e) => setCustomerFilter({...customerFilter, type: e.target.value})}
            className="bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white"
          >
            <option value="all">Tous les clients</option>
            <option value="frequent">Clients fidèles (3+ achats)</option>
            <option value="recent">Clients récents (30 jours)</option>
          </select>
          <select
            value={customerFilter.productId}
            onChange={(e) => setCustomerFilter({...customerFilter, productId: e.target.value, serviceId: ''})}
            className="bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white"
          >
            <option value="">Filtrer par produit/service</option>
            {services.map(s => (
              <option key={s.id} value={s.id}>{s.name}</option>
            ))}
          </select>
          <button 
            onClick={() => setCustomerFilter({ type: 'all', search: '', productId: '', serviceId: '' })}
            className="px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg text-gray-300"
          >
            Réinitialiser
          </button>
        </div>

        {/* Customer List */}
        {customers.length > 0 ? (
          <div className="space-y-2 max-h-[400px] overflow-y-auto">
            {customers.map((customer) => (
              <div 
                key={customer.id} 
                onClick={() => toggleCustomerSelection(customer.id)}
                className={`p-4 rounded-xl cursor-pointer transition-all flex items-center justify-between ${
                  selectedCustomers.includes(customer.id) 
                    ? 'bg-[#0047AB]/20 border border-[#0047AB]' 
                    : 'bg-white/5 hover:bg-white/10 border border-transparent'
                }`}
              >
                <div className="flex items-center gap-3">
                  <div className={`w-5 h-5 rounded border-2 flex items-center justify-center ${
                    selectedCustomers.includes(customer.id) ? 'bg-[#0047AB] border-[#0047AB]' : 'border-gray-500'
                  }`}>
                    {selectedCustomers.includes(customer.id) && <CheckCircle className="w-4 h-4 text-white" />}
                  </div>
                  <div className="w-10 h-10 rounded-full bg-[#0047AB]/20 flex items-center justify-center">
                    {customer.profile_image ? (
                      <img src={customer.profile_image} alt="" className="w-10 h-10 rounded-full object-cover" />
                    ) : (
                      <User className="w-5 h-5 text-[#0047AB]" />
                    )}
                  </div>
                  <div>
                    <p className="text-white font-medium">{customer.first_name} {customer.last_name}</p>
                    <p className="text-sm text-gray-400">{customer.email}</p>
                  </div>
                </div>
                <div className="flex items-center gap-6 text-sm">
                  <div className="text-center">
                    <p className="text-[#0047AB] font-semibold">{customer.orders_count}</p>
                    <p className="text-xs text-gray-500">commandes</p>
                  </div>
                  <div className="text-center">
                    <p className="text-[#D4AF37] font-semibold">{customer.total_spent} CHF</p>
                    <p className="text-xs text-gray-500">dépensé</p>
                  </div>
                  <div className="text-center">
                    <p className="text-gray-300">{formatDate(customer.last_order_date)}</p>
                    <p className="text-xs text-gray-500">dernière commande</p>
                  </div>
                  {customer.is_frequent && (
                    <span className="px-2 py-1 bg-green-500/20 text-green-400 rounded text-xs">Fidèle</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <Users className="w-12 h-12 text-gray-500 mx-auto mb-3" />
            <p className="text-gray-400">Aucun client trouvé</p>
            <p className="text-sm text-gray-500">Les clients apparaîtront ici après leurs premières commandes</p>
          </div>
        )}
      </div>

      {/* Campaigns Section */}
      <div className="card-service rounded-xl p-6">
        <h2 className="text-lg font-semibold text-white mb-4">Mes campagnes IA</h2>
        {campaigns.length > 0 ? (
          <div className="space-y-3">
            {campaigns.map((campaign) => (
              <div key={campaign.id} className="p-4 bg-white/5 rounded-xl flex items-center justify-between">
                <div>
                  <p className="text-white font-medium">{campaign.name || `Ciblage: ${campaign.age_range} ans`} • {campaign.location}</p>
                  <p className="text-sm text-gray-400">{campaign.interests?.join(', ') || 'Tous les intérêts'}</p>
                </div>
                <div className="flex items-center gap-4 text-sm">
                  <span className="text-[#0047AB]">{formatNumber(campaign.reach)} portée</span>
                  <span className="text-green-400">{formatNumber(campaign.engagement)} engagements</span>
                  <button 
                    onClick={() => toggleCampaign(campaign.id)}
                    className={`px-2 py-1 rounded text-xs ${campaign.status === 'active' ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400'}`}
                  >
                    {campaign.status === 'active' ? 'Actif' : 'En pause'}
                  </button>
                  <button onClick={() => deleteCampaign(campaign.id)} className="p-1 text-red-400 hover:bg-red-500/20 rounded">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <Target className="w-12 h-12 text-gray-500 mx-auto mb-3" />
            <p className="text-gray-400">Aucune campagne IA active</p>
            <p className="text-sm text-gray-500">Créez votre première campagne de ciblage</p>
          </div>
        )}
      </div>

      {/* Question Modal */}
      {showQuestionModal && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
          <div className="bg-[#0A0A0A] rounded-2xl w-full max-w-lg border border-white/10">
            <div className="p-6 border-b border-white/10 flex items-center justify-between">
              <h2 className="text-xl font-bold text-white">Envoyer une question suggestive</h2>
              <button onClick={() => setShowQuestionModal(false)} className="text-gray-400 hover:text-white">
                <X className="w-6 h-6" />
              </button>
            </div>
            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm text-gray-400 mb-2">
                  Destinataires ({selectedCustomers.length} client{selectedCustomers.length > 1 ? 's' : ''})
                </label>
                <div className="flex flex-wrap gap-2 max-h-24 overflow-y-auto p-3 bg-white/5 rounded-lg">
                  {selectedCustomers.map(id => {
                    const customer = customers.find(c => c.id === id);
                    return customer ? (
                      <span key={id} className="px-2 py-1 bg-[#0047AB]/20 text-[#0047AB] rounded text-sm">
                        {customer.first_name} {customer.last_name}
                      </span>
                    ) : null;
                  })}
                </div>
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-2">Votre question</label>
                <textarea
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  placeholder="Ex: Êtes-vous satisfait de votre dernier achat ? Que pourrions-nous améliorer ?"
                  className="w-full h-32 bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-500 resize-none"
                />
              </div>
              <div className="flex gap-3">
                <button
                  onClick={() => setShowQuestionModal(false)}
                  className="flex-1 px-4 py-3 bg-white/10 hover:bg-white/20 rounded-xl text-white"
                >
                  Annuler
                </button>
                <button
                  onClick={sendQuestion}
                  disabled={sendingQuestion}
                  className="flex-1 px-4 py-3 bg-[#0047AB] hover:bg-[#0047AB]/80 rounded-xl text-white flex items-center justify-center gap-2"
                >
                  {sendingQuestion ? (
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  ) : (
                    <>
                      <Send className="w-4 h-4" />
                      Envoyer
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Create Campaign Modal */}
      {showCreate && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
          <div className="bg-[#0A0A0A] rounded-2xl w-full max-w-2xl border border-white/10 max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-white/10 flex items-center justify-between">
              <h2 className="text-xl font-bold text-white">Nouveau ciblage IA</h2>
              <button onClick={() => setShowCreate(false)} className="text-gray-400 hover:text-white">
                <X className="w-6 h-6" />
              </button>
            </div>
            <div className="p-6 space-y-6">
              <div>
                <label className="block text-sm text-gray-400 mb-2">Nom de la campagne</label>
                <input
                  type="text"
                  value={targetAudience.name}
                  onChange={(e) => setTargetAudience({...targetAudience, name: e.target.value})}
                  placeholder="Ex: Campagne été 2026"
                  className="w-full input-dark"
                />
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-gray-400 mb-2">Tranche d'âge</label>
                  <select 
                    value={targetAudience.age_range}
                    onChange={(e) => setTargetAudience({...targetAudience, age_range: e.target.value})}
                    className="w-full input-dark"
                  >
                    <option value="18-24">18-24 ans</option>
                    <option value="25-34">25-34 ans</option>
                    <option value="35-44">35-44 ans</option>
                    <option value="45-54">45-54 ans</option>
                    <option value="55+">55+ ans</option>
                    <option value="25-45">25-45 ans (Recommandé)</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-2">Genre</label>
                  <select 
                    value={targetAudience.gender}
                    onChange={(e) => setTargetAudience({...targetAudience, gender: e.target.value})}
                    className="w-full input-dark"
                  >
                    <option value="all">Tous</option>
                    <option value="male">Hommes</option>
                    <option value="female">Femmes</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm text-gray-400 mb-2">Intérêts</label>
                <div className="flex flex-wrap gap-2">
                  {interests.map(interest => (
                    <button
                      key={interest}
                      type="button"
                      onClick={() => handleInterestToggle(interest)}
                      className={`px-3 py-1 rounded-full text-sm transition-colors ${
                        targetAudience.interests.includes(interest)
                          ? 'bg-[#0047AB] text-white'
                          : 'bg-white/10 text-gray-300 hover:bg-white/20'
                      }`}
                    >
                      {interest}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm text-gray-400 mb-2">Comportements</label>
                <div className="flex flex-wrap gap-2">
                  {behaviors.map(behavior => (
                    <button
                      key={behavior}
                      type="button"
                      onClick={() => handleBehaviorToggle(behavior)}
                      className={`px-3 py-1 rounded-full text-sm transition-colors ${
                        targetAudience.behavior.includes(behavior)
                          ? 'bg-[#D4AF37] text-black'
                          : 'bg-white/10 text-gray-300 hover:bg-white/20'
                      }`}
                    >
                      {behavior}
                    </button>
                  ))}
                </div>
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  onClick={() => setShowCreate(false)}
                  className="flex-1 px-4 py-3 bg-white/10 hover:bg-white/20 rounded-xl text-white"
                >
                  Annuler
                </button>
                <button
                  onClick={createCampaign}
                  className="flex-1 px-4 py-3 bg-[#0047AB] hover:bg-[#0047AB]/80 rounded-xl text-white"
                >
                  Créer la campagne
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default IAClientsSection;
