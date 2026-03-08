/**
 * Demandes Spécialistes & Lifestyle Passes Page
 * - AI-powered specialist search
 * - Create/browse specialist requests
 * - Lifestyle passes subscription
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
  Search, Send, Clock, MapPin, DollarSign, AlertTriangle,
  Sparkles, Heart, Crown, Star, Check, Plus, ArrowRight,
  Briefcase, GraduationCap, Home, Utensils, Laptop
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Category icons
const categoryIcons = {
  beaute: Sparkles,
  sante: Heart,
  artisanat: Briefcase,
  restauration: Utensils,
  mode: Star,
  tech: Laptop,
  education: GraduationCap,
  evenements: Star,
  immobilier: Home,
  autre: Briefcase
};

// Urgency colors
const urgencyColors = {
  urgent: 'bg-red-600',
  normal: 'bg-amber-600',
  flexible: 'bg-emerald-600'
};

export default function SpecialistsPage() {
  const { user, token } = useAuth();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  
  // State
  const [activeTab, setActiveTab] = useState('search');
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [requests, setRequests] = useState([]);
  const [myRequests, setMyRequests] = useState([]);
  const [categories, setCategories] = useState([]);
  const [lifestylePasses, setLifestylePasses] = useState({});
  const [myPasses, setMyPasses] = useState([]);
  const [loading, setLoading] = useState(false);
  
  // Modal states
  const [showRequestModal, setShowRequestModal] = useState(false);
  const [showPassModal, setShowPassModal] = useState(false);
  const [selectedPass, setSelectedPass] = useState(null);
  const [selectedRequest, setSelectedRequest] = useState(null);
  const [showResponseModal, setShowResponseModal] = useState(false);
  
  // Form state
  const [newRequest, setNewRequest] = useState({
    title: '',
    description: '',
    category: 'beaute',
    urgency: 'normal',
    budget_min: '',
    budget_max: '',
    location: ''
  });
  
  const [response, setResponse] = useState({
    message: '',
    proposed_price: '',
    estimated_time: ''
  });

  // Fetch data
  const fetchData = useCallback(async () => {
    if (!token) return;
    
    try {
      setLoading(true);
      
      const [requestsRes, myRequestsRes, categoriesRes, passesRes, myPassesRes] = await Promise.all([
        fetch(`${API_URL}/api/specialists/requests`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        fetch(`${API_URL}/api/specialists/requests/my`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        fetch(`${API_URL}/api/specialists/categories`),
        fetch(`${API_URL}/api/specialists/passes`),
        fetch(`${API_URL}/api/specialists/passes/my`, {
          headers: { Authorization: `Bearer ${token}` }
        })
      ]);
      
      if (requestsRes.ok) {
        const data = await requestsRes.json();
        setRequests(data.requests || []);
      }
      
      if (myRequestsRes.ok) {
        const data = await myRequestsRes.json();
        setMyRequests(data.requests || []);
      }
      
      if (categoriesRes.ok) {
        const data = await categoriesRes.json();
        setCategories(data.categories || []);
      }
      
      if (passesRes.ok) {
        const data = await passesRes.json();
        setLifestylePasses(data.passes || {});
      }
      
      if (myPassesRes.ok) {
        const data = await myPassesRes.json();
        setMyPasses(data.passes || []);
      }
      
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Handle Stripe return
  useEffect(() => {
    const passSuccess = searchParams.get('pass_success');
    const passCancelled = searchParams.get('pass_cancelled');
    
    if (passCancelled) {
      toast.error('Paiement annulé');
      setSearchParams({});
      return;
    }
    
    if (passSuccess && token) {
      (async () => {
        try {
          const res = await fetch(`${API_URL}/api/specialists/passes/${passSuccess}/confirm`, {
            method: 'POST',
            headers: { Authorization: `Bearer ${token}` }
          });
          
          if (res.ok) {
            toast.success('Pass activé avec succès ! 🎉');
          } else {
            toast.error('Erreur de confirmation du paiement');
          }
        } catch (error) {
          console.error('Error confirming pass:', error);
          toast.error('Erreur de connexion');
        }
        setSearchParams({});
        fetchData();
      })();
    }
  }, [searchParams, token, setSearchParams, fetchData]);

  // AI Search
  const handleAISearch = async () => {
    if (!searchQuery.trim() || searchQuery.length < 10) {
      toast.error('Votre recherche doit faire au moins 10 caractères');
      return;
    }
    
    try {
      setLoading(true);
      const res = await fetch(`${API_URL}/api/specialists/search/ai?query=${encodeURIComponent(searchQuery)}`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (res.ok) {
        const data = await res.json();
        setSearchResults(data.results || []);
        toast.success(`${data.count} résultat(s) trouvé(s)`);
      }
    } catch (error) {
      toast.error('Erreur de recherche');
    } finally {
      setLoading(false);
    }
  };

  // Create request
  const handleCreateRequest = async () => {
    if (!newRequest.title || !newRequest.description) {
      toast.error('Veuillez remplir tous les champs obligatoires');
      return;
    }
    
    try {
      const res = await fetch(`${API_URL}/api/specialists/requests`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          ...newRequest,
          budget_min: newRequest.budget_min ? parseFloat(newRequest.budget_min) : null,
          budget_max: newRequest.budget_max ? parseFloat(newRequest.budget_max) : null
        })
      });
      
      if (res.ok) {
        toast.success('Demande créée avec succès !');
        setShowRequestModal(false);
        setNewRequest({
          title: '',
          description: '',
          category: 'beaute',
          urgency: 'normal',
          budget_min: '',
          budget_max: '',
          location: ''
        });
        fetchData();
      } else {
        const data = await res.json();
        toast.error(data.detail || 'Erreur');
      }
    } catch (error) {
      toast.error('Erreur de connexion');
    }
  };

  // Subscribe to pass
  const handleSubscribePass = async (passType) => {
    try {
      const res = await fetch(`${API_URL}/api/specialists/passes/subscribe`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ pass_type: passType })
      });
      
      const data = await res.json();
      
      if (data.checkout_url) {
        window.location.href = data.checkout_url;
      } else if (data.has_subscription) {
        toast.success('Vous avez déjà ce pass !');
        setShowPassModal(false);
      }
    } catch (error) {
      toast.error('Erreur de connexion');
    }
  };

  // Respond to request (for enterprises)
  const handleRespondToRequest = async () => {
    if (!response.message || !selectedRequest) {
      toast.error('Veuillez écrire un message');
      return;
    }
    
    try {
      const res = await fetch(`${API_URL}/api/specialists/requests/${selectedRequest.id}/respond`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          request_id: selectedRequest.id,
          message: response.message,
          proposed_price: response.proposed_price ? parseFloat(response.proposed_price) : null,
          estimated_time: response.estimated_time || null
        })
      });
      
      if (res.ok) {
        toast.success('Réponse envoyée !');
        setShowResponseModal(false);
        setResponse({ message: '', proposed_price: '', estimated_time: '' });
        setSelectedRequest(null);
      } else {
        const data = await res.json();
        toast.error(data.detail || 'Erreur');
      }
    } catch (error) {
      toast.error('Erreur de connexion');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-zinc-950 via-zinc-900 to-zinc-950">
      <Header />
      
      <main className="pt-24 pb-16 px-4 md:px-8">
        <div className="max-w-7xl mx-auto">
          
          {/* Hero */}
          <div className="text-center mb-12">
            <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
              Demandes <span className="text-amber-400">Spécialistes</span>
            </h1>
            <p className="text-zinc-400 text-lg max-w-2xl mx-auto">
              Trouvez le spécialiste idéal avec notre recherche IA ou publiez votre demande
            </p>
          </div>

          {/* AI Search Box */}
          <Card className="bg-zinc-800/50 border-zinc-700 mb-8">
            <CardContent className="p-6">
              <div className="flex gap-4">
                <div className="flex-1 relative">
                  <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-400" />
                  <Input
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Ex: Trouvez-moi un spécialiste qui sait faire des mini bagues sur mesure..."
                    className="pl-12 bg-zinc-900 border-zinc-600 h-12 text-white"
                    onKeyDown={(e) => e.key === 'Enter' && handleAISearch()}
                  />
                </div>
                <Button 
                  onClick={handleAISearch}
                  disabled={loading}
                  className="bg-amber-600 hover:bg-amber-700 h-12 px-8"
                >
                  <Sparkles className="w-4 h-4 mr-2" />
                  Recherche IA
                </Button>
              </div>
              
              {searchResults.length > 0 && (
                <div className="mt-6 grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {searchResults.map((result, i) => (
                    <Card key={i} className="bg-zinc-900/50 border-zinc-700">
                      <CardContent className="p-4">
                        <h3 className="text-white font-semibold">{result.business_name || result.name}</h3>
                        <p className="text-zinc-400 text-sm mt-1">{result.description?.substring(0, 100)}...</p>
                        <div className="flex items-center gap-2 mt-2">
                          {result.rating && (
                            <Badge className="bg-amber-600/20 text-amber-400">
                              <Star className="w-3 h-3 mr-1" /> {result.rating}
                            </Badge>
                          )}
                          {result.location && (
                            <span className="text-xs text-zinc-500">
                              <MapPin className="w-3 h-3 inline mr-1" />{result.location}
                            </span>
                          )}
                        </div>
                        <Button 
                          size="sm" 
                          className="mt-3 w-full"
                          onClick={() => navigate(`/entreprise/${result.id}`)}
                        >
                          Voir le profil
                        </Button>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Main Tabs */}
          <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
            <TabsList className="bg-zinc-800/50 border border-zinc-700">
              <TabsTrigger value="search" className="data-[state=active]:bg-amber-600">
                Demandes
              </TabsTrigger>
              <TabsTrigger value="my-requests" className="data-[state=active]:bg-amber-600">
                Mes Demandes
              </TabsTrigger>
              <TabsTrigger value="passes" className="data-[state=active]:bg-amber-600">
                Lifestyle Pass
              </TabsTrigger>
            </TabsList>

            {/* Requests Tab */}
            <TabsContent value="search" className="space-y-6">
              <div className="flex justify-between items-center">
                <h2 className="text-xl font-semibold text-white">Demandes Urgentes & Spécifiques</h2>
                <Button onClick={() => setShowRequestModal(true)} className="bg-amber-600 hover:bg-amber-700">
                  <Plus className="w-4 h-4 mr-2" />
                  Créer une demande
                </Button>
              </div>
              
              {requests.length === 0 ? (
                <Card className="bg-zinc-800/50 border-zinc-700">
                  <CardContent className="p-12 text-center">
                    <Search className="w-12 h-12 text-zinc-500 mx-auto mb-4" />
                    <p className="text-zinc-400">Aucune demande pour le moment</p>
                  </CardContent>
                </Card>
              ) : (
                <div className="grid md:grid-cols-2 gap-6">
                  {requests.map(req => {
                    const CategoryIcon = categoryIcons[req.category] || Briefcase;
                    return (
                      <Card key={req.id} className="bg-zinc-800/50 border-zinc-700 hover:border-amber-600/50 transition-all">
                        <CardHeader className="pb-2">
                          <div className="flex items-start justify-between">
                            <div className="flex items-center gap-3">
                              <div className="w-10 h-10 rounded-full bg-amber-600/20 flex items-center justify-center">
                                <CategoryIcon className="w-5 h-5 text-amber-400" />
                              </div>
                              <div>
                                <CardTitle className="text-white text-lg">{req.title}</CardTitle>
                                <CardDescription>par {req.user_name}</CardDescription>
                              </div>
                            </div>
                            <Badge className={urgencyColors[req.urgency]}>
                              {req.urgency === 'urgent' && <AlertTriangle className="w-3 h-3 mr-1" />}
                              {req.urgency}
                            </Badge>
                          </div>
                        </CardHeader>
                        <CardContent>
                          <p className="text-zinc-300 text-sm mb-3">{req.description?.substring(0, 150)}...</p>
                          <div className="flex flex-wrap gap-2 text-sm text-zinc-400">
                            {req.location && (
                              <span className="flex items-center gap-1">
                                <MapPin className="w-3 h-3" /> {req.location}
                              </span>
                            )}
                            {(req.budget_min || req.budget_max) && (
                              <span className="flex items-center gap-1">
                                <DollarSign className="w-3 h-3" />
                                {req.budget_min && `${req.budget_min} CHF`}
                                {req.budget_min && req.budget_max && ' - '}
                                {req.budget_max && `${req.budget_max} CHF`}
                              </span>
                            )}
                            <span className="flex items-center gap-1">
                              <Send className="w-3 h-3" /> {req.responses_count} réponse(s)
                            </span>
                          </div>
                        </CardContent>
                        {user?.user_type === 'enterprise' && (
                          <CardFooter>
                            <Button 
                              className="w-full"
                              onClick={() => {
                                setSelectedRequest(req);
                                setShowResponseModal(true);
                              }}
                            >
                              Répondre à la demande
                            </Button>
                          </CardFooter>
                        )}
                      </Card>
                    );
                  })}
                </div>
              )}
            </TabsContent>

            {/* My Requests Tab */}
            <TabsContent value="my-requests" className="space-y-6">
              <h2 className="text-xl font-semibold text-white">Mes Demandes</h2>
              
              {myRequests.length === 0 ? (
                <Card className="bg-zinc-800/50 border-zinc-700">
                  <CardContent className="p-12 text-center">
                    <p className="text-zinc-400">Vous n'avez pas encore créé de demande</p>
                    <Button 
                      onClick={() => setShowRequestModal(true)} 
                      className="mt-4 bg-amber-600 hover:bg-amber-700"
                    >
                      Créer ma première demande
                    </Button>
                  </CardContent>
                </Card>
              ) : (
                <div className="space-y-4">
                  {myRequests.map(req => (
                    <Card key={req.id} className="bg-zinc-800/50 border-zinc-700">
                      <CardContent className="p-6">
                        <div className="flex items-center justify-between">
                          <div>
                            <h3 className="text-white font-semibold">{req.title}</h3>
                            <p className="text-zinc-400 text-sm mt-1">{req.description?.substring(0, 100)}...</p>
                          </div>
                          <div className="text-right">
                            <Badge className={
                              req.status === 'matched' ? 'bg-emerald-600' :
                              req.status === 'open' ? 'bg-amber-600' : 'bg-zinc-600'
                            }>
                              {req.status === 'matched' ? 'Trouvé' : req.status === 'open' ? 'En cours' : req.status}
                            </Badge>
                            <p className="text-zinc-500 text-xs mt-1">{req.responses_count} réponse(s)</p>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </TabsContent>

            {/* Lifestyle Passes Tab */}
            <TabsContent value="passes" className="space-y-6">
              <h2 className="text-xl font-semibold text-white">Lifestyle Passes</h2>
              <p className="text-zinc-400">Accédez à des prestations exclusives dans les domaines de votre choix</p>
              
              {/* My Active Passes */}
              {myPasses.length > 0 && (
                <div className="mb-8">
                  <h3 className="text-lg font-semibold text-white mb-4">Mes Pass Actifs</h3>
                  <div className="flex flex-wrap gap-4">
                    {myPasses.map(pass => (
                      <Badge key={pass.id} className="bg-emerald-600 px-4 py-2">
                        <Check className="w-4 h-4 mr-2" />
                        {pass.pass_name}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Available Passes */}
              <div className="grid md:grid-cols-3 gap-6">
                {Object.entries(lifestylePasses).map(([key, pass]) => (
                  <Card 
                    key={key} 
                    className={`bg-zinc-800/50 border-zinc-700 hover:border-amber-600/50 transition-all ${
                      key === 'mvp' ? 'border-amber-600' : ''
                    }`}
                  >
                    <CardHeader>
                      <div className="flex items-center gap-2">
                        {key === 'healthy' && <Heart className="w-5 h-5 text-emerald-400" />}
                        {key === 'better_you' && <Sparkles className="w-5 h-5 text-purple-400" />}
                        {key === 'mvp' && <Crown className="w-5 h-5 text-amber-400" />}
                        <CardTitle className="text-white">{pass.name}</CardTitle>
                      </div>
                      <CardDescription>{pass.description}</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="text-3xl font-bold text-white mb-4">
                        {pass.price} <span className="text-lg text-zinc-400">CHF/mois</span>
                      </div>
                      <ul className="space-y-2">
                        {pass.features?.map((feature, i) => (
                          <li key={i} className="flex items-center gap-2 text-zinc-300 text-sm">
                            <Check className="w-4 h-4 text-emerald-400" />
                            {feature}
                          </li>
                        ))}
                      </ul>
                    </CardContent>
                    <CardFooter>
                      <Button 
                        className={`w-full ${key === 'mvp' ? 'bg-amber-600 hover:bg-amber-700' : ''}`}
                        onClick={() => handleSubscribePass(key)}
                      >
                        S'abonner
                        <ArrowRight className="w-4 h-4 ml-2" />
                      </Button>
                    </CardFooter>
                  </Card>
                ))}
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </main>

      {/* Create Request Modal */}
      <Dialog open={showRequestModal} onOpenChange={setShowRequestModal}>
        <DialogContent className="bg-zinc-900 border-zinc-700 text-white max-w-lg">
          <DialogHeader>
            <DialogTitle>Créer une demande</DialogTitle>
            <DialogDescription className="text-zinc-400">
              Décrivez précisément ce que vous recherchez
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4 py-4">
            <div>
              <label className="text-sm text-zinc-400 mb-1 block">Titre *</label>
              <Input
                value={newRequest.title}
                onChange={(e) => setNewRequest({...newRequest, title: e.target.value})}
                placeholder="Ex: Recherche bijoutier pour bague sur mesure"
                className="bg-zinc-800 border-zinc-700"
              />
            </div>
            
            <div>
              <label className="text-sm text-zinc-400 mb-1 block">Description *</label>
              <Textarea
                value={newRequest.description}
                onChange={(e) => setNewRequest({...newRequest, description: e.target.value})}
                placeholder="Décrivez votre besoin en détail..."
                className="bg-zinc-800 border-zinc-700 min-h-[100px]"
              />
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm text-zinc-400 mb-1 block">Catégorie</label>
                <Select
                  value={newRequest.category}
                  onValueChange={(value) => setNewRequest({...newRequest, category: value})}
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
              
              <div>
                <label className="text-sm text-zinc-400 mb-1 block">Urgence</label>
                <Select
                  value={newRequest.urgency}
                  onValueChange={(value) => setNewRequest({...newRequest, urgency: value})}
                >
                  <SelectTrigger className="bg-zinc-800 border-zinc-700">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="urgent">🔴 Urgent</SelectItem>
                    <SelectItem value="normal">🟡 Normal</SelectItem>
                    <SelectItem value="flexible">🟢 Flexible</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm text-zinc-400 mb-1 block">Budget min (CHF)</label>
                <Input
                  type="number"
                  value={newRequest.budget_min}
                  onChange={(e) => setNewRequest({...newRequest, budget_min: e.target.value})}
                  className="bg-zinc-800 border-zinc-700"
                />
              </div>
              <div>
                <label className="text-sm text-zinc-400 mb-1 block">Budget max (CHF)</label>
                <Input
                  type="number"
                  value={newRequest.budget_max}
                  onChange={(e) => setNewRequest({...newRequest, budget_max: e.target.value})}
                  className="bg-zinc-800 border-zinc-700"
                />
              </div>
            </div>
            
            <div>
              <label className="text-sm text-zinc-400 mb-1 block">Localisation</label>
              <Input
                value={newRequest.location}
                onChange={(e) => setNewRequest({...newRequest, location: e.target.value})}
                placeholder="Ex: Lausanne"
                className="bg-zinc-800 border-zinc-700"
              />
            </div>
          </div>
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowRequestModal(false)}>
              Annuler
            </Button>
            <Button onClick={handleCreateRequest} className="bg-amber-600 hover:bg-amber-700">
              Publier la demande
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Response Modal (for enterprises) */}
      <Dialog open={showResponseModal} onOpenChange={setShowResponseModal}>
        <DialogContent className="bg-zinc-900 border-zinc-700 text-white max-w-lg">
          <DialogHeader>
            <DialogTitle>Répondre à la demande</DialogTitle>
            <DialogDescription className="text-zinc-400">
              {selectedRequest?.title}
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4 py-4">
            <div>
              <label className="text-sm text-zinc-400 mb-1 block">Votre message *</label>
              <Textarea
                value={response.message}
                onChange={(e) => setResponse({...response, message: e.target.value})}
                placeholder="Présentez votre expertise et votre proposition..."
                className="bg-zinc-800 border-zinc-700 min-h-[100px]"
              />
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm text-zinc-400 mb-1 block">Prix proposé (CHF)</label>
                <Input
                  type="number"
                  value={response.proposed_price}
                  onChange={(e) => setResponse({...response, proposed_price: e.target.value})}
                  className="bg-zinc-800 border-zinc-700"
                />
              </div>
              <div>
                <label className="text-sm text-zinc-400 mb-1 block">Délai estimé</label>
                <Input
                  value={response.estimated_time}
                  onChange={(e) => setResponse({...response, estimated_time: e.target.value})}
                  placeholder="Ex: 2 semaines"
                  className="bg-zinc-800 border-zinc-700"
                />
              </div>
            </div>
          </div>
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowResponseModal(false)}>
              Annuler
            </Button>
            <Button onClick={handleRespondToRequest} className="bg-amber-600 hover:bg-amber-700">
              Envoyer la réponse
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Footer />
    </div>
  );
}
