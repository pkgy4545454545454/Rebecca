/**
 * Email Preferences Component for Titelli
 * Allows users to manage their email notification preferences
 */
import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/card';
import { Button } from './ui/button';
import { Switch } from './ui/switch';
import { toast } from 'sonner';
import { 
  Mail, Bell, Gift, ShoppingBag, Calendar, 
  Trophy, Users, CreditCard, Settings, Check
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const EMAIL_CATEGORIES = [
  {
    id: 'referral',
    title: 'Parrainage',
    description: 'Notifications quand quelqu\'un utilise votre code',
    icon: Gift,
    color: 'text-purple-400',
    bgColor: 'bg-purple-500/20',
  },
  {
    id: 'payments',
    title: 'Paiements',
    description: 'Confirmations de paiement et factures',
    icon: CreditCard,
    color: 'text-emerald-400',
    bgColor: 'bg-emerald-500/20',
  },
  {
    id: 'orders',
    title: 'Commandes',
    description: 'Mises à jour sur vos commandes',
    icon: ShoppingBag,
    color: 'text-blue-400',
    bgColor: 'bg-blue-500/20',
  },
  {
    id: 'rdv',
    title: 'RDV chez Titelli',
    description: 'Invitations et messages de rencontres',
    icon: Calendar,
    color: 'text-pink-400',
    bgColor: 'bg-pink-500/20',
  },
  {
    id: 'sports',
    title: 'Sports',
    description: 'Matchs et compétitions',
    icon: Trophy,
    color: 'text-amber-400',
    bgColor: 'bg-amber-500/20',
  },
  {
    id: 'promotions',
    title: 'Promotions',
    description: 'Offres spéciales et réductions',
    icon: Bell,
    color: 'text-red-400',
    bgColor: 'bg-red-500/20',
  },
  {
    id: 'newsletter',
    title: 'Newsletter',
    description: 'Actualités et nouveautés Titelli',
    icon: Mail,
    color: 'text-cyan-400',
    bgColor: 'bg-cyan-500/20',
  },
  {
    id: 'community',
    title: 'Communauté',
    description: 'Nouveaux abonnés et interactions',
    icon: Users,
    color: 'text-orange-400',
    bgColor: 'bg-orange-500/20',
  },
];

export default function EmailPreferences() {
  const { token } = useAuth();
  const [preferences, setPreferences] = useState({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [masterEnabled, setMasterEnabled] = useState(true);

  const fetchPreferences = useCallback(async () => {
    if (!token) return;
    
    try {
      setLoading(true);
      const res = await fetch(`${API_URL}/api/notifications/email-preferences`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (res.ok) {
        const data = await res.json();
        setPreferences(data.preferences || {});
        setMasterEnabled(data.email_enabled !== false);
      } else {
        // Default all to true if not set
        const defaults = {};
        EMAIL_CATEGORIES.forEach(cat => {
          defaults[cat.id] = true;
        });
        setPreferences(defaults);
      }
    } catch (error) {
      console.error('Error fetching preferences:', error);
      // Set defaults
      const defaults = {};
      EMAIL_CATEGORIES.forEach(cat => {
        defaults[cat.id] = true;
      });
      setPreferences(defaults);
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    fetchPreferences();
  }, [fetchPreferences]);

  const handleToggle = (categoryId) => {
    setPreferences(prev => ({
      ...prev,
      [categoryId]: !prev[categoryId]
    }));
  };

  const handleMasterToggle = () => {
    const newValue = !masterEnabled;
    setMasterEnabled(newValue);
    
    // If disabling master, keep individual preferences but they won't receive emails
    if (!newValue) {
      toast.info('Tous les emails sont désactivés');
    }
  };

  const handleSave = async () => {
    setSaving(true);
    
    try {
      const res = await fetch(`${API_URL}/api/notifications/email-preferences`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          email_enabled: masterEnabled,
          preferences: preferences
        })
      });
      
      if (res.ok) {
        toast.success('Préférences enregistrées !');
      } else {
        toast.error('Erreur lors de la sauvegarde');
      }
    } catch (error) {
      console.error('Error saving preferences:', error);
      toast.error('Erreur de connexion');
    } finally {
      setSaving(false);
    }
  };

  const enabledCount = Object.values(preferences).filter(Boolean).length;

  if (loading) {
    return (
      <Card className="bg-zinc-800/50 border-zinc-700">
        <CardContent className="p-6 text-center">
          <div className="animate-pulse text-zinc-400">Chargement...</div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {/* Master Switch Card */}
      <Card className="bg-gradient-to-br from-zinc-800 to-zinc-900 border-zinc-700">
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-500/20 rounded-lg">
                <Mail className="w-5 h-5 text-blue-400" />
              </div>
              <div>
                <CardTitle className="text-white text-lg">Notifications Email</CardTitle>
                <CardDescription className="text-zinc-400">
                  {masterEnabled 
                    ? `${enabledCount} catégorie(s) activée(s)`
                    : 'Toutes les notifications désactivées'
                  }
                </CardDescription>
              </div>
            </div>
            <Switch
              checked={masterEnabled}
              onCheckedChange={handleMasterToggle}
            />
          </div>
        </CardHeader>
      </Card>

      {/* Individual Preferences */}
      <Card className={`bg-zinc-800/50 border-zinc-700 ${!masterEnabled ? 'opacity-50' : ''}`}>
        <CardHeader>
          <CardTitle className="text-white text-lg flex items-center gap-2">
            <Settings className="w-5 h-5 text-zinc-400" />
            Préférences par catégorie
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {EMAIL_CATEGORIES.map((category) => (
            <div 
              key={category.id}
              className={`flex items-center justify-between p-3 rounded-lg transition-colors ${
                preferences[category.id] && masterEnabled
                  ? 'bg-zinc-900/50'
                  : 'bg-zinc-900/30'
              }`}
            >
              <div className="flex items-center gap-3">
                <div className={`p-2 rounded-lg ${category.bgColor}`}>
                  <category.icon className={`w-4 h-4 ${category.color}`} />
                </div>
                <div>
                  <p className="text-white text-sm font-medium">{category.title}</p>
                  <p className="text-zinc-500 text-xs">{category.description}</p>
                </div>
              </div>
              <Switch
                checked={preferences[category.id] ?? true}
                onCheckedChange={() => handleToggle(category.id)}
                disabled={!masterEnabled}
              />
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Save Button */}
      <Button 
        onClick={handleSave}
        disabled={saving}
        className="w-full bg-blue-600 hover:bg-blue-700"
      >
        {saving ? (
          <span className="flex items-center gap-2">
            <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            Enregistrement...
          </span>
        ) : (
          <span className="flex items-center gap-2">
            <Check className="w-4 h-4" />
            Enregistrer les préférences
          </span>
        )}
      </Button>

      {/* Info */}
      <p className="text-xs text-zinc-500 text-center px-4">
        Vous pouvez modifier ces préférences à tout moment. Les emails transactionnels importants 
        (confirmations de paiement, sécurité) seront toujours envoyés.
      </p>
    </div>
  );
}
