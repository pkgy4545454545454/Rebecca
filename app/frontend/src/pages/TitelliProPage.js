/**
 * Titelli Pro++ Page - B2B Services
 * - Regular B2B deliveries
 * - Stock liquidation
 * - Lifestyle Pass integration for enterprises
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
  Truck, Package, Building2, Clock, Calendar, DollarSign,
  Check, Plus, ArrowRight, Sparkles, Crown, TrendingDown,
  BarChart3, Users, Repeat, Tag, Percent
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function TitelliProPage() {
  const { user, token } = useAuth();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  
  // State
  const [activeTab, setActiveTab] = useState('overview');
  const [proStatus, setProStatus] = useState(null);
  const [deliveryClients, setDeliveryClients] = useState([]);
  const [liquidationItems, setLiquidationItems] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // Modal states
  const [showSubscribeModal, setShowSubscribeModal] = useState(false);
  const [showDeliveryModal, setShowDeliveryModal] = useState(false);
  const [showLiquidationModal, setShowLiquidationModal] = useState(false);
  
  // Form state
  const [newDelivery, setNewDelivery] = useState({
    client_name: '',
    client_email: '',
    product_name: '',
    quantity: 1,
    frequency: 'weekly',
    delivery_day: 'monday',
    notes: ''
  });
  
  const [newLiquidation, setNewLiquidation] = useState({
    product_name: '',
    original_price: '',
    liquidation_price: '',
    quantity: 1,
    reason: 'overstock',
    expiry_date: ''
  });

  // Check if user is enterprise
  useEffect(() => {
    if (!user) {
      navigate('/auth');
      return;
    }
    if (user.user_type !== 'enterprise' && user.user_type !== 'entreprise') {
      toast.error('Titelli Pro++ est réservé aux entreprises');
      navigate('/');
      return;
    }
  }, [user, navigate]);

  // Fetch data
  const fetchData = useCallback(async () => {
    if (!token) return;
    
    try {
      setLoading(true);
      
      // Get Pro++ status
      const proRes = await fetch(`${API_URL}/api/pro/status`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (proRes.ok) {
        const data = await proRes.json();
        setProStatus(data);
      }
      
      // Get delivery clients
      const deliveryRes = await fetch(`${API_URL}/api/pro/deliveries`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (deliveryRes.ok) {
        const data = await deliveryRes.json();
        setDeliveryClients(data.deliveries || []);
      }
      
      // Get liquidation items
      const liquidationRes = await fetch(`${API_URL}/api/pro/liquidations`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (liquidationRes.ok) {
        const data = await liquidationRes.json();
        setLiquidationItems(data.items || []);
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
    const success = searchParams.get('success');
    const cancelled = searchParams.get('cancelled');
    
    if (cancelled) {
      toast.error('Paiement annulé');
      setSearchParams({});
      return;
    }
    
    if (success && token) {
      // Confirm subscription payment
      (async () => {
        try {
          const res = await fetch(`${API_URL}/api/pro/subscribe/${success}/confirm`, {
            method: 'POST',
            headers: { Authorization: `Bearer ${token}` }
          });
          
          if (res.ok) {
            toast.success('Titelli Pro++ activé avec succès ! 🎉');
          } else {
            toast.error('Erreur de confirmation du paiement');
          }
        } catch (error) {
          console.error('Error confirming Pro++ subscription:', error);
          toast.error('Erreur de connexion');
        }
        setSearchParams({});
        fetchData();
      })();
    }
  }, [searchParams, token, setSearchParams, fetchData]);

  // Subscribe to Pro++
  const handleSubscribe = async () => {
    try {
      const res = await fetch(`${API_URL}/api/pro/subscribe`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ business_type: 'general' })
      });
      
      const data = await res.json();
      
      if (data.checkout_url) {
        window.location.href = data.checkout_url;
      } else if (data.has_subscription) {
        toast.success('Vous avez déjà Titelli Pro++ !');
        setShowSubscribeModal(false);
        fetchData();
      }
    } catch (error) {
      toast.error('Erreur de connexion');
    }
  };

  // Create delivery client
  const handleCreateDelivery = async () => {
    if (!newDelivery.client_name || !newDelivery.product_name) {
      toast.error('Veuillez remplir les champs obligatoires');
      return;
    }
    
    try {
      const res = await fetch(`${API_URL}/api/pro/deliveries`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(newDelivery)
      });
      
      if (res.ok) {
        toast.success('Client livraison ajouté !');
        setShowDeliveryModal(false);
        setNewDelivery({
          client_name: '',
          client_email: '',
          product_name: '',
          quantity: 1,
          frequency: 'weekly',
          delivery_day: 'monday',
          notes: ''
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

  // Create liquidation item
  const handleCreateLiquidation = async () => {
    if (!newLiquidation.product_name || !newLiquidation.liquidation_price) {
      toast.error('Veuillez remplir les champs obligatoires');
      return;
    }
    
    try {
      const res = await fetch(`${API_URL}/api/pro/liquidations`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          ...newLiquidation,
          original_price: parseFloat(newLiquidation.original_price) || 0,
          liquidation_price: parseFloat(newLiquidation.liquidation_price)
        })
      });
      
      if (res.ok) {
        toast.success('Article en liquidation ajouté !');
        setShowLiquidationModal(false);
        setNewLiquidation({
          product_name: '',
          original_price: '',
          liquidation_price: '',
          quantity: 1,
          reason: 'overstock',
          expiry_date: ''
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

  if (!user || (user.user_type !== 'enterprise' && user.user_type !== 'entreprise')) return null;

  const features = [
    {
      icon: Truck,
      title: 'Livraisons B2B Régulières',
      description: 'Livrez vos produits/services aux entreprises clientes de façon récurrente'
    },
    {
      icon: TrendingDown,
      title: 'Liquidation de Stock',
      description: 'Vendez rapidement votre stock excédentaire à prix réduit'
    },
    {
      icon: Sparkles,
      title: 'Intégration Lifestyle Pass',
      description: 'Proposez vos services dans les Lifestyle Passes Titelli'
    },
    {
      icon: Building2,
      title: 'Clients Entreprises',
      description: 'Accédez au réseau d\'entreprises partenaires Titelli'
    },
    {
      icon: BarChart3,
      title: 'Analytics Avancés',
      description: 'Suivez vos performances B2B en détail'
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-zinc-950 via-zinc-900 to-zinc-950">
      <Header />
      
      <main className="pt-24 pb-16 px-4 md:px-8">
        <div className="max-w-7xl mx-auto">
          
          {/* Hero */}
          <div className="text-center mb-12">
            <Badge className="bg-amber-600 mb-4">
              <Crown className="w-3 h-3 mr-1" /> PRO++
            </Badge>
            <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
              Titelli <span className="text-amber-400">Pro++</span>
            </h1>
            <p className="text-zinc-400 text-lg max-w-2xl mx-auto">
              Solutions B2B avancées pour développer votre activité professionnelle
            </p>
          </div>

          {/* Not subscribed - Show features */}
          {!proStatus?.has_subscription && (
            <div className="mb-12">
              <Card className="bg-gradient-to-br from-amber-900/30 to-zinc-900 border-amber-600/50">
                <CardContent className="p-8">
                  <div className="flex flex-col md:flex-row items-center justify-between gap-8">
                    <div>
                      <h2 className="text-2xl font-bold text-white mb-2">
                        Passez à Titelli Pro++
                      </h2>
                      <p className="text-zinc-300 mb-4">
                        Débloquez toutes les fonctionnalités B2B avancées
                      </p>
                      <div className="text-4xl font-bold text-amber-400">
                        199 <span className="text-lg text-zinc-400">CHF/mois</span>
                      </div>
                    </div>
                    <Button 
                      size="lg" 
                      onClick={() => setShowSubscribeModal(true)}
                      className="bg-amber-600 hover:bg-amber-700 px-8"
                    >
                      <Crown className="w-5 h-5 mr-2" />
                      S'abonner maintenant
                    </Button>
                  </div>
                  
                  <div className="grid md:grid-cols-5 gap-6 mt-8">
                    {features.map((feature, i) => (
                      <div key={i} className="text-center">
                        <div className="w-12 h-12 rounded-full bg-amber-600/20 flex items-center justify-center mx-auto mb-3">
                          <feature.icon className="w-6 h-6 text-amber-400" />
                        </div>
                        <h3 className="text-white font-semibold text-sm mb-1">{feature.title}</h3>
                        <p className="text-zinc-400 text-xs">{feature.description}</p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Subscribed - Show dashboard */}
          {proStatus?.has_subscription && (
            <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
              <TabsList className="bg-zinc-800/50 border border-zinc-700">
                <TabsTrigger value="overview" className="data-[state=active]:bg-amber-600">
                  Vue d'ensemble
                </TabsTrigger>
                <TabsTrigger value="deliveries" className="data-[state=active]:bg-amber-600">
                  Livraisons B2B
                </TabsTrigger>
                <TabsTrigger value="liquidation" className="data-[state=active]:bg-amber-600">
                  Liquidation
                </TabsTrigger>
                <TabsTrigger value="analytics" className="data-[state=active]:bg-amber-600">
                  Analytics
                </TabsTrigger>
              </TabsList>

              {/* Overview Tab */}
              <TabsContent value="overview" className="space-y-6">
                <div className="grid md:grid-cols-4 gap-4">
                  <Card className="bg-zinc-800/50 border-zinc-700">
                    <CardContent className="p-4 text-center">
                      <Truck className="w-8 h-8 text-amber-400 mx-auto mb-2" />
                      <div className="text-2xl font-bold text-white">{deliveryClients.length}</div>
                      <div className="text-sm text-zinc-400">Clients B2B</div>
                    </CardContent>
                  </Card>
                  <Card className="bg-zinc-800/50 border-zinc-700">
                    <CardContent className="p-4 text-center">
                      <Tag className="w-8 h-8 text-emerald-400 mx-auto mb-2" />
                      <div className="text-2xl font-bold text-white">{liquidationItems.length}</div>
                      <div className="text-sm text-zinc-400">Articles en liquidation</div>
                    </CardContent>
                  </Card>
                  <Card className="bg-zinc-800/50 border-zinc-700">
                    <CardContent className="p-4 text-center">
                      <Repeat className="w-8 h-8 text-purple-400 mx-auto mb-2" />
                      <div className="text-2xl font-bold text-white">
                        {deliveryClients.filter(d => d.frequency === 'weekly').length}
                      </div>
                      <div className="text-sm text-zinc-400">Livraisons hebdo</div>
                    </CardContent>
                  </Card>
                  <Card className="bg-zinc-800/50 border-zinc-700">
                    <CardContent className="p-4 text-center">
                      <Crown className="w-8 h-8 text-amber-400 mx-auto mb-2" />
                      <div className="text-lg font-bold text-emerald-400">Actif</div>
                      <div className="text-sm text-zinc-400">Statut Pro++</div>
                    </CardContent>
                  </Card>
                </div>
                
                <div className="grid md:grid-cols-2 gap-6">
                  <Card className="bg-zinc-800/50 border-zinc-700">
                    <CardHeader>
                      <CardTitle className="text-white flex items-center gap-2">
                        <Truck className="w-5 h-5 text-amber-400" />
                        Actions rapides
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <Button 
                        className="w-full justify-start" 
                        variant="outline"
                        onClick={() => setShowDeliveryModal(true)}
                      >
                        <Plus className="w-4 h-4 mr-2" />
                        Ajouter un client B2B
                      </Button>
                      <Button 
                        className="w-full justify-start" 
                        variant="outline"
                        onClick={() => setShowLiquidationModal(true)}
                      >
                        <Tag className="w-4 h-4 mr-2" />
                        Mettre un article en liquidation
                      </Button>
                    </CardContent>
                  </Card>
                  
                  <Card className="bg-zinc-800/50 border-zinc-700">
                    <CardHeader>
                      <CardTitle className="text-white flex items-center gap-2">
                        <Sparkles className="w-5 h-5 text-purple-400" />
                        Lifestyle Pass
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-zinc-400 text-sm mb-4">
                        Vos services peuvent être proposés dans les Lifestyle Passes Titelli
                      </p>
                      <div className="flex gap-2">
                        <Badge className="bg-emerald-600/20 text-emerald-400">Healthy</Badge>
                        <Badge className="bg-purple-600/20 text-purple-400">Better You</Badge>
                        <Badge className="bg-amber-600/20 text-amber-400">MVP</Badge>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>

              {/* Deliveries Tab */}
              <TabsContent value="deliveries" className="space-y-6">
                <div className="flex justify-between items-center">
                  <h2 className="text-xl font-semibold text-white">Clients Livraisons B2B</h2>
                  <Button onClick={() => setShowDeliveryModal(true)} className="bg-amber-600 hover:bg-amber-700">
                    <Plus className="w-4 h-4 mr-2" />
                    Nouveau client
                  </Button>
                </div>
                
                {deliveryClients.length === 0 ? (
                  <Card className="bg-zinc-800/50 border-zinc-700">
                    <CardContent className="p-12 text-center">
                      <Truck className="w-12 h-12 text-zinc-500 mx-auto mb-4" />
                      <p className="text-zinc-400">Aucun client B2B pour le moment</p>
                      <Button 
                        onClick={() => setShowDeliveryModal(true)} 
                        className="mt-4 bg-amber-600 hover:bg-amber-700"
                      >
                        Ajouter votre premier client
                      </Button>
                    </CardContent>
                  </Card>
                ) : (
                  <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {deliveryClients.map(client => (
                      <Card key={client.id} className="bg-zinc-800/50 border-zinc-700">
                        <CardContent className="p-4">
                          <div className="flex items-start justify-between mb-3">
                            <div>
                              <h3 className="text-white font-semibold">{client.client_name}</h3>
                              <p className="text-zinc-400 text-sm">{client.product_name}</p>
                            </div>
                            <Badge className={
                              client.frequency === 'daily' ? 'bg-purple-600' :
                              client.frequency === 'weekly' ? 'bg-amber-600' : 'bg-zinc-600'
                            }>
                              {client.frequency === 'daily' ? 'Quotidien' :
                               client.frequency === 'weekly' ? 'Hebdo' : 'Mensuel'}
                            </Badge>
                          </div>
                          <div className="flex items-center gap-4 text-sm text-zinc-400">
                            <span className="flex items-center gap-1">
                              <Package className="w-3 h-3" /> {client.quantity} unités
                            </span>
                            <span className="flex items-center gap-1">
                              <Calendar className="w-3 h-3" /> {client.delivery_day}
                            </span>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}
              </TabsContent>

              {/* Liquidation Tab */}
              <TabsContent value="liquidation" className="space-y-6">
                <div className="flex justify-between items-center">
                  <h2 className="text-xl font-semibold text-white">Articles en Liquidation</h2>
                  <Button onClick={() => setShowLiquidationModal(true)} className="bg-amber-600 hover:bg-amber-700">
                    <Plus className="w-4 h-4 mr-2" />
                    Nouvel article
                  </Button>
                </div>
                
                {liquidationItems.length === 0 ? (
                  <Card className="bg-zinc-800/50 border-zinc-700">
                    <CardContent className="p-12 text-center">
                      <TrendingDown className="w-12 h-12 text-zinc-500 mx-auto mb-4" />
                      <p className="text-zinc-400">Aucun article en liquidation</p>
                      <Button 
                        onClick={() => setShowLiquidationModal(true)} 
                        className="mt-4 bg-amber-600 hover:bg-amber-700"
                      >
                        Ajouter un article
                      </Button>
                    </CardContent>
                  </Card>
                ) : (
                  <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {liquidationItems.map(item => (
                      <Card key={item.id} className="bg-zinc-800/50 border-zinc-700">
                        <CardContent className="p-4">
                          <div className="flex items-start justify-between mb-3">
                            <h3 className="text-white font-semibold">{item.product_name}</h3>
                            <Badge className="bg-red-600">
                              <Percent className="w-3 h-3 mr-1" />
                              -{Math.round((1 - item.liquidation_price / item.original_price) * 100)}%
                            </Badge>
                          </div>
                          <div className="flex items-center gap-2 mb-2">
                            <span className="text-zinc-500 line-through text-sm">{item.original_price} CHF</span>
                            <span className="text-emerald-400 font-bold">{item.liquidation_price} CHF</span>
                          </div>
                          <div className="text-sm text-zinc-400">
                            {item.quantity} en stock • {item.reason === 'overstock' ? 'Surstock' : 
                             item.reason === 'seasonal' ? 'Fin de saison' : 'Autre'}
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}
              </TabsContent>

              {/* Analytics Tab */}
              <TabsContent value="analytics" className="space-y-6">
                <h2 className="text-xl font-semibold text-white">Analytics B2B</h2>
                <div className="grid md:grid-cols-2 gap-6">
                  <Card className="bg-zinc-800/50 border-zinc-700">
                    <CardHeader>
                      <CardTitle className="text-white">Performance Livraisons</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="h-48 flex items-center justify-center text-zinc-500">
                        <BarChart3 className="w-12 h-12 mr-4" />
                        <span>Graphiques bientôt disponibles</span>
                      </div>
                    </CardContent>
                  </Card>
                  <Card className="bg-zinc-800/50 border-zinc-700">
                    <CardHeader>
                      <CardTitle className="text-white">Ventes Liquidation</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="h-48 flex items-center justify-center text-zinc-500">
                        <TrendingDown className="w-12 h-12 mr-4" />
                        <span>Graphiques bientôt disponibles</span>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>
            </Tabs>
          )}
        </div>
      </main>

      {/* Subscribe Modal */}
      <Dialog open={showSubscribeModal} onOpenChange={setShowSubscribeModal}>
        <DialogContent className="bg-zinc-900 border-zinc-700 text-white max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Crown className="w-5 h-5 text-amber-400" />
              Titelli Pro++
            </DialogTitle>
            <DialogDescription className="text-zinc-400">
              Débloquez toutes les fonctionnalités B2B
            </DialogDescription>
          </DialogHeader>
          
          <div className="py-6 text-center">
            <div className="text-5xl font-bold text-white mb-2">
              199 <span className="text-xl text-zinc-400">CHF/mois</span>
            </div>
            <ul className="text-left space-y-2 mt-6 text-zinc-300">
              {features.map((f, i) => (
                <li key={i} className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-emerald-400" />
                  {f.title}
                </li>
              ))}
            </ul>
          </div>
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowSubscribeModal(false)}>
              Plus tard
            </Button>
            <Button onClick={handleSubscribe} className="bg-amber-600 hover:bg-amber-700">
              <Crown className="w-4 h-4 mr-2" />
              S'abonner
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delivery Modal */}
      <Dialog open={showDeliveryModal} onOpenChange={setShowDeliveryModal}>
        <DialogContent className="bg-zinc-900 border-zinc-700 text-white max-w-lg">
          <DialogHeader>
            <DialogTitle>Nouveau Client B2B</DialogTitle>
            <DialogDescription className="text-zinc-400">
              Configurez une livraison récurrente
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4 py-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm text-zinc-400 mb-1 block">Nom du client *</label>
                <Input
                  value={newDelivery.client_name}
                  onChange={(e) => setNewDelivery({...newDelivery, client_name: e.target.value})}
                  placeholder="Entreprise SA"
                  className="bg-zinc-800 border-zinc-700"
                />
              </div>
              <div>
                <label className="text-sm text-zinc-400 mb-1 block">Email</label>
                <Input
                  value={newDelivery.client_email}
                  onChange={(e) => setNewDelivery({...newDelivery, client_email: e.target.value})}
                  placeholder="contact@entreprise.ch"
                  className="bg-zinc-800 border-zinc-700"
                />
              </div>
            </div>
            
            <div>
              <label className="text-sm text-zinc-400 mb-1 block">Produit/Service *</label>
              <Input
                value={newDelivery.product_name}
                onChange={(e) => setNewDelivery({...newDelivery, product_name: e.target.value})}
                placeholder="Ex: Croissants frais"
                className="bg-zinc-800 border-zinc-700"
              />
            </div>
            
            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="text-sm text-zinc-400 mb-1 block">Quantité</label>
                <Input
                  type="number"
                  value={newDelivery.quantity}
                  onChange={(e) => setNewDelivery({...newDelivery, quantity: parseInt(e.target.value) || 1})}
                  className="bg-zinc-800 border-zinc-700"
                />
              </div>
              <div>
                <label className="text-sm text-zinc-400 mb-1 block">Fréquence</label>
                <Select
                  value={newDelivery.frequency}
                  onValueChange={(value) => setNewDelivery({...newDelivery, frequency: value})}
                >
                  <SelectTrigger className="bg-zinc-800 border-zinc-700">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="daily">Quotidien</SelectItem>
                    <SelectItem value="weekly">Hebdomadaire</SelectItem>
                    <SelectItem value="monthly">Mensuel</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <label className="text-sm text-zinc-400 mb-1 block">Jour de livraison</label>
                <Select
                  value={newDelivery.delivery_day}
                  onValueChange={(value) => setNewDelivery({...newDelivery, delivery_day: value})}
                >
                  <SelectTrigger className="bg-zinc-800 border-zinc-700">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="monday">Lundi</SelectItem>
                    <SelectItem value="tuesday">Mardi</SelectItem>
                    <SelectItem value="wednesday">Mercredi</SelectItem>
                    <SelectItem value="thursday">Jeudi</SelectItem>
                    <SelectItem value="friday">Vendredi</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            
            <div>
              <label className="text-sm text-zinc-400 mb-1 block">Notes</label>
              <Textarea
                value={newDelivery.notes}
                onChange={(e) => setNewDelivery({...newDelivery, notes: e.target.value})}
                placeholder="Instructions spéciales..."
                className="bg-zinc-800 border-zinc-700"
              />
            </div>
          </div>
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowDeliveryModal(false)}>
              Annuler
            </Button>
            <Button onClick={handleCreateDelivery} className="bg-amber-600 hover:bg-amber-700">
              Ajouter le client
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Liquidation Modal */}
      <Dialog open={showLiquidationModal} onOpenChange={setShowLiquidationModal}>
        <DialogContent className="bg-zinc-900 border-zinc-700 text-white max-w-lg">
          <DialogHeader>
            <DialogTitle>Article en Liquidation</DialogTitle>
            <DialogDescription className="text-zinc-400">
              Vendez rapidement votre stock excédentaire
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4 py-4">
            <div>
              <label className="text-sm text-zinc-400 mb-1 block">Nom du produit *</label>
              <Input
                value={newLiquidation.product_name}
                onChange={(e) => setNewLiquidation({...newLiquidation, product_name: e.target.value})}
                placeholder="Ex: T-shirt collection été"
                className="bg-zinc-800 border-zinc-700"
              />
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm text-zinc-400 mb-1 block">Prix original (CHF)</label>
                <Input
                  type="number"
                  value={newLiquidation.original_price}
                  onChange={(e) => setNewLiquidation({...newLiquidation, original_price: e.target.value})}
                  className="bg-zinc-800 border-zinc-700"
                />
              </div>
              <div>
                <label className="text-sm text-zinc-400 mb-1 block">Prix liquidation (CHF) *</label>
                <Input
                  type="number"
                  value={newLiquidation.liquidation_price}
                  onChange={(e) => setNewLiquidation({...newLiquidation, liquidation_price: e.target.value})}
                  className="bg-zinc-800 border-zinc-700"
                />
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm text-zinc-400 mb-1 block">Quantité</label>
                <Input
                  type="number"
                  value={newLiquidation.quantity}
                  onChange={(e) => setNewLiquidation({...newLiquidation, quantity: parseInt(e.target.value) || 1})}
                  className="bg-zinc-800 border-zinc-700"
                />
              </div>
              <div>
                <label className="text-sm text-zinc-400 mb-1 block">Raison</label>
                <Select
                  value={newLiquidation.reason}
                  onValueChange={(value) => setNewLiquidation({...newLiquidation, reason: value})}
                >
                  <SelectTrigger className="bg-zinc-800 border-zinc-700">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="overstock">Surstock</SelectItem>
                    <SelectItem value="seasonal">Fin de saison</SelectItem>
                    <SelectItem value="expiring">Proche expiration</SelectItem>
                    <SelectItem value="other">Autre</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowLiquidationModal(false)}>
              Annuler
            </Button>
            <Button onClick={handleCreateLiquidation} className="bg-amber-600 hover:bg-amber-700">
              Publier en liquidation
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Footer />
    </div>
  );
}
