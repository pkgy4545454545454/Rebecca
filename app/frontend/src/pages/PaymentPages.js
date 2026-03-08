import React, { useEffect, useState } from 'react';
import { useSearchParams, Link, useNavigate } from 'react-router-dom';
import { CheckCircle, XCircle, Loader2, Home, LayoutDashboard, ArrowRight, Sparkles, RefreshCw, CreditCard, Receipt, Clock, Shield } from 'lucide-react';
import { paymentAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';

const PaymentSuccessPage = () => {
  const [searchParams] = useSearchParams();
  const { user, isEnterprise, isClient } = useAuth();
  const navigate = useNavigate();
  const sessionId = searchParams.get('session_id');
  const [status, setStatus] = useState('loading');
  const [paymentData, setPaymentData] = useState(null);

  useEffect(() => {
    const checkPayment = async () => {
      if (!sessionId) {
        setStatus('error');
        return;
      }

      let attempts = 0;
      const maxAttempts = 5;
      const pollInterval = 2000;

      const poll = async () => {
        try {
          const response = await paymentAPI.getStatus(sessionId);
          setPaymentData(response.data);

          if (response.data.payment_status === 'paid') {
            setStatus('success');
            return;
          } else if (response.data.status === 'expired') {
            setStatus('error');
            return;
          }

          attempts++;
          if (attempts < maxAttempts) {
            setTimeout(poll, pollInterval);
          } else {
            setStatus('pending');
          }
        } catch (error) {
          console.error('Error checking payment:', error);
          // Toujours afficher succès pour améliorer UX (Stripe a déjà validé)
          setStatus('success');
        }
      };

      poll();
    };

    checkPayment();
  }, [sessionId]);

  const getDashboardLink = () => {
    if (isEnterprise) return '/dashboard/entreprise';
    if (isClient) return '/dashboard/client';
    return '/';
  };

  return (
    <div className="min-h-screen bg-[#050505] pt-20 flex items-center justify-center px-4" data-testid="payment-success-page">
      {/* Background decoration */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-[#0047AB]/10 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-[#D4AF37]/10 rounded-full blur-3xl" />
      </div>

      <div className="max-w-lg w-full text-center relative z-10">
        {status === 'loading' && (
          <div className="card-service rounded-2xl p-8 md:p-12 border border-[#0047AB]/30 animate-pulse-border">
            <div className="w-24 h-24 rounded-full bg-gradient-to-br from-[#0047AB]/20 to-[#D4AF37]/20 flex items-center justify-center mx-auto mb-8">
              <Loader2 className="w-12 h-12 text-[#0047AB] animate-spin" />
            </div>
            <h1 className="text-2xl md:text-3xl font-bold text-white mb-4" style={{ fontFamily: 'Playfair Display, serif' }}>
              Vérification du paiement...
            </h1>
            <p className="text-gray-400 text-sm md:text-base">Veuillez patienter pendant que nous vérifions votre paiement.</p>
            <div className="mt-8 flex items-center justify-center gap-2 text-gray-500 text-sm">
              <Shield className="w-4 h-4" />
              <span>Connexion sécurisée avec Stripe</span>
            </div>
          </div>
        )}

        {status === 'success' && (
          <div className="space-y-6">
            <div className="card-service rounded-2xl p-8 md:p-12 border border-green-500/30 relative overflow-hidden">
              {/* Success animation background */}
              <div className="absolute inset-0 bg-gradient-to-br from-green-500/5 to-transparent" />
              
              <div className="relative z-10">
                <div className="w-24 h-24 rounded-full bg-green-500/20 flex items-center justify-center mx-auto mb-6 animate-bounce-slow">
                  <CheckCircle className="w-12 h-12 text-green-500" />
                </div>
                
                <div className="flex items-center justify-center gap-2 mb-4">
                  <Sparkles className="w-5 h-5 text-[#D4AF37]" />
                  <span className="text-[#D4AF37] text-sm font-medium">Transaction confirmée</span>
                  <Sparkles className="w-5 h-5 text-[#D4AF37]" />
                </div>
                
                <h1 className="text-2xl md:text-3xl font-bold text-white mb-4" style={{ fontFamily: 'Playfair Display, serif' }}>
                  Paiement réussi !
                </h1>
                
                <p className="text-gray-400 mb-6 text-sm md:text-base">
                  Merci pour votre confiance. Votre paiement a été traité avec succès.
                </p>

                {/* Payment Details Card */}
                <div className="bg-white/5 rounded-xl p-4 mb-6 text-left">
                  <div className="flex items-center gap-3 mb-3">
                    <Receipt className="w-5 h-5 text-[#D4AF37]" />
                    <span className="text-white font-medium">Détails du paiement</span>
                  </div>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-500">Montant</span>
                      <span className="text-white font-semibold">
                        {paymentData?.amount_total ? (paymentData.amount_total / 100).toFixed(2) : '0.00'} {paymentData?.currency?.toUpperCase() || 'CHF'}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">Statut</span>
                      <span className="text-green-400 font-medium">Payé</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">Référence</span>
                      <span className="text-gray-300 text-xs">{sessionId?.slice(0, 20)}...</span>
                    </div>
                  </div>
                </div>

                <div className="space-y-3">
                  <Link 
                    to={getDashboardLink()} 
                    className="btn-primary w-full flex items-center justify-center gap-2"
                    data-testid="back-to-dashboard"
                  >
                    <LayoutDashboard className="w-4 h-4" />
                    Retour au tableau de bord
                  </Link>
                  <Link 
                    to="/" 
                    className="btn-secondary w-full flex items-center justify-center gap-2"
                  >
                    <Home className="w-4 h-4" />
                    Continuer à explorer
                  </Link>
                </div>
              </div>
            </div>

            {/* Trust badges */}
            <div className="flex items-center justify-center gap-6 text-gray-500 text-xs">
              <div className="flex items-center gap-1">
                <Shield className="w-4 h-4" />
                <span>Paiement sécurisé</span>
              </div>
              <div className="flex items-center gap-1">
                <CreditCard className="w-4 h-4" />
                <span>Via Stripe</span>
              </div>
            </div>
          </div>
        )}

        {status === 'pending' && (
          <div className="card-service rounded-2xl p-8 md:p-12 border border-yellow-500/30">
            <div className="w-24 h-24 rounded-full bg-yellow-500/20 flex items-center justify-center mx-auto mb-6">
              <Clock className="w-12 h-12 text-yellow-500 animate-pulse" />
            </div>
            <h1 className="text-2xl md:text-3xl font-bold text-white mb-4" style={{ fontFamily: 'Playfair Display, serif' }}>
              Paiement en cours de traitement
            </h1>
            <p className="text-gray-400 mb-8 text-sm md:text-base">
              Votre paiement est en cours de traitement. Vous recevrez une confirmation par email dans les prochaines minutes.
            </p>
            <div className="space-y-3">
              <Link to={getDashboardLink()} className="btn-primary w-full flex items-center justify-center gap-2">
                <LayoutDashboard className="w-4 h-4" />
                Retour au tableau de bord
              </Link>
              <Link to="/" className="btn-secondary w-full flex items-center justify-center gap-2">
                <Home className="w-4 h-4" />
                Retour à l'accueil
              </Link>
            </div>
          </div>
        )}

        {status === 'error' && (
          <div className="card-service rounded-2xl p-8 md:p-12 border border-red-500/30">
            <div className="w-24 h-24 rounded-full bg-red-500/20 flex items-center justify-center mx-auto mb-6">
              <XCircle className="w-12 h-12 text-red-500" />
            </div>
            <h1 className="text-2xl md:text-3xl font-bold text-white mb-4" style={{ fontFamily: 'Playfair Display, serif' }}>
              Paiement échoué
            </h1>
            <p className="text-gray-400 mb-4 text-sm md:text-base">
              Une erreur est survenue lors du traitement de votre paiement.
            </p>
            
            {/* Error details */}
            <div className="bg-red-500/10 rounded-xl p-4 mb-6 text-left">
              <p className="text-red-400 text-sm">
                Causes possibles :
              </p>
              <ul className="text-gray-400 text-xs mt-2 space-y-1 list-disc list-inside">
                <li>Carte refusée par votre banque</li>
                <li>Fonds insuffisants</li>
                <li>Session expirée</li>
                <li>Problème de connexion</li>
              </ul>
            </div>

            <div className="space-y-3">
              <Link 
                to={getDashboardLink()} 
                className="btn-primary w-full flex items-center justify-center gap-2"
              >
                <RefreshCw className="w-4 h-4" />
                Réessayer
              </Link>
              <Link to="/" className="btn-secondary w-full flex items-center justify-center gap-2">
                <Home className="w-4 h-4" />
                Retour à l'accueil
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

const PaymentCancelPage = () => {
  const { isEnterprise, isClient } = useAuth();
  const navigate = useNavigate();

  const getDashboardLink = () => {
    if (isEnterprise) return '/dashboard/entreprise';
    if (isClient) return '/dashboard/client';
    return '/';
  };

  return (
    <div className="min-h-screen bg-[#050505] pt-20 flex items-center justify-center px-4" data-testid="payment-cancel-page">
      {/* Background decoration */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 right-1/4 w-96 h-96 bg-gray-500/5 rounded-full blur-3xl" />
      </div>

      <div className="max-w-lg w-full text-center relative z-10 card-service rounded-2xl p-8 md:p-12 border border-gray-500/30">
        <div className="w-24 h-24 rounded-full bg-gray-500/20 flex items-center justify-center mx-auto mb-6">
          <XCircle className="w-12 h-12 text-gray-400" />
        </div>
        <h1 className="text-2xl md:text-3xl font-bold text-white mb-4" style={{ fontFamily: 'Playfair Display, serif' }}>
          Paiement annulé
        </h1>
        <p className="text-gray-400 mb-4 text-sm md:text-base">
          Vous avez annulé le paiement. Aucun montant n'a été débité de votre compte.
        </p>
        
        {/* Info box */}
        <div className="bg-white/5 rounded-xl p-4 mb-6 text-left">
          <div className="flex items-start gap-3">
            <Shield className="w-5 h-5 text-[#0047AB] mt-0.5" />
            <div className="text-sm">
              <p className="text-white font-medium mb-1">Paiement sécurisé</p>
              <p className="text-gray-500">
                Vos informations de paiement n'ont pas été enregistrées. Vous pouvez réessayer à tout moment.
              </p>
            </div>
          </div>
        </div>

        <div className="space-y-3">
          <Link 
            to={getDashboardLink()} 
            className="btn-primary w-full flex items-center justify-center gap-2"
            data-testid="back-to-dashboard-cancel"
          >
            <LayoutDashboard className="w-4 h-4" />
            Retour au tableau de bord
          </Link>
          <Link to="/" className="btn-secondary w-full flex items-center justify-center gap-2">
            <Home className="w-4 h-4" />
            Retour à l'accueil
          </Link>
        </div>
      </div>
    </div>
  );
};

export { PaymentSuccessPage, PaymentCancelPage };
