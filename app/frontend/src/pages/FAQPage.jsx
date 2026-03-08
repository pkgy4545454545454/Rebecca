import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Search, HelpCircle, MessageCircle, Mail, Phone } from 'lucide-react';

const FAQPage = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [openItems, setOpenItems] = useState({});

  const faqCategories = [
    {
      title: "Général",
      icon: "🏠",
      questions: [
        {
          q: "Qu'est-ce que Titelli ?",
          a: "Titelli est une plateforme suisse de mise en relation entre prestataires de services et clients. Nous connectons les entreprises locales avec leurs futurs clients, tout en offrant un système de cashback unique et des outils marketing avancés."
        },
        {
          q: "Comment fonctionne Titelli ?",
          a: "Les entreprises créent leur profil, ajoutent leurs services/produits, et les clients peuvent les découvrir, réserver et payer directement sur la plateforme. Les clients bénéficient de cashback sur leurs achats, et les entreprises d'outils de gestion et marketing."
        },
        {
          q: "Titelli est-il disponible partout en Suisse ?",
          a: "Actuellement, Titelli se concentre sur la région de Lausanne et la Suisse romande. Nous prévoyons une expansion progressive vers d'autres régions suisses."
        },
        {
          q: "Comment contacter le support ?",
          a: "Vous pouvez nous contacter par email à support@titelli.com, via le chat en ligne disponible sur le site, ou par téléphone au +41 XX XXX XX XX (lun-ven 9h-18h)."
        }
      ]
    },
    {
      title: "Compte & Inscription",
      icon: "👤",
      questions: [
        {
          q: "Comment créer un compte ?",
          a: "Cliquez sur 'Connexion' en haut à droite, puis 'S'inscrire'. Choisissez votre type de compte (Client ou Entreprise), remplissez vos informations et validez. Vous recevrez un email de confirmation."
        },
        {
          q: "Quelle est la différence entre un compte Client et Entreprise ?",
          a: "Un compte Client permet d'acheter des services, bénéficier de cashback et gérer ses commandes. Un compte Entreprise permet de vendre des services/produits, gérer son catalogue, accéder aux outils marketing et recevoir des paiements."
        },
        {
          q: "Comment modifier mes informations personnelles ?",
          a: "Connectez-vous à votre compte, accédez à votre Dashboard, puis cliquez sur 'Profil'. Vous pourrez y modifier toutes vos informations : nom, email, photo, adresse, etc."
        },
        {
          q: "J'ai oublié mon mot de passe, que faire ?",
          a: "Sur la page de connexion, cliquez sur 'Mot de passe oublié'. Entrez votre email et vous recevrez un lien pour réinitialiser votre mot de passe."
        },
        {
          q: "Comment supprimer mon compte ?",
          a: "Accédez à votre Dashboard > Paramètres > Supprimer mon compte. Cette action est irréversible. Vos données seront supprimées conformément à notre politique de confidentialité."
        }
      ]
    },
    {
      title: "Cashback & Avantages",
      icon: "💰",
      questions: [
        {
          q: "Comment fonctionne le cashback ?",
          a: "À chaque achat effectué sur Titelli, vous recevez automatiquement un pourcentage du montant en cashback. Ce montant est crédité sur votre compte et peut être utilisé pour vos prochains achats ou retiré vers votre compte bancaire (minimum 50 CHF)."
        },
        {
          q: "Quel est le taux de cashback ?",
          a: "Le taux dépend de votre abonnement : Gratuit (1%), Premium (10%), VIP (15%). Plus votre abonnement est élevé, plus vous gagnez de cashback sur vos achats."
        },
        {
          q: "Comment utiliser mon cashback ?",
          a: "Lors du paiement, vous pouvez choisir d'utiliser tout ou partie de votre solde cashback. Le montant sera automatiquement déduit de votre commande."
        },
        {
          q: "Comment retirer mon cashback ?",
          a: "Dans votre Dashboard > Cashback, ajoutez votre IBAN, puis cliquez sur 'Retirer'. Le montant minimum est de 50 CHF. Le virement est effectué sous 3-5 jours ouvrés."
        },
        {
          q: "Le cashback expire-t-il ?",
          a: "Non, votre cashback n'expire jamais tant que votre compte est actif. En cas de fermeture de compte, le cashback non retiré sera perdu."
        }
      ]
    },
    {
      title: "Commandes & Paiements",
      icon: "🛒",
      questions: [
        {
          q: "Quels moyens de paiement sont acceptés ?",
          a: "Nous acceptons les cartes bancaires (Visa, Mastercard, American Express), Apple Pay, Google Pay et TWINT. Tous les paiements sont sécurisés via Stripe."
        },
        {
          q: "Comment suivre ma commande ?",
          a: "Accédez à votre Dashboard > Mes commandes. Vous y trouverez l'historique complet avec le statut de chaque commande. Vous recevez également des notifications par email à chaque changement de statut."
        },
        {
          q: "Comment annuler une commande ?",
          a: "Les conditions d'annulation dépendent du prestataire. Généralement, vous pouvez annuler gratuitement jusqu'à 24h avant le rendez-vous. Consultez les conditions spécifiques de chaque service."
        },
        {
          q: "Comment obtenir une facture ?",
          a: "Toutes vos factures sont disponibles dans Dashboard > Mes commandes. Cliquez sur une commande puis 'Télécharger la facture' pour obtenir le PDF."
        },
        {
          q: "Que faire en cas de problème avec une commande ?",
          a: "Contactez d'abord le prestataire via la messagerie intégrée. Si le problème persiste, contactez notre support qui interviendra pour trouver une solution."
        }
      ]
    },
    {
      title: "Pour les Entreprises",
      icon: "🏢",
      questions: [
        {
          q: "Comment inscrire mon entreprise ?",
          a: "Créez un compte 'Entreprise', complétez votre profil avec vos informations, ajoutez vos services/produits, et vous êtes prêt à recevoir des clients ! Nous validons les inscriptions sous 24-48h."
        },
        {
          q: "Quels sont les frais pour les entreprises ?",
          a: "Titelli prélève une commission sur chaque vente (8% à 15% selon votre abonnement). Il n'y a pas de frais fixes obligatoires. Des abonnements optionnels (29-149 CHF/mois) réduisent la commission et offrent des avantages."
        },
        {
          q: "Comment recevoir mes paiements ?",
          a: "Les paiements sont automatiquement crédités sur votre solde Titelli après chaque vente. Vous pouvez demander un virement vers votre compte bancaire à tout moment (minimum 50 CHF, délai 3-5 jours)."
        },
        {
          q: "Comment créer une publicité ?",
          a: "Accédez à Dashboard > Mes publicités ou utilisez notre outil 'Pub Média IA' pour créer des visuels professionnels générés par intelligence artificielle. Vous pouvez tester gratuitement avant de payer."
        },
        {
          q: "Comment gérer mon équipe ?",
          a: "Dans Dashboard > Mon personnel, vous pouvez ajouter des collaborateurs, leur attribuer des rôles et permissions, et gérer leurs accès à votre compte entreprise."
        }
      ]
    },
    {
      title: "Publicité IA",
      icon: "🎨",
      questions: [
        {
          q: "Comment fonctionne la Pub Média IA ?",
          a: "Notre outil utilise l'intelligence artificielle (DALL-E, Sora) pour générer des images et vidéos publicitaires professionnelles. Vous choisissez un template, personnalisez le texte, et l'IA crée le visuel."
        },
        {
          q: "Puis-je tester avant de payer ?",
          a: "Oui ! Vous pouvez voir un aperçu de votre création avant de payer. Utilisez le code BIENVENUE100 pour obtenir 100 CHF de crédit pub gratuit."
        },
        {
          q: "Combien coûte une publicité IA ?",
          a: "Les images coûtent entre 29.90 et 69.90 CHF selon le template. Les vidéos entre 129.90 et 399.90 CHF. Une création sur mesure est disponible à 149.90 CHF."
        },
        {
          q: "Combien de temps pour recevoir ma création ?",
          a: "Les images sont générées en quelques minutes. Les vidéos peuvent prendre jusqu'à 1 heure selon la complexité. Vous recevez une notification quand c'est prêt."
        }
      ]
    },
    {
      title: "Sécurité & Confidentialité",
      icon: "🔒",
      questions: [
        {
          q: "Mes données sont-elles sécurisées ?",
          a: "Oui, nous utilisons le chiffrement SSL/TLS pour toutes les communications. Les paiements sont sécurisés par Stripe (certifié PCI DSS). Vos données sont stockées sur des serveurs sécurisés en Europe."
        },
        {
          q: "Comment Titelli utilise mes données ?",
          a: "Vos données sont utilisées uniquement pour fournir nos services, améliorer votre expérience et vous envoyer des communications pertinentes (si vous avez accepté). Consultez notre Politique de Confidentialité pour plus de détails."
        },
        {
          q: "Puis-je exporter mes données ?",
          a: "Oui, conformément au RGPD, vous pouvez demander une copie de vos données. Accédez à Dashboard > Paramètres > Exporter mes données."
        },
        {
          q: "Comment signaler un problème de sécurité ?",
          a: "Si vous détectez une faille de sécurité, contactez immédiatement security@titelli.com. Nous prenons très au sérieux toute question de sécurité."
        }
      ]
    }
  ];

  const toggleItem = (categoryIndex, questionIndex) => {
    const key = `${categoryIndex}-${questionIndex}`;
    setOpenItems(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  const filteredCategories = faqCategories.map(category => ({
    ...category,
    questions: category.questions.filter(
      item => 
        item.q.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.a.toLowerCase().includes(searchQuery.toLowerCase())
    )
  })).filter(category => category.questions.length > 0);

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-white">
      {/* Hero Section */}
      <div className="relative py-20 px-4 bg-gradient-to-b from-blue-600/20 to-transparent">
        <div className="max-w-4xl mx-auto text-center">
          <HelpCircle className="w-16 h-16 text-blue-400 mx-auto mb-6" />
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            Centre d'aide
          </h1>
          <p className="text-xl text-gray-400 mb-8">
            Trouvez rapidement les réponses à vos questions
          </p>
          
          {/* Search Bar */}
          <div className="relative max-w-xl mx-auto">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Rechercher une question..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-12 pr-4 py-4 bg-white/10 border border-white/20 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:border-blue-500 transition-colors"
            />
          </div>
        </div>
      </div>

      {/* FAQ Content */}
      <div className="max-w-4xl mx-auto px-4 pb-20">
        {filteredCategories.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-400 text-lg">Aucun résultat trouvé pour "{searchQuery}"</p>
            <button 
              onClick={() => setSearchQuery('')}
              className="mt-4 text-blue-400 hover:text-blue-300"
            >
              Effacer la recherche
            </button>
          </div>
        ) : (
          filteredCategories.map((category, categoryIndex) => (
            <div key={categoryIndex} className="mb-8">
              <h2 className="text-2xl font-bold mb-4 flex items-center gap-3">
                <span className="text-3xl">{category.icon}</span>
                {category.title}
              </h2>
              
              <div className="space-y-3">
                {category.questions.map((item, questionIndex) => {
                  const isOpen = openItems[`${categoryIndex}-${questionIndex}`];
                  return (
                    <div 
                      key={questionIndex}
                      className="bg-white/5 border border-white/10 rounded-xl overflow-hidden"
                    >
                      <button
                        onClick={() => toggleItem(categoryIndex, questionIndex)}
                        className="w-full px-6 py-4 flex items-center justify-between text-left hover:bg-white/5 transition-colors"
                      >
                        <span className="font-medium pr-4">{item.q}</span>
                        {isOpen ? (
                          <ChevronUp className="w-5 h-5 text-blue-400 flex-shrink-0" />
                        ) : (
                          <ChevronDown className="w-5 h-5 text-gray-400 flex-shrink-0" />
                        )}
                      </button>
                      
                      {isOpen && (
                        <div className="px-6 pb-4">
                          <div className="pt-2 border-t border-white/10">
                            <p className="text-gray-300 leading-relaxed mt-3">
                              {item.a}
                            </p>
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          ))
        )}

        {/* Contact Section */}
        <div className="mt-16 bg-gradient-to-r from-blue-600/20 to-purple-600/20 rounded-2xl p-8 border border-white/10">
          <h2 className="text-2xl font-bold mb-4 text-center">
            Vous n'avez pas trouvé votre réponse ?
          </h2>
          <p className="text-gray-400 text-center mb-8">
            Notre équipe est là pour vous aider
          </p>
          
          <div className="grid md:grid-cols-3 gap-4">
            <a 
              href="mailto:support@titelli.com"
              className="flex items-center justify-center gap-3 bg-white/10 hover:bg-white/20 rounded-xl p-4 transition-colors"
            >
              <Mail className="w-5 h-5 text-blue-400" />
              <span>support@titelli.com</span>
            </a>
            <a 
              href="tel:+41000000000"
              className="flex items-center justify-center gap-3 bg-white/10 hover:bg-white/20 rounded-xl p-4 transition-colors"
            >
              <Phone className="w-5 h-5 text-green-400" />
              <span>+41 XX XXX XX XX</span>
            </a>
            <button 
              className="flex items-center justify-center gap-3 bg-blue-600 hover:bg-blue-500 rounded-xl p-4 transition-colors"
            >
              <MessageCircle className="w-5 h-5" />
              <span>Chat en direct</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FAQPage;
