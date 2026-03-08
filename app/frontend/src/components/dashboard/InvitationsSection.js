import React, { useState, useEffect } from 'react';
import { Send, Plus, Trash2, Users, Calendar, Clock, CheckCircle, XCircle, HelpCircle, Gift, MessageSquare, Bell } from 'lucide-react';
import { clientInvitationsAPI } from '../../services/api';
import { toast } from 'sonner';

const InvitationsSection = () => {
  const [invitations, setInvitations] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [activeType, setActiveType] = useState('invitation');
  const [formData, setFormData] = useState({
    title: '',
    message: '',
    invitation_type: 'event',
    target_audience: 'all',
    scheduled_date: ''
  });

  const suggestiveQuestions = [
    "Avez-vous découvert nos nouvelles offres ?",
    "Êtes-vous satisfait de nos services ?",
    "Que pouvons-nous améliorer pour vous ?",
    "Souhaitez-vous être informé de nos événements ?",
    "Recommanderiez-vous nos services à vos proches ?"
  ];

  useEffect(() => {
    fetchInvitations();
  }, []);

  const fetchInvitations = async () => {
    try {
      const response = await clientInvitationsAPI.list();
      setInvitations(response.data?.invitations || []);
      setStats(response.data?.stats || {});
    } catch (error) {
      console.error('Error fetching invitations:', error);
    } finally {
      setLoading(false);
    }
  };

  const createInvitation = async () => {
    if (!formData.title || !formData.message) {
      toast.error('Veuillez remplir tous les champs');
      return;
    }
    try {
      await clientInvitationsAPI.create(formData);
      toast.success('Invitation créée avec succès');
      setShowCreate(false);
      setFormData({ title: '', message: '', invitation_type: 'event', target_audience: 'all', scheduled_date: '' });
      fetchInvitations();
    } catch (error) {
      toast.error('Erreur lors de la création');
    }
  };

  const deleteInvitation = async (invitationId) => {
    try {
      await clientInvitationsAPI.delete(invitationId);
      toast.success('Invitation supprimée');
      fetchInvitations();
    } catch (error) {
      toast.error('Erreur lors de la suppression');
    }
  };

  const toggleInvitation = async (invitationId) => {
    try {
      await clientInvitationsAPI.toggle(invitationId);
      toast.success('Statut mis à jour');
      fetchInvitations();
    } catch (error) {
      toast.error('Erreur lors de la mise à jour');
    }
  };

  const handleQuickQuestion = (question) => {
    setFormData({ ...formData, title: 'Question client', message: question, invitation_type: 'survey' });
    setShowCreate(true);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="w-10 h-10 border-4 border-[#0047AB] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="invitations-section">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
            Invitations Clients
          </h1>
          <p className="text-gray-400 mt-1">Engagez vos clients avec des messages personnalisés</p>
        </div>
        <button onClick={() => setShowCreate(true)} className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" /> Nouvelle invitation
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="card-service rounded-xl p-4">
          <Send className="w-5 h-5 text-[#0047AB] mb-2" />
          <p className="text-2xl font-bold text-white">{stats.total_sent || 0}</p>
          <p className="text-sm text-gray-400">Envoyées</p>
        </div>
        <div className="card-service rounded-xl p-4">
          <CheckCircle className="w-5 h-5 text-green-400 mb-2" />
          <p className="text-2xl font-bold text-white">{stats.total_opened || 0}</p>
          <p className="text-sm text-gray-400">Ouvertures</p>
        </div>
        <div className="card-service rounded-xl p-4">
          <Users className="w-5 h-5 text-[#D4AF37] mb-2" />
          <p className="text-2xl font-bold text-white">{stats.total_responses || 0}</p>
          <p className="text-sm text-gray-400">Réponses</p>
        </div>
        <div className="card-service rounded-xl p-4">
          <Clock className="w-5 h-5 text-purple-400 mb-2" />
          <p className="text-2xl font-bold text-white">{stats.scheduled || 0}</p>
          <p className="text-sm text-gray-400">Planifiées</p>
        </div>
      </div>

      {/* Quick Questions */}
      <div className="card-service rounded-xl p-6 border-[#0047AB]/30 bg-gradient-to-r from-[#0047AB]/5 to-transparent">
        <h2 className="text-lg font-semibold text-white mb-2 flex items-center gap-2">
          <HelpCircle className="w-5 h-5 text-[#0047AB]" />
          Questions suggestives
        </h2>
        <p className="text-sm text-gray-400 mb-4">Posez rapidement une question à vos clients</p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {suggestiveQuestions.map((question, i) => (
            <button
              key={i}
              onClick={() => handleQuickQuestion(question)}
              className="p-3 bg-white/5 rounded-lg text-left text-sm text-gray-300 hover:bg-[#0047AB]/20 hover:text-white transition-all"
            >
              "{question}"
            </button>
          ))}
        </div>
      </div>

      {/* Type Tabs */}
      <div className="flex gap-2 border-b border-white/10">
        {[
          { id: 'invitation', label: 'Invitations', icon: Gift },
          { id: 'survey', label: 'Sondages', icon: HelpCircle },
          { id: 'reminder', label: 'Rappels', icon: Bell },
          { id: 'message', label: 'Messages', icon: MessageSquare }
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveType(tab.id)}
            className={`flex items-center gap-2 px-4 py-3 border-b-2 transition-colors ${
              activeType === tab.id
                ? 'border-[#0047AB] text-white'
                : 'border-transparent text-gray-400 hover:text-white'
            }`}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Invitations List */}
      <div className="space-y-3">
        {invitations.filter(inv => activeType === 'all' || inv.invitation_type === activeType).length > 0 ? (
          invitations.filter(inv => activeType === 'all' || inv.invitation_type === activeType).map((invitation) => (
            <div key={invitation.id} className="card-service rounded-xl p-4">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="text-white font-medium">{invitation.title}</h3>
                    <span className={`px-2 py-0.5 rounded text-xs ${
                      invitation.status === 'active' ? 'bg-green-500/20 text-green-400' :
                      invitation.status === 'scheduled' ? 'bg-yellow-500/20 text-yellow-400' :
                      'bg-gray-500/20 text-gray-400'
                    }`}>
                      {invitation.status === 'active' ? 'Active' : invitation.status === 'scheduled' ? 'Planifiée' : 'Terminée'}
                    </span>
                  </div>
                  <p className="text-sm text-gray-400 mb-3">{invitation.message}</p>
                  <div className="flex items-center gap-4 text-xs text-gray-500">
                    <span className="flex items-center gap-1">
                      <Users className="w-3 h-3" />
                      {invitation.target_audience === 'all' ? 'Tous les clients' : invitation.target_audience}
                    </span>
                    {invitation.scheduled_date && (
                      <span className="flex items-center gap-1">
                        <Calendar className="w-3 h-3" />
                        {new Date(invitation.scheduled_date).toLocaleDateString('fr-FR')}
                      </span>
                    )}
                    <span className="flex items-center gap-1">
                      <Send className="w-3 h-3" />
                      {invitation.sent_count || 0} envoyées
                    </span>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button 
                    onClick={() => toggleInvitation(invitation.id)}
                    className={`p-2 rounded-lg ${invitation.status === 'active' ? 'bg-yellow-500/20 text-yellow-400' : 'bg-green-500/20 text-green-400'}`}
                  >
                    {invitation.status === 'active' ? <XCircle className="w-4 h-4" /> : <CheckCircle className="w-4 h-4" />}
                  </button>
                  <button 
                    onClick={() => deleteInvitation(invitation.id)}
                    className="p-2 bg-red-500/20 text-red-400 rounded-lg hover:bg-red-500/30"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="card-service rounded-xl p-12 text-center">
            <Send className="w-12 h-12 text-gray-500 mx-auto mb-3" />
            <p className="text-gray-400">Aucune invitation dans cette catégorie</p>
            <button onClick={() => setShowCreate(true)} className="btn-secondary mt-4">
              Créer une invitation
            </button>
          </div>
        )}
      </div>

      {/* Create Modal */}
      {showCreate && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="card-service rounded-xl p-6 w-full max-w-lg">
            <h3 className="text-lg font-semibold text-white mb-6">Nouvelle invitation</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-gray-400 mb-2">Titre *</label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData({...formData, title: e.target.value})}
                  placeholder="Ex: Invitation événement VIP"
                  className="input-dark w-full"
                />
              </div>

              <div>
                <label className="block text-sm text-gray-400 mb-2">Type</label>
                <select
                  value={formData.invitation_type}
                  onChange={(e) => setFormData({...formData, invitation_type: e.target.value})}
                  className="input-dark w-full"
                >
                  <option value="event">Événement</option>
                  <option value="survey">Sondage</option>
                  <option value="reminder">Rappel</option>
                  <option value="promotion">Promotion</option>
                </select>
              </div>

              <div>
                <label className="block text-sm text-gray-400 mb-2">Message *</label>
                <textarea
                  value={formData.message}
                  onChange={(e) => setFormData({...formData, message: e.target.value})}
                  placeholder="Rédigez votre message..."
                  className="input-dark w-full h-32"
                />
              </div>

              <div>
                <label className="block text-sm text-gray-400 mb-2">Audience cible</label>
                <select
                  value={formData.target_audience}
                  onChange={(e) => setFormData({...formData, target_audience: e.target.value})}
                  className="input-dark w-full"
                >
                  <option value="all">Tous les clients</option>
                  <option value="new">Nouveaux clients</option>
                  <option value="loyal">Clients fidèles</option>
                  <option value="inactive">Clients inactifs</option>
                </select>
              </div>

              <div>
                <label className="block text-sm text-gray-400 mb-2">Date d'envoi (optionnel)</label>
                <input
                  type="datetime-local"
                  value={formData.scheduled_date}
                  onChange={(e) => setFormData({...formData, scheduled_date: e.target.value})}
                  className="input-dark w-full"
                />
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              <button onClick={() => setShowCreate(false)} className="btn-secondary flex-1">Annuler</button>
              <button onClick={createInvitation} className="btn-primary flex-1">Créer l'invitation</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default InvitationsSection;
