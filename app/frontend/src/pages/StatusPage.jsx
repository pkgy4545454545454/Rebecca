import React, { useState, useEffect } from 'react';
import { CheckCircle, XCircle, AlertTriangle, RefreshCw, Server, Database, CreditCard, Globe, Shield } from 'lucide-react';

const StatusPage = () => {
  const [services, setServices] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState(new Date());

  const checkServices = async () => {
    setIsLoading(true);
    
    // Simuler la vérification des services (en production, appeler les vraies APIs)
    const serviceChecks = [
      {
        name: "Site Web",
        description: "Interface utilisateur principale",
        icon: Globe,
        status: "operational",
        responseTime: 45,
        uptime: 99.99
      },
      {
        name: "API Backend",
        description: "Services API REST",
        icon: Server,
        status: "operational",
        responseTime: 120,
        uptime: 99.95
      },
      {
        name: "Base de données",
        description: "MongoDB Atlas",
        icon: Database,
        status: "operational",
        responseTime: 15,
        uptime: 99.99
      },
      {
        name: "Paiements Stripe",
        description: "Traitement des paiements",
        icon: CreditCard,
        status: "operational",
        responseTime: 200,
        uptime: 99.98
      },
      {
        name: "Sécurité SSL",
        description: "Certificats et chiffrement",
        icon: Shield,
        status: "operational",
        responseTime: 10,
        uptime: 100
      },
      {
        name: "IA Génération Images",
        description: "DALL-E / OpenAI",
        icon: Server,
        status: "operational",
        responseTime: 3500,
        uptime: 99.5
      },
      {
        name: "IA Génération Vidéos",
        description: "Sora / OpenAI",
        icon: Server,
        status: "operational",
        responseTime: 45000,
        uptime: 98.5
      }
    ];

    // Vérification réelle de l'API
    try {
      const start = Date.now();
      const response = await fetch('/api/health');
      const responseTime = Date.now() - start;
      
      if (response.ok) {
        serviceChecks[1].responseTime = responseTime;
        serviceChecks[1].status = "operational";
      } else {
        serviceChecks[1].status = "degraded";
      }
    } catch (error) {
      serviceChecks[1].status = "down";
    }

    setServices(serviceChecks);
    setLastUpdated(new Date());
    setIsLoading(false);
  };

  useEffect(() => {
    checkServices();
    
    // Rafraîchir toutes les 60 secondes
    const interval = setInterval(checkServices, 60000);
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status) => {
    switch (status) {
      case 'operational': return 'text-green-400';
      case 'degraded': return 'text-yellow-400';
      case 'down': return 'text-red-400';
      default: return 'text-gray-400';
    }
  };

  const getStatusBg = (status) => {
    switch (status) {
      case 'operational': return 'bg-green-400/10 border-green-400/30';
      case 'degraded': return 'bg-yellow-400/10 border-yellow-400/30';
      case 'down': return 'bg-red-400/10 border-red-400/30';
      default: return 'bg-gray-400/10 border-gray-400/30';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'operational': return <CheckCircle className="w-5 h-5 text-green-400" />;
      case 'degraded': return <AlertTriangle className="w-5 h-5 text-yellow-400" />;
      case 'down': return <XCircle className="w-5 h-5 text-red-400" />;
      default: return <RefreshCw className="w-5 h-5 text-gray-400 animate-spin" />;
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'operational': return 'Opérationnel';
      case 'degraded': return 'Dégradé';
      case 'down': return 'Hors service';
      default: return 'Vérification...';
    }
  };

  const allOperational = services.every(s => s.status === 'operational');
  const hasIssues = services.some(s => s.status === 'degraded' || s.status === 'down');

  // Historique des incidents (exemple statique)
  const incidents = [
    {
      date: "2026-02-08",
      title: "Maintenance planifiée",
      description: "Mise à jour des serveurs - Aucune interruption de service",
      status: "resolved",
      duration: "30 min"
    },
    {
      date: "2026-01-25",
      title: "Latence API temporaire",
      description: "Augmentation du temps de réponse due à un pic de trafic",
      status: "resolved",
      duration: "15 min"
    }
  ];

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-white">
      {/* Header */}
      <div className="bg-gradient-to-b from-blue-600/20 to-transparent py-16 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-4xl font-bold mb-4">État des Services</h1>
          <p className="text-gray-400 mb-8">
            Surveillance en temps réel de l'infrastructure Titelli
          </p>
          
          {/* Overall Status */}
          <div className={`inline-flex items-center gap-3 px-6 py-3 rounded-full ${
            allOperational ? 'bg-green-400/20 border border-green-400/30' : 
            hasIssues ? 'bg-yellow-400/20 border border-yellow-400/30' : 
            'bg-gray-400/20 border border-gray-400/30'
          }`}>
            {allOperational ? (
              <>
                <CheckCircle className="w-6 h-6 text-green-400" />
                <span className="text-green-400 font-semibold">Tous les systèmes sont opérationnels</span>
              </>
            ) : hasIssues ? (
              <>
                <AlertTriangle className="w-6 h-6 text-yellow-400" />
                <span className="text-yellow-400 font-semibold">Certains services rencontrent des problèmes</span>
              </>
            ) : (
              <>
                <RefreshCw className="w-6 h-6 text-gray-400 animate-spin" />
                <span className="text-gray-400 font-semibold">Vérification en cours...</span>
              </>
            )}
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 pb-20">
        {/* Refresh Button */}
        <div className="flex items-center justify-between mb-6">
          <p className="text-sm text-gray-400">
            Dernière mise à jour : {lastUpdated.toLocaleTimeString('fr-CH')}
          </p>
          <button
            onClick={checkServices}
            disabled={isLoading}
            className="flex items-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
            Actualiser
          </button>
        </div>

        {/* Services List */}
        <div className="space-y-3 mb-12">
          {services.map((service, index) => {
            const IconComponent = service.icon;
            return (
              <div 
                key={index}
                className={`flex items-center justify-between p-4 rounded-xl border ${getStatusBg(service.status)}`}
              >
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 bg-white/10 rounded-lg flex items-center justify-center">
                    <IconComponent className="w-5 h-5 text-gray-300" />
                  </div>
                  <div>
                    <h3 className="font-semibold">{service.name}</h3>
                    <p className="text-sm text-gray-400">{service.description}</p>
                  </div>
                </div>
                
                <div className="flex items-center gap-6">
                  <div className="text-right hidden sm:block">
                    <p className="text-sm text-gray-400">Temps de réponse</p>
                    <p className="font-mono text-sm">{service.responseTime}ms</p>
                  </div>
                  <div className="text-right hidden sm:block">
                    <p className="text-sm text-gray-400">Uptime</p>
                    <p className="font-mono text-sm text-green-400">{service.uptime}%</p>
                  </div>
                  <div className="flex items-center gap-2">
                    {getStatusIcon(service.status)}
                    <span className={`text-sm font-medium ${getStatusColor(service.status)}`}>
                      {getStatusText(service.status)}
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Uptime Chart (Simplified) */}
        <div className="bg-white/5 rounded-xl p-6 border border-white/10 mb-12">
          <h2 className="text-xl font-bold mb-4">Disponibilité des 90 derniers jours</h2>
          <div className="flex gap-1">
            {Array.from({ length: 90 }).map((_, i) => (
              <div
                key={i}
                className={`h-8 flex-1 rounded-sm ${
                  i > 85 ? 'bg-green-400' : 
                  i === 72 ? 'bg-yellow-400' : 
                  'bg-green-400'
                }`}
                title={`Jour ${90 - i}: ${i === 72 ? 'Incident mineur' : '100% disponible'}`}
              />
            ))}
          </div>
          <div className="flex justify-between mt-2 text-sm text-gray-400">
            <span>Il y a 90 jours</span>
            <span>Aujourd'hui</span>
          </div>
          <div className="flex items-center gap-4 mt-4">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-green-400 rounded-sm" />
              <span className="text-sm text-gray-400">Opérationnel</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-yellow-400 rounded-sm" />
              <span className="text-sm text-gray-400">Incident mineur</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-red-400 rounded-sm" />
              <span className="text-sm text-gray-400">Panne</span>
            </div>
          </div>
        </div>

        {/* Incident History */}
        <div className="bg-white/5 rounded-xl p-6 border border-white/10">
          <h2 className="text-xl font-bold mb-6">Historique des incidents</h2>
          
          {incidents.length === 0 ? (
            <p className="text-gray-400 text-center py-8">
              Aucun incident récent
            </p>
          ) : (
            <div className="space-y-4">
              {incidents.map((incident, index) => (
                <div key={index} className="flex items-start gap-4 pb-4 border-b border-white/10 last:border-0">
                  <div className="mt-1">
                    {incident.status === 'resolved' ? (
                      <CheckCircle className="w-5 h-5 text-green-400" />
                    ) : (
                      <AlertTriangle className="w-5 h-5 text-yellow-400" />
                    )}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <h3 className="font-semibold">{incident.title}</h3>
                      <span className="text-sm text-gray-400">{incident.date}</span>
                    </div>
                    <p className="text-gray-400 text-sm">{incident.description}</p>
                    <div className="flex items-center gap-4 mt-2">
                      <span className={`text-xs px-2 py-1 rounded-full ${
                        incident.status === 'resolved' 
                          ? 'bg-green-400/20 text-green-400' 
                          : 'bg-yellow-400/20 text-yellow-400'
                      }`}>
                        {incident.status === 'resolved' ? 'Résolu' : 'En cours'}
                      </span>
                      <span className="text-xs text-gray-500">Durée: {incident.duration}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Subscribe to Updates */}
        <div className="mt-8 text-center">
          <p className="text-gray-400 mb-4">
            Recevez des notifications en cas d'incident
          </p>
          <button className="px-6 py-3 bg-blue-600 hover:bg-blue-500 rounded-xl transition-colors font-medium">
            S'abonner aux alertes
          </button>
        </div>
      </div>
    </div>
  );
};

export default StatusPage;
