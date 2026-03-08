import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Package, Clock, CheckCircle, XCircle, ChevronRight, Building2, Calendar } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { orderAPI } from '../services/api';

const OrdersPage = () => {
  const { isAuthenticated } = useAuth();
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchOrders = async () => {
      if (!isAuthenticated) {
        setLoading(false);
        return;
      }

      try {
        const response = await orderAPI.list();
        setOrders(response.data);
      } catch (error) {
        console.error('Error fetching orders:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchOrders();
  }, [isAuthenticated]);

  const getStatusBadge = (status) => {
    switch (status) {
      case 'pending':
        return (
          <span className="flex items-center gap-1 px-3 py-1 bg-yellow-500/20 text-yellow-500 rounded-full text-sm">
            <Clock className="w-4 h-4" />
            En attente
          </span>
        );
      case 'confirmed':
        return (
          <span className="flex items-center gap-1 px-3 py-1 bg-blue-500/20 text-blue-500 rounded-full text-sm">
            <CheckCircle className="w-4 h-4" />
            Confirmée
          </span>
        );
      case 'completed':
        return (
          <span className="flex items-center gap-1 px-3 py-1 bg-green-500/20 text-green-500 rounded-full text-sm">
            <CheckCircle className="w-4 h-4" />
            Terminée
          </span>
        );
      case 'cancelled':
        return (
          <span className="flex items-center gap-1 px-3 py-1 bg-red-500/20 text-red-500 rounded-full text-sm">
            <XCircle className="w-4 h-4" />
            Annulée
          </span>
        );
      default:
        return (
          <span className="px-3 py-1 bg-gray-500/20 text-gray-500 rounded-full text-sm">
            {status}
          </span>
        );
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: 'long',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-[#050505] pt-24 px-4" data-testid="orders-page">
        <div className="max-w-4xl mx-auto py-16 text-center">
          <h1 className="text-3xl font-bold text-white mb-4" style={{ fontFamily: 'Playfair Display, serif' }}>
            Connectez-vous
          </h1>
          <p className="text-gray-400 mb-8">
            Vous devez être connecté pour voir vos commandes
          </p>
          <Link to="/auth" className="btn-primary">
            Se connecter
          </Link>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-[#050505] pt-24 flex items-center justify-center">
        <div className="w-16 h-16 border-4 border-[#0047AB] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#050505] pt-24 px-4" data-testid="orders-page">
      <div className="max-w-4xl mx-auto py-8">
        <h1 className="text-3xl font-bold text-white mb-8" style={{ fontFamily: 'Playfair Display, serif' }}>
          Mes Commandes
        </h1>

        {orders.length === 0 ? (
          <div className="text-center py-16">
            <div className="w-24 h-24 bg-white/5 rounded-full flex items-center justify-center mx-auto mb-6">
              <Package className="w-12 h-12 text-gray-500" />
            </div>
            <h2 className="text-xl font-semibold text-white mb-2">Aucune commande</h2>
            <p className="text-gray-400 mb-8">
              Vous n'avez pas encore passé de commande
            </p>
            <Link to="/services" className="btn-primary">
              Découvrir les services
            </Link>
          </div>
        ) : (
          <div className="space-y-4">
            {orders.map((order) => (
              <div key={order.id} className="card-service rounded-xl p-6" data-testid={`order-${order.id}`}>
                {/* Header */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4 pb-4 border-b border-white/10">
                  <div>
                    <div className="flex items-center gap-3 mb-1">
                      <span className="text-sm text-gray-400">Commande</span>
                      <span className="font-mono text-white">#{order.id.slice(0, 8)}</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm text-gray-400">
                      <Calendar className="w-4 h-4" />
                      {formatDate(order.created_at)}
                    </div>
                  </div>
                  {getStatusBadge(order.status)}
                </div>

                {/* Items */}
                <div className="space-y-3 mb-4">
                  {order.items.map((item, index) => (
                    <div key={index} className="flex justify-between items-center p-3 bg-white/5 rounded-lg">
                      <div>
                        <p className="text-white font-medium">{item.name}</p>
                        <p className="text-sm text-gray-400">Quantité: {item.quantity}</p>
                      </div>
                      <p className="text-white font-semibold">
                        {(item.price * item.quantity).toFixed(2)} CHF
                      </p>
                    </div>
                  ))}
                </div>

                {/* Footer */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-4 border-t border-white/10">
                  <Link 
                    to={`/entreprise/${order.enterprise_id}`}
                    className="flex items-center gap-2 text-[#0047AB] hover:text-[#2E74D6] transition-colors"
                  >
                    <Building2 className="w-4 h-4" />
                    Voir l'entreprise
                    <ChevronRight className="w-4 h-4" />
                  </Link>
                  <div className="text-right">
                    <p className="text-sm text-gray-400">Total</p>
                    <p className="text-2xl font-bold text-[#D4AF37]">{order.total.toFixed(2)} CHF</p>
                  </div>
                </div>

                {/* Notes */}
                {order.notes && (
                  <div className="mt-4 p-3 bg-white/5 rounded-lg">
                    <p className="text-sm text-gray-400">Notes:</p>
                    <p className="text-white">{order.notes}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default OrdersPage;
