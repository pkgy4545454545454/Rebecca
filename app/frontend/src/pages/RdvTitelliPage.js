/**
 * Rdv chez Titelli - Social Booking & Dating Page
 * - Browse and create shared offers for 2 people
 * - Friendly vs Romantic mode
 * - Real-time chat
 */
import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate, useSearchParams } from 'react-router-dom';
import Header from '../components/Header';
import Footer from '../components/Footer';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '../components/ui/card';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '../components/ui/dialog';
import { Input } from '../components/ui/input';
import { Textarea } from '../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { toast } from 'sonner';
import { 
  Heart, Users, MessageCircle, Calendar, MapPin, Clock, 
  Plus, Send, Check, X, Sparkles, Crown, Coffee, 
  Utensils, Dumbbell, Palette, TreePine, PartyPopper
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Category icons mapping
const categoryIcons = {
  restaurant: Utensils,
  sport: Dumbbell,
  wellness: Sparkles,
  culture: Palette,
  nature: TreePine,
  party: PartyPopper,
  creative: Palette,
  other: Coffee
};

export default function RdvTitelliPage() {
  const { user, token } = useAuth();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  
  // State
  const [activeTab, setActiveTab] = useState('discover');
  const [offerType, setOfferType] = useState('friendly');
  const [offers, setOffers] = useState([]);
  const [myOffers, setMyOffers] = useState([]);
  const [availableUsers, setAvailableUsers] = useState([]);
  const [invitations, setInvitations] = useState([]);
  const [categories, setCategories] = useState([]);
  const [stats, setStats] = useState(null);
  const [subscriptionStatus, setSubscriptionStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  
  // Modal states
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [showSubscribeModal, setShowSubscribeModal] = useState(false);
  const [selectedOffer, setSelectedOffer] = useState(null);
  const [selectedUser, setSelectedUser] = useState(null);
  
  // Form state
  const [newOffer, setNewOffer] = useState({
    title: '',
    description: '',
    offer_type: 'friendly',
    category: 'restaurant',
    location: '',
    proposed_date: '',
    price_per_person: 0
  });

  // Fetch data
  const fetchData = useCallback(async () => {
    if (!token) return;
    
    try {
      setLoading(true);
      
      // Fetch in parallel
      const [offersRes, myOffersRes, invitationsRes, categoriesRes, statsRes, subscriptionRes] = await Promise.all([
        fetch(`${API_URL}/api/rdv/offers?offer_type=${offerType}`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        fetch(`${API_URL}/api/rdv/offers/my`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        fetch(`${API_URL}/api/rdv/invitations/received?status=pending`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        fetch(`${API_URL}/api/rdv/categories`),
        fetch(`${API_URL}/api/rdv/stats`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        fetch(`${API_URL}/api/rdv/subscriptions/romantic/status`, {
          headers: { Authorization: `Bearer ${token}` }
        })
      ]);
      
      if (offersRes.ok) {
        const data = await offersRes.json();
        setOffers(data.offers || []);
      }
      
      if (myOffersRes.ok) {
        const data = await myOffersRes.json();
        setMyOffers(data.offers || []);
      }
      
      if (invitationsRes.ok) {
        const data = await invitationsRes.json();
        setInvitations(data.invitations || []);
      }
      
      if (categoriesRes.ok) {
        const data = await categoriesRes.json();
        setCategories(data.categories || []);
      }
      
      if (statsRes.ok) {
        const data = await statsRes.json();
        setStats(data);
      }
      
      if (subscriptionRes.ok) {
        const data = await subscriptionRes.json();
        setSubscriptionStatus(data);
      }
      
    } catch (error) {
      console.error('Error fetching data:', error);
      toast.error('Erreur de chargement');
    } finally {
      setLoading(false);
    }
  }, [token, offerType]);

  useEffect(() => {
    if (!user) {
      navigate('/auth');
      return;
    }
    fetchData();
  }, [user, navigate, fetchData]);

  // Handle Stripe return params
  useEffect(() => {
    const handlePaymentReturn = async () => {
      const subscriptionSuccess = searchParams.get('subscription_success');
      const subscriptionCancelled = searchParams.get('subscription_cancelled');
      const invitationAccepted = searchParams.get('invitation_accepted');
      const invitationCancelled = searchParams.get('invitation_cancelled');
      
      // Handle cancellations
      if (subscriptionCancelled) {
        toast.error('Abonnement annulé');
        setSearchParams({});
        return;
      }
      
      if (invitationCancelled) {
        toast.error('Paiement annulé');
        setSearchParams({});
        return;
      }
      
      if (subscriptionSuccess) {
        // Confirm subscription payment
        try {
          const res = await fetch(`${API_URL}/api/rdv/subscriptions/romantic/${subscriptionSuccess}/confirm`, {
            method: 'POST',
            headers: { Authorization: `Bearer ${token}` }
          });
          
          if (res.ok) {
            toast.success('Abonnement romantique activé ! 💕');
            setOfferType('romantic');
          } else {
            toast.error('Erreur de confirmation du paiement');
          }
        } catch (error) {
          console.error('Error confirming subscription:', error);
          toast.error('Erreur de connexion');
        }
        
        // Clear params
        setSearchParams({});
        fetchData();
      }
      
      if (invitationAccepted) {
        // Confirm invitation payment
        try {
          const res = await fetch(`${API_URL}/api/rdv/invitations/${invitationAccepted}/confirm-payment`, {
            method: 'POST',
            headers: { Authorization: `Bearer ${token}` }
          });
          
          if (res.ok) {
            const data = await res.json();
            toast.success('Invitation acceptée ! 🎉');
            if (data.chat_room_id) {
              navigate(`/rdv/chat/${data.chat_room_id}`);
            }
          } else {
            toast.error('Erreur de confirmation du paiement');
          }
        } catch (error) {
          console.error('Error confirming invitation:', error);
          toast.error('Erreur de connexion');
        }
        
        // Clear params
        setSearchParams({});
        fetchData();
      }
    };
    
    if (token) {
      handlePaymentReturn();
    }
  }, [searchParams, token, setSearchParams, fetchData, navigate]);

  // Fetch available users when switching to romantic or looking for users
  const fetchAvailableUsers = async (type) => {
    try {
      const res = await fetch(`${API_URL}/api/rdv/available-users?availability_type=${type}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (res.status === 402) {
        setShowSubscribeModal(true);
        return;
      }
      
      if (res.ok) {
        const data = await res.json();
        setAvailableUsers(data.users || []);
      }
    } catch (error) {
      console.error('Error fetching users:', error);
    }
  };

  // Create offer
  const handleCreateOffer = async () => {
    if (!newOffer.title || !newOffer.category) {
      toast.error('Veuillez remplir les champs obligatoires');
      return;
    }
    
    try {
      const res = await fetch(`${API_URL}/api/rdv/offers`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(newOffer)
      });
      
      if (res.status === 402) {
        setShowSubscribeModal(true);
        setShowCreateModal(false);
        return;
      }
      
      if (res.ok) {
        toast.success('Offre créée avec succès !');
        setShowCreateModal(false);
        setNewOffer({
          title: '',
          description: '',
          offer_type: 'friendly',
          category: 'restaurant',
          location: '',
          proposed_date: '',
          price_per_person: 0
        });
        fetchData();
      } else {
        const data = await res.json();
        toast.error(data.detail || 'Erreur lors de la création');
      }
    } catch (error) {
      toast.error('Erreur de connexion');
    }
  };

  // Send invitation
  const handleSendInvitation = async (userId) => {
    if (!selectedOffer) return;
    
    try {
      const res = await fetch(`${API_URL}/api/rdv/invitations`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          offer_id: selectedOffer.id,
          invitee_id: userId,
          message: `Je t'invite à ${selectedOffer.title} !`
        })
      });
      
      if (res.ok) {
        toast.success('Invitation envoyée !');
        setShowInviteModal(false);
        setSelectedOffer(null);
      } else {
        const data = await res.json();
        toast.error(data.detail || 'Erreur lors de l\'envoi');
      }
    } catch (error) {
      toast.error('Erreur de connexion');
    }
  };

  // Accept invitation - redirects to Stripe
  const handleAcceptInvitation = async (invitationId) => {
    try {
      const res = await fetch(`${API_URL}/api/rdv/invitations/${invitationId}/accept`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }
      });
      
      const data = await res.json();
      
      if (data.requires_payment && data.checkout_url) {
        // Redirect to Stripe checkout
        window.location.href = data.checkout_url;
      } else if (data.chat_room_id) {
        toast.success('Invitation acceptée !');
        navigate(`/rdv/chat/${data.chat_room_id}`);
      } else {
        toast.error(data.detail || 'Erreur');
      }
    } catch (error) {
      toast.error('Erreur de connexion');
    }
  };

  // Decline invitation
  const handleDeclineInvitation = async (invitationId) => {
    try {
      const res = await fetch(`${API_URL}/api/rdv/invitations/${invitationId}/decline`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (res.ok) {
        toast.success('Invitation déclinée');
        fetchData();
      }
    } catch (error) {
      toast.error('Erreur de connexion');
    }
  };

  // Subscribe to romantic - redirects to Stripe
  const handleSubscribeRomantic = async () => {
    try {
      const res = await fetch(`${API_URL}/api/rdv/subscriptions/romantic`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }
      });
      
      const data = await res.json();
      
      if (data.checkout_url) {
        // Redirect to Stripe checkout
        window.location.href = data.checkout_url;
      } else if (data.has_subscription) {
        toast.success('Abonnement déjà actif !');
        setShowSubscribeModal(false);
        fetchData();
      } else {
        toast.error(data.detail || 'Erreur');
      }
    } catch (error) {
      toast.error('Erreur de connexion');
    }
  };

  // Open invite modal
  const openInviteModal = (offer) => {
    setSelectedOffer(offer);
    fetchAvailableUsers(offer.offer_type);
    setShowInviteModal(true);
  };

  if (!user) return null;

  return (
    <div className="min-h-screen bg-gradient-to-b from-zinc-950 via-zinc-900 to-zinc-950">
      <Header />
      
      <main className="pt-24 pb-16 px-4 md:px-8">
        <div className="max-w-7xl mx-auto">
          
          {/* Hero Section */}
          <div className="text-center mb-12">
            <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
              Rdv chez <span className="text-amber-400">Titelli</span>
            </h1>
            <p className="text-zinc-400 text-lg max-w-2xl mx-auto">
              Réservez une activité pour 2 et invitez quelqu'un ! 
              Date romantique ou rendez-vous amical, à vous de choisir.
            </p>
            
            {/* Mode Toggle */}
            <div className="flex justify-center gap-4 mt-8">
              <Button
                variant={offerType === 'friendly' ? 'default' : 'outline'}
                onClick={() => setOfferType('friendly')}
                className={offerType === 'friendly' ? 'bg-emerald-600 hover:bg-emerald-700' : ''}
              >
                <Users className="w-4 h-4 mr-2" />
                Amical
              </Button>
              <Button
                variant={offerType === 'romantic' ? 'default' : 'outline'}
                onClick={() => {
                  if (!subscriptionStatus?.has_subscription) {
                    setShowSubscribeModal(true);
                  } else {
                    setOfferType('romantic');
                  }
                }}
                className={offerType === 'romantic' ? 'bg-pink-600 hover:bg-pink-700' : ''}
              >
                <Heart className="w-4 h-4 mr-2" />
                Romantique
                {!subscriptionStatus?.has_subscription && (
                  <Crown className="w-3 h-3 ml-1 text-amber-400" />
                )}
              </Button>
            </div>
          </div>

          {/* Stats Cards */}
          {stats && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
              <Card className="bg-zinc-800/50 border-zinc-700">
                <CardContent className="p-4 text-center">
                  <div className="text-2xl font-bold text-white">{stats.offers_created}</div>
                  <div className="text-sm text-zinc-400">Offres créées</div>
                </CardContent>
              </Card>
              <Card className="bg-zinc-800/50 border-zinc-700">
                <CardContent className="p-4 text-center">
                  <div className="text-2xl font-bold text-emerald-400">{stats.offers_confirmed}</div>
                  <div className="text-sm text-zinc-400">Rendez-vous</div>
                </CardContent>
              </Card>
              <Card className="bg-zinc-800/50 border-zinc-700">
                <CardContent className="p-4 text-center">
                  <div className="text-2xl font-bold text-amber-400">{stats.invitations_received}</div>
                  <div className="text-sm text-zinc-400">Invitations reçues</div>
                </CardContent>
              </Card>
              <Card className="bg-zinc-800/50 border-zinc-700">
                <CardContent className="p-4 text-center">
                  <div className="text-2xl font-bold text-pink-400">
                    {stats.has_romantic_subscription ? '✓' : '✗'}
                  </div>
                  <div className="text-sm text-zinc-400">Abo Romantique</div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Main Tabs */}
          <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
            <TabsList className="bg-zinc-800/50 border border-zinc-700">
              <TabsTrigger value="discover" className="data-[state=active]:bg-amber-600">
                Découvrir
              </TabsTrigger>
              <TabsTrigger value="my-offers" className="data-[state=active]:bg-amber-600">
                Mes Offres
              </TabsTrigger>
              <TabsTrigger value="invitations" className="data-[state=active]:bg-amber-600">
                Invitations
                {invitations.length > 0 && (
                  <Badge className="ml-2 bg-pink-600">{invitations.length}</Badge>
                )}
              </TabsTrigger>
              <TabsTrigger value="users" className="data-[state=active]:bg-amber-600">
                Personnes
              </TabsTrigger>
            </TabsList>

            {/* Discover Tab */}
            <TabsContent value="discover" className="space-y-6">
              <div className="flex justify-between items-center">
                <h2 className="text-xl font-semibold text-white">
                  Offres {offerType === 'friendly' ? 'Amicales' : 'Romantiques'}
                </h2>
                <Button onClick={() => setShowCreateModal(true)} className="bg-amber-600 hover:bg-amber-700">
                  <Plus className="w-4 h-4 mr-2" />
                  Créer une offre
                </Button>
              </div>
              
              {loading ? (
                <div className="text-center py-12 text-zinc-400">Chargement...</div>
              ) : offers.length === 0 ? (
                <Card className="bg-zinc-800/50 border-zinc-700">
                  <CardContent className="p-12 text-center">
                    <Sparkles className="w-12 h-12 text-amber-400 mx-auto mb-4" />
                    <h3 className="text-lg font-semibold text-white mb-2">Aucune offre disponible</h3>
                    <p className="text-zinc-400 mb-4">Soyez le premier à créer une offre !</p>
                    <Button onClick={() => setShowCreateModal(true)} className="bg-amber-600 hover:bg-amber-700">
                      Créer une offre
                    </Button>
                  </CardContent>
                </Card>
              ) : (
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {offers.map(offer => {
                    const CategoryIcon = categoryIcons[offer.category] || Coffee;
                    return (
                      <Card key={offer.id} className="bg-zinc-800/50 border-zinc-700 hover:border-amber-600/50 transition-all">
                        <CardHeader>
                          <div className="flex items-start justify-between">
                            <div className="flex items-center gap-3">
                              <div className="w-10 h-10 rounded-full bg-amber-600/20 flex items-center justify-center">
                                <CategoryIcon className="w-5 h-5 text-amber-400" />
                              </div>
                              <div>
                                <CardTitle className="text-white text-lg">{offer.title}</CardTitle>
                                <CardDescription className="text-zinc-400">
                                  par {offer.creator_name}
                                </CardDescription>
                              </div>
                            </div>
                            <Badge className={offer.offer_type === 'romantic' ? 'bg-pink-600' : 'bg-emerald-600'}>
                              {offer.offer_type === 'romantic' ? <Heart className="w-3 h-3 mr-1" /> : <Users className="w-3 h-3 mr-1" />}
                              {offer.offer_type === 'romantic' ? 'Romantique' : 'Amical'}
                            </Badge>
                          </div>
                        </CardHeader>
                        <CardContent className="space-y-3">
                          {offer.description && (
                            <p className="text-zinc-300 text-sm">{offer.description}</p>
                          )}
                          <div className="flex flex-wrap gap-2 text-sm text-zinc-400">
                            {offer.location && (
                              <span className="flex items-center gap-1">
                                <MapPin className="w-3 h-3" /> {offer.location}
                              </span>
                            )}
                            {offer.proposed_date && (
                              <span className="flex items-center gap-1">
                                <Calendar className="w-3 h-3" /> 
                                {new Date(offer.proposed_date).toLocaleDateString('fr-FR')}
                              </span>
                            )}
                          </div>
                          {offer.price_per_person > 0 && (
                            <div className="text-amber-400 font-semibold">
                              {offer.price_per_person} CHF / personne
                            </div>
                          )}
                        </CardContent>
                        <CardFooter>
                          <Button 
                            className="w-full bg-amber-600 hover:bg-amber-700"
                            onClick={() => openInviteModal(offer)}
                          >
                            <Send className="w-4 h-4 mr-2" />
                            Inviter quelqu'un
                          </Button>
                        </CardFooter>
                      </Card>
                    );
                  })}
                </div>
              )}
            </TabsContent>

            {/* My Offers Tab */}
            <TabsContent value="my-offers" className="space-y-6">
              <div className="flex justify-between items-center">
                <h2 className="text-xl font-semibold text-white">Mes Offres</h2>
                <Button onClick={() => setShowCreateModal(true)} className="bg-amber-600 hover:bg-amber-700">
                  <Plus className="w-4 h-4 mr-2" />
                  Nouvelle offre
                </Button>
              </div>
              
              {myOffers.length === 0 ? (
                <Card className="bg-zinc-800/50 border-zinc-700">
                  <CardContent className="p-12 text-center">
                    <p className="text-zinc-400">Vous n'avez pas encore créé d'offre</p>
                  </CardContent>
                </Card>
              ) : (
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {myOffers.map(offer => (
                    <Card key={offer.id} className="bg-zinc-800/50 border-zinc-700">
                      <CardHeader>
                        <div className="flex justify-between items-start">
                          <CardTitle className="text-white">{offer.title}</CardTitle>
                          <Badge variant={
                            offer.status === 'confirmed' ? 'default' :
                            offer.status === 'open' ? 'secondary' : 'destructive'
                          }>
                            {offer.status === 'confirmed' ? 'Confirmé' :
                             offer.status === 'open' ? 'En attente' : 'Annulé'}
                          </Badge>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <div className="text-sm text-zinc-400">
                          {offer.participants?.length || 1} participant(s)
                        </div>
                        {offer.chat_room_id && (
                          <Button 
                            size="sm" 
                            className="mt-4 w-full"
                            onClick={() => navigate(`/rdv/chat/${offer.chat_room_id}`)}
                          >
                            <MessageCircle className="w-4 h-4 mr-2" />
                            Ouvrir le chat
                          </Button>
                        )}
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </TabsContent>

            {/* Invitations Tab */}
            <TabsContent value="invitations" className="space-y-6">
              <h2 className="text-xl font-semibold text-white">Invitations Reçues</h2>
              
              {invitations.length === 0 ? (
                <Card className="bg-zinc-800/50 border-zinc-700">
                  <CardContent className="p-12 text-center">
                    <p className="text-zinc-400">Aucune invitation en attente</p>
                  </CardContent>
                </Card>
              ) : (
                <div className="space-y-4">
                  {invitations.map(invitation => (
                    <Card key={invitation.id} className="bg-zinc-800/50 border-zinc-700">
                      <CardContent className="p-6">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-4">
                            <div className="w-12 h-12 rounded-full bg-amber-600/20 flex items-center justify-center">
                              {invitation.offer_type === 'romantic' ? 
                                <Heart className="w-6 h-6 text-pink-400" /> :
                                <Users className="w-6 h-6 text-emerald-400" />
                              }
                            </div>
                            <div>
                              <h3 className="text-white font-semibold">{invitation.offer_title}</h3>
                              <p className="text-zinc-400 text-sm">
                                Invitation de {invitation.inviter_name}
                              </p>
                              {invitation.message && (
                                <p className="text-zinc-300 text-sm mt-1">"{invitation.message}"</p>
                              )}
                            </div>
                          </div>
                          <div className="flex gap-2">
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleDeclineInvitation(invitation.id)}
                              className="text-red-400 border-red-400/50 hover:bg-red-400/10"
                            >
                              <X className="w-4 h-4" />
                            </Button>
                            <Button
                              size="sm"
                              onClick={() => handleAcceptInvitation(invitation.id)}
                              className="bg-emerald-600 hover:bg-emerald-700"
                            >
                              <Check className="w-4 h-4 mr-1" />
                              Accepter (2 CHF)
                            </Button>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </TabsContent>

            {/* Users Tab */}
            <TabsContent value="users" className="space-y-6">
              <div className="flex justify-between items-center">
                <h2 className="text-xl font-semibold text-white">
                  Personnes Disponibles ({offerType === 'friendly' ? 'Amical' : 'Romantique'})
                </h2>
                <Button 
                  variant="outline"
                  onClick={() => fetchAvailableUsers(offerType)}
                >
                  Actualiser
                </Button>
              </div>
              
              {availableUsers.length === 0 ? (
                <Card className="bg-zinc-800/50 border-zinc-700">
                  <CardContent className="p-12 text-center">
                    <p className="text-zinc-400">Aucune personne disponible pour le moment</p>
                    <Button 
                      className="mt-4"
                      variant="outline"
                      onClick={() => fetchAvailableUsers(offerType)}
                    >
                      Rafraîchir la liste
                    </Button>
                  </CardContent>
                </Card>
              ) : (
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {availableUsers.map(availUser => (
                    <Card key={availUser.user_id} className="bg-zinc-800/50 border-zinc-700">
                      <CardContent className="p-6">
                        <div className="flex items-center gap-4">
                          <div className="w-16 h-16 rounded-full bg-zinc-700 overflow-hidden">
                            {availUser.user_image ? (
                              <img src={availUser.user_image} alt="" className="w-full h-full object-cover" />
                            ) : (
                              <div className="w-full h-full flex items-center justify-center text-2xl text-zinc-400">
                                {availUser.user_name?.charAt(0) || '?'}
                              </div>
                            )}
                          </div>
                          <div>
                            <h3 className="text-white font-semibold">{availUser.user_name}</h3>
                            {availUser.bio && (
                              <p className="text-zinc-400 text-sm">{availUser.bio}</p>
                            )}
                            <div className="flex flex-wrap gap-1 mt-2">
                              {availUser.interests?.slice(0, 3).map((interest, i) => (
                                <Badge key={i} variant="secondary" className="text-xs">
                                  {interest}
                                </Badge>
                              ))}
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </TabsContent>
          </Tabs>
        </div>
      </main>

      {/* Create Offer Modal */}
      <Dialog open={showCreateModal} onOpenChange={setShowCreateModal}>
        <DialogContent className="bg-zinc-900 border-zinc-700 text-white max-w-lg">
          <DialogHeader>
            <DialogTitle>Créer une offre pour 2</DialogTitle>
            <DialogDescription className="text-zinc-400">
              Proposez une activité et invitez quelqu'un à vous rejoindre
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4 py-4">
            <div>
              <label className="text-sm text-zinc-400 mb-1 block">Titre *</label>
              <Input
                value={newOffer.title}
                onChange={(e) => setNewOffer({...newOffer, title: e.target.value})}
                placeholder="Ex: Brunch au bord du lac"
                className="bg-zinc-800 border-zinc-700"
              />
            </div>
            
            <div>
              <label className="text-sm text-zinc-400 mb-1 block">Description</label>
              <Textarea
                value={newOffer.description}
                onChange={(e) => setNewOffer({...newOffer, description: e.target.value})}
                placeholder="Décrivez votre offre..."
                className="bg-zinc-800 border-zinc-700"
              />
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm text-zinc-400 mb-1 block">Type *</label>
                <Select
                  value={newOffer.offer_type}
                  onValueChange={(value) => setNewOffer({...newOffer, offer_type: value})}
                >
                  <SelectTrigger className="bg-zinc-800 border-zinc-700">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="friendly">
                      <span className="flex items-center gap-2">
                        <Users className="w-4 h-4 text-emerald-400" /> Amical
                      </span>
                    </SelectItem>
                    <SelectItem value="romantic">
                      <span className="flex items-center gap-2">
                        <Heart className="w-4 h-4 text-pink-400" /> Romantique
                      </span>
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <label className="text-sm text-zinc-400 mb-1 block">Catégorie *</label>
                <Select
                  value={newOffer.category}
                  onValueChange={(value) => setNewOffer({...newOffer, category: value})}
                >
                  <SelectTrigger className="bg-zinc-800 border-zinc-700">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {categories.map(cat => (
                      <SelectItem key={cat.id} value={cat.id}>{cat.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            
            <div>
              <label className="text-sm text-zinc-400 mb-1 block">Lieu</label>
              <Input
                value={newOffer.location}
                onChange={(e) => setNewOffer({...newOffer, location: e.target.value})}
                placeholder="Ex: Lausanne, Ouchy"
                className="bg-zinc-800 border-zinc-700"
              />
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm text-zinc-400 mb-1 block">Date proposée</label>
                <Input
                  type="datetime-local"
                  value={newOffer.proposed_date}
                  onChange={(e) => setNewOffer({...newOffer, proposed_date: e.target.value})}
                  className="bg-zinc-800 border-zinc-700"
                />
              </div>
              <div>
                <label className="text-sm text-zinc-400 mb-1 block">Prix/personne (CHF)</label>
                <Input
                  type="number"
                  value={newOffer.price_per_person}
                  onChange={(e) => setNewOffer({...newOffer, price_per_person: parseFloat(e.target.value) || 0})}
                  className="bg-zinc-800 border-zinc-700"
                />
              </div>
            </div>
            
            {newOffer.offer_type === 'romantic' && !subscriptionStatus?.has_subscription && (
              <div className="bg-pink-600/20 border border-pink-600/50 rounded-lg p-3">
                <p className="text-pink-300 text-sm flex items-center gap-2">
                  <Crown className="w-4 h-4" />
                  Abonnement romantique requis (200 CHF/mois)
                </p>
              </div>
            )}
          </div>
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowCreateModal(false)}>
              Annuler
            </Button>
            <Button onClick={handleCreateOffer} className="bg-amber-600 hover:bg-amber-700">
              Créer l'offre
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Invite Modal */}
      <Dialog open={showInviteModal} onOpenChange={setShowInviteModal}>
        <DialogContent className="bg-zinc-900 border-zinc-700 text-white max-w-lg">
          <DialogHeader>
            <DialogTitle>Inviter quelqu'un</DialogTitle>
            <DialogDescription className="text-zinc-400">
              Choisissez qui vous souhaitez inviter à "{selectedOffer?.title}"
            </DialogDescription>
          </DialogHeader>
          
          <div className="py-4 max-h-96 overflow-y-auto space-y-3">
            {availableUsers.length === 0 ? (
              <p className="text-center text-zinc-400 py-8">
                Aucune personne disponible
              </p>
            ) : (
              availableUsers.map(availUser => (
                <div 
                  key={availUser.user_id}
                  className="flex items-center justify-between p-3 bg-zinc-800/50 rounded-lg hover:bg-zinc-800 cursor-pointer"
                  onClick={() => handleSendInvitation(availUser.user_id)}
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-zinc-700 overflow-hidden">
                      {availUser.user_image ? (
                        <img src={availUser.user_image} alt="" className="w-full h-full object-cover" />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center text-zinc-400">
                          {availUser.user_name?.charAt(0) || '?'}
                        </div>
                      )}
                    </div>
                    <span className="text-white">{availUser.user_name}</span>
                  </div>
                  <Button size="sm" className="bg-amber-600 hover:bg-amber-700">
                    <Send className="w-4 h-4" />
                  </Button>
                </div>
              ))
            )}
          </div>
        </DialogContent>
      </Dialog>

      {/* Subscribe Modal */}
      <Dialog open={showSubscribeModal} onOpenChange={setShowSubscribeModal}>
        <DialogContent className="bg-zinc-900 border-zinc-700 text-white max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Heart className="w-5 h-5 text-pink-400" />
              Abonnement Romantique
            </DialogTitle>
            <DialogDescription className="text-zinc-400">
              Débloquez les fonctionnalités romantiques
            </DialogDescription>
          </DialogHeader>
          
          <div className="py-6 text-center">
            <div className="text-5xl font-bold text-white mb-2">
              200 <span className="text-xl text-zinc-400">CHF/mois</span>
            </div>
            <ul className="text-left space-y-2 mt-6 text-zinc-300">
              <li className="flex items-center gap-2">
                <Check className="w-4 h-4 text-emerald-400" />
                Créer des offres romantiques
              </li>
              <li className="flex items-center gap-2">
                <Check className="w-4 h-4 text-emerald-400" />
                Voir les personnes disponibles
              </li>
              <li className="flex items-center gap-2">
                <Check className="w-4 h-4 text-emerald-400" />
                Chat privé illimité
              </li>
              <li className="flex items-center gap-2">
                <Check className="w-4 h-4 text-emerald-400" />
                Badge Premium
              </li>
            </ul>
          </div>
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowSubscribeModal(false)}>
              Plus tard
            </Button>
            <Button onClick={handleSubscribeRomantic} className="bg-pink-600 hover:bg-pink-700">
              <Crown className="w-4 h-4 mr-2" />
              S'abonner
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Footer />
    </div>
  );
}
