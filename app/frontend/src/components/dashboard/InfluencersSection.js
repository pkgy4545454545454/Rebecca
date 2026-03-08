import React, { useState, useEffect } from 'react';
import { Users, MessageSquare, TrendingUp, Star, ExternalLink, DollarSign, Trash2 } from 'lucide-react';
import { influencersAPI } from '../../services/api';
import { toast } from 'sonner';

const InfluencersSection = () => {
  const [influencers, setInfluencers] = useState([]);
  const [collaborations, setCollaborations] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [showContact, setShowContact] = useState(null);
  const [contactMessage, setContactMessage] = useState('');
  const [contactBudget, setContactBudget] = useState(500);
  const [categoryFilter, setCategoryFilter] = useState('all');

  const categories = ['all', 'Lifestyle', 'Food', 'Beauty', 'Tech', 'Sport', 'Travel'];

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [influencersRes, collabRes] = await Promise.all([
        influencersAPI.list(),
        influencersAPI.getCollaborations()
      ]);
      // API returns {influencers: [...], total: N}
      const influencersData = influencersRes.data?.influencers || influencersRes.data || [];
      setInfluencers(Array.isArray(influencersData) ? influencersData : []);
      setCollaborations(collabRes.data?.collaborations || []);
      setStats(collabRes.data?.stats || {});
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleContactInfluencer = async (influencer) => {
    if (!contactMessage.trim()) {
      toast.error('Veuillez écrire un message');
      return;
    }
    try {
      await influencersAPI.createCollaboration({
        influencer_id: influencer.id,
        message: contactMessage,
        budget: contactBudget
      });
      toast.success(`Demande envoyée à ${influencer.name} !`);
      setShowContact(null);
      setContactMessage('');
      fetchData();
    } catch (error) {
      toast.error('Erreur lors de l\'envoi de la demande');
    }
  };

  const cancelCollaboration = async (collabId) => {
    try {
      await influencersAPI.cancelCollaboration(collabId);
      toast.success('Collaboration annulée');
      fetchData();
    } catch (error) {
      toast.error('Erreur lors de l\'annulation');
    }
  };

  const formatNumber = (num) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num?.toString() || '0';
  };

  const filteredInfluencers = categoryFilter === 'all' 
    ? influencers 
    : influencers.filter(i => i.category === categoryFilter);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="w-10 h-10 border-4 border-[#D4AF37] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="influencers-section">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
            Influenceurs
          </h1>
          <p className="text-gray-400 mt-1">Collaborez avec les créateurs de contenu de la région</p>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="card-service rounded-xl p-4">
          <Users className="w-5 h-5 text-[#0047AB] mb-2" />
          <p className="text-2xl font-bold text-white">{influencers.length}</p>
          <p className="text-sm text-gray-400">Influenceurs disponibles</p>
        </div>
        <div className="card-service rounded-xl p-4">
          <MessageSquare className="w-5 h-5 text-[#D4AF37] mb-2" />
          <p className="text-2xl font-bold text-white">{stats.active_collaborations || 0}</p>
          <p className="text-sm text-gray-400">Collaborations actives</p>
        </div>
        <div className="card-service rounded-xl p-4">
          <TrendingUp className="w-5 h-5 text-green-400 mb-2" />
          <p className="text-2xl font-bold text-white">{formatNumber(stats.total_reach || 0)}</p>
          <p className="text-sm text-gray-400">Portée potentielle</p>
        </div>
        <div className="card-service rounded-xl p-4">
          <DollarSign className="w-5 h-5 text-purple-400 mb-2" />
          <p className="text-2xl font-bold text-white">{stats.total_investment || 0} CHF</p>
          <p className="text-sm text-gray-400">Investi ce mois</p>
        </div>
      </div>

      {/* Active Collaborations */}
      {collaborations.length > 0 && (
        <div className="card-service rounded-xl p-6">
          <h2 className="text-lg font-semibold text-white mb-4">Mes collaborations</h2>
          <div className="space-y-3">
            {collaborations.map((collab) => (
              <div key={collab.id} className="p-4 bg-white/5 rounded-xl flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <img 
                    src={collab.influencer_image || 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=100'} 
                    alt="" 
                    className="w-12 h-12 rounded-full object-cover"
                  />
                  <div>
                    <p className="text-white font-medium">{collab.influencer_name}</p>
                    <p className="text-sm text-gray-400">{collab.message?.substring(0, 50)}...</p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <span className="text-[#D4AF37] font-semibold">{collab.budget} CHF</span>
                  <span className={`px-2 py-1 rounded text-xs ${
                    collab.status === 'active' ? 'bg-green-500/20 text-green-400' :
                    collab.status === 'pending' ? 'bg-yellow-500/20 text-yellow-400' :
                    'bg-gray-500/20 text-gray-400'
                  }`}>
                    {collab.status === 'active' ? 'Actif' : collab.status === 'pending' ? 'En attente' : 'Terminé'}
                  </span>
                  {collab.status === 'pending' && (
                    <button onClick={() => cancelCollaboration(collab.id)} className="p-1 text-red-400 hover:bg-red-500/20 rounded">
                      <Trash2 className="w-4 h-4" />
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Category Filter */}
      <div className="flex gap-2 overflow-x-auto pb-2">
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setCategoryFilter(cat)}
            className={`px-4 py-2 rounded-full text-sm whitespace-nowrap transition-colors ${
              categoryFilter === cat
                ? 'bg-[#D4AF37] text-black'
                : 'bg-white/5 text-gray-400 hover:bg-white/10'
            }`}
          >
            {cat === 'all' ? 'Tous' : cat}
          </button>
        ))}
      </div>

      {/* Influencers Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredInfluencers.map((influencer) => (
          <div key={influencer.id} className="card-service rounded-xl p-4 hover:border-[#D4AF37]/50 transition-colors">
            <div className="flex items-center gap-4 mb-4">
              <img 
                src={influencer.image || 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=100'} 
                alt={influencer.name} 
                className="w-16 h-16 rounded-full object-cover border-2 border-[#D4AF37]/30"
              />
              <div className="flex-1">
                <h3 className="text-white font-semibold">{influencer.name}</h3>
                <p className="text-sm text-[#D4AF37]">{influencer.category}</p>
                <div className="flex items-center gap-1 text-xs text-gray-400">
                  <Star className="w-3 h-3 text-yellow-500 fill-yellow-500" />
                  {influencer.engagement_rate}% engagement
                </div>
              </div>
            </div>
            <div className="grid grid-cols-3 gap-2 text-center mb-4">
              <div className="p-2 bg-white/5 rounded-lg">
                <p className="text-white font-bold">{formatNumber(influencer.followers)}</p>
                <p className="text-xs text-gray-500">Abonnés</p>
              </div>
              <div className="p-2 bg-white/5 rounded-lg">
                <p className="text-white font-bold">{influencer.price} CHF</p>
                <p className="text-xs text-gray-500">Tarif</p>
              </div>
              <div className="p-2 bg-white/5 rounded-lg">
                <p className="text-white font-bold">{influencer.posts || 0}</p>
                <p className="text-xs text-gray-500">Posts</p>
              </div>
            </div>
            <div className="flex gap-2">
              <button 
                onClick={() => setShowContact(influencer)}
                className="flex-1 btn-primary text-sm py-2"
              >
                Contacter
              </button>
              {influencer.instagram && (
                <a 
                  href={`https://instagram.com/${influencer.instagram.replace('@', '')}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="p-2 bg-white/5 rounded-lg text-gray-400 hover:text-white transition-colors"
                >
                  <ExternalLink className="w-4 h-4" />
                </a>
              )}
            </div>
          </div>
        ))}
      </div>

      {filteredInfluencers.length === 0 && (
        <div className="card-service rounded-xl p-12 text-center">
          <Users className="w-12 h-12 text-gray-500 mx-auto mb-3" />
          <p className="text-gray-400">Aucun influenceur dans cette catégorie</p>
        </div>
      )}

      {/* Contact Modal */}
      {showContact && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="card-service rounded-xl p-6 w-full max-w-md">
            <div className="flex items-center gap-4 mb-6">
              <img 
                src={showContact.image || 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=100'} 
                alt={showContact.name} 
                className="w-16 h-16 rounded-full object-cover"
              />
              <div>
                <h3 className="text-lg font-semibold text-white">{showContact.name}</h3>
                <p className="text-[#D4AF37]">{showContact.category}</p>
                <p className="text-sm text-gray-400">{formatNumber(showContact.followers)} abonnés</p>
              </div>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-gray-400 mb-2">Votre message</label>
                <textarea
                  value={contactMessage}
                  onChange={(e) => setContactMessage(e.target.value)}
                  placeholder="Décrivez votre projet de collaboration..."
                  className="input-dark w-full h-32"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-2">Budget proposé (CHF)</label>
                <input
                  type="number"
                  value={contactBudget}
                  onChange={(e) => setContactBudget(parseInt(e.target.value))}
                  min={showContact.price}
                  className="input-dark w-full"
                />
                <p className="text-xs text-gray-500 mt-1">Tarif minimum: {showContact.price} CHF</p>
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              <button onClick={() => { setShowContact(null); setContactMessage(''); }} className="btn-secondary flex-1">
                Annuler
              </button>
              <button onClick={() => handleContactInfluencer(showContact)} className="btn-primary flex-1">
                Envoyer la demande
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default InfluencersSection;
