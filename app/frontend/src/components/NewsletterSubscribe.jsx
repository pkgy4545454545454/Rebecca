import React, { useState } from 'react';
import { Mail, Check, Loader2, Sparkles } from 'lucide-react';
import API from '../services/api';

const NewsletterSubscribe = ({ variant = 'default' }) => {
  const [email, setEmail] = useState('');
  const [firstName, setFirstName] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      await API.post('/api/newsletter/subscribe', {
        email,
        first_name: firstName || null,
        preferences: ['promotions', 'news', 'tips']
      });
      setIsSuccess(true);
      setEmail('');
      setFirstName('');
    } catch (err) {
      setError(err.response?.data?.detail || 'Une erreur est survenue');
    } finally {
      setIsLoading(false);
    }
  };

  if (isSuccess) {
    return (
      <div className={`${variant === 'footer' ? '' : 'bg-gradient-to-r from-green-500/20 to-emerald-500/20 rounded-xl p-6 border border-green-500/30'}`}>
        <div className="flex items-center justify-center gap-3 text-green-400">
          <Check className="w-6 h-6" />
          <span className="font-medium">Merci pour votre inscription !</span>
        </div>
        <p className="text-gray-400 text-sm text-center mt-2">
          Vous recevrez bientôt nos dernières actualités et offres exclusives.
        </p>
      </div>
    );
  }

  if (variant === 'footer') {
    return (
      <form onSubmit={handleSubmit} className="space-y-3">
        <div className="flex gap-2">
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Votre email"
            required
            className="flex-1 px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500 text-sm"
          />
          <button
            type="submit"
            disabled={isLoading}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg transition-colors disabled:opacity-50"
          >
            {isLoading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Mail className="w-4 h-4" />
            )}
          </button>
        </div>
        {error && <p className="text-red-400 text-xs">{error}</p>}
      </form>
    );
  }

  return (
    <div className="bg-gradient-to-r from-blue-600/20 to-purple-600/20 rounded-2xl p-8 border border-white/10">
      <div className="text-center mb-6">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-500/20 rounded-full mb-4">
          <Sparkles className="w-8 h-8 text-blue-400" />
        </div>
        <h3 className="text-2xl font-bold text-white mb-2">
          Restez informé
        </h3>
        <p className="text-gray-400">
          Recevez nos offres exclusives, actualités et conseils directement dans votre boîte mail.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4 max-w-md mx-auto">
        <div className="grid grid-cols-2 gap-3">
          <input
            type="text"
            value={firstName}
            onChange={(e) => setFirstName(e.target.value)}
            placeholder="Prénom (optionnel)"
            className="px-4 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
          />
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Votre email *"
            required
            className="px-4 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
          />
        </div>
        
        <button
          type="submit"
          disabled={isLoading}
          className="w-full py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 rounded-xl text-white font-medium transition-all disabled:opacity-50 flex items-center justify-center gap-2"
        >
          {isLoading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Inscription...
            </>
          ) : (
            <>
              <Mail className="w-5 h-5" />
              S'inscrire à la newsletter
            </>
          )}
        </button>

        {error && (
          <p className="text-red-400 text-sm text-center">{error}</p>
        )}

        <p className="text-gray-500 text-xs text-center">
          En vous inscrivant, vous acceptez de recevoir nos communications. 
          Désabonnement possible à tout moment.
        </p>
      </form>
    </div>
  );
};

export default NewsletterSubscribe;
