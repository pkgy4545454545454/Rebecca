import React from 'react';
import { Link } from 'react-router-dom';
import { 
  FileText, 
  CreditCard, 
  Shield, 
  Clock, 
  RefreshCw,
  AlertCircle,
  CheckCircle,
  Mail,
  Phone,
  MapPin
} from 'lucide-react';

const CGVPage = () => {
  return (
    <div className="min-h-screen bg-[#050505] pt-24 px-4">
      <div className="max-w-4xl mx-auto py-16">
        <div className="flex items-center gap-4 mb-8">
          <FileText className="w-12 h-12 text-yellow-400" />
          <h1 className="text-4xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
            Conditions Générales de Vente
          </h1>
        </div>

        <p className="text-gray-400 mb-12 text-lg">
          Dernière mise à jour : Février 2026
        </p>

        <div className="space-y-12 text-gray-400">
          {/* Article 1 */}
          <section>
            <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-3">
              <span className="w-8 h-8 rounded-full bg-yellow-500 text-black flex items-center justify-center text-sm font-bold">1</span>
              Objet
            </h2>
            <div className="pl-11">
              <p className="mb-4 leading-relaxed">
                Les présentes conditions générales de vente (CGV) régissent l'utilisation de la plateforme Titelli, 
                les relations entre Titelli SA et ses utilisateurs (clients et prestataires), ainsi que les conditions 
                d'accès aux différents services proposés.
              </p>
              <p className="leading-relaxed">
                En utilisant la plateforme Titelli, vous acceptez sans réserve les présentes CGV.
              </p>
            </div>
          </section>

          {/* Article 2 - Procédé de facturation */}
          <section className="bg-gray-800/30 rounded-2xl p-6 border border-gray-700">
            <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-3">
              <span className="w-8 h-8 rounded-full bg-yellow-500 text-black flex items-center justify-center text-sm font-bold">2</span>
              Procédé de facturation
            </h2>
            <div className="pl-11 space-y-4">
              <div className="flex items-start gap-3">
                <CreditCard className="w-5 h-5 text-yellow-400 mt-1 flex-shrink-0" />
                <p className="leading-relaxed">
                  <strong className="text-white">Titelli vous verse chaque début du mois</strong> les revenus de vos ventes du mois précédent, 
                  déduisant <strong className="text-yellow-400">20%</strong> (cash-back + frais Titelli).
                </p>
              </div>
              
              <div className="flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-orange-400 mt-1 flex-shrink-0" />
                <p className="leading-relaxed">
                  Les ventes livrées retiennent des frais de livraison supplémentaires.
                </p>
              </div>
              
              <div className="bg-green-900/30 border border-green-700/50 rounded-xl p-4 mt-4">
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-green-400 mt-1 flex-shrink-0" />
                  <p className="text-green-200/90 leading-relaxed">
                    En dépit des frais, il est attendu d'obtenir une <strong className="text-white">augmentation de 20 à 45%</strong> de vos bénéfices 
                    la première année sous réserve de bonne gestion de vos opportunités business Titelli.
                  </p>
                </div>
              </div>
            </div>
          </section>

          {/* Article 3 - Tarification */}
          <section>
            <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-3">
              <span className="w-8 h-8 rounded-full bg-yellow-500 text-black flex items-center justify-center text-sm font-bold">3</span>
              Tarification des services
            </h2>
            <div className="pl-11">
              <div className="grid md:grid-cols-2 gap-4">
                <div className="bg-gray-800/50 rounded-xl p-4 border border-gray-700">
                  <h3 className="font-bold text-white mb-3">Inscription</h3>
                  <ul className="space-y-2">
                    <li className="flex justify-between">
                      <span>Inscription annuelle</span>
                      <span className="text-yellow-400 font-bold">250 CHF</span>
                    </li>
                  </ul>
                </div>
                
                <div className="bg-gray-800/50 rounded-xl p-4 border border-gray-700">
                  <h3 className="font-bold text-white mb-3">Service Premium</h3>
                  <ul className="space-y-2">
                    <li className="flex justify-between">
                      <span>Annuel</span>
                      <span className="text-yellow-400 font-bold">540 CHF</span>
                    </li>
                    <li className="flex justify-between">
                      <span>Mensuel</span>
                      <span className="text-yellow-400 font-bold">45 CHF</span>
                    </li>
                  </ul>
                </div>
                
                <div className="bg-gray-800/50 rounded-xl p-4 border border-gray-700">
                  <h3 className="font-bold text-white mb-3">Commissions</h3>
                  <ul className="space-y-2">
                    <li className="flex justify-between">
                      <span>Commission sur ventes</span>
                      <span className="text-yellow-400 font-bold">10-20%</span>
                    </li>
                  </ul>
                </div>
                
                <div className="bg-gray-800/50 rounded-xl p-4 border border-gray-700">
                  <h3 className="font-bold text-white mb-3">Services à la carte</h3>
                  <ul className="space-y-2">
                    <li className="flex justify-between">
                      <span>Pub Média</span>
                      <span className="text-yellow-400 font-bold">29.90+ CHF</span>
                    </li>
                    <li className="flex justify-between">
                      <span>Sur Mesure</span>
                      <span className="text-yellow-400 font-bold">149.90 CHF</span>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </section>

          {/* Article 4 - Renouvellement */}
          <section className="bg-yellow-900/20 rounded-2xl p-6 border border-yellow-700/30">
            <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-3">
              <RefreshCw className="w-8 h-8 text-yellow-400" />
              Renouvellement
            </h2>
            <p className="leading-relaxed text-lg">
              Renouvellement de la prestation chaque année sous réserve d'un <strong className="text-white">courrier écrit 
              dans le mois qui précède le renouvellement</strong>.
            </p>
          </section>

          {/* Article 5 - Non-souscription */}
          <section>
            <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-3">
              <span className="w-8 h-8 rounded-full bg-yellow-500 text-black flex items-center justify-center text-sm font-bold">5</span>
              Non-souscription
            </h2>
            <div className="pl-11">
              <p className="leading-relaxed">
                Si vous ne souhaitez pas souscrire aux services Titelli, et que vous ne souhaitez pas être exposé à titre indicatif, 
                il vous est possible d'adresser un mail au service client concerné.
              </p>
            </div>
          </section>

          {/* Article 6 - Paiements */}
          <section>
            <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-3">
              <span className="w-8 h-8 rounded-full bg-yellow-500 text-black flex items-center justify-center text-sm font-bold">6</span>
              Paiements
            </h2>
            <div className="pl-11 space-y-4">
              <p className="leading-relaxed">
                Tous les paiements sont sécurisés via <strong className="text-white">Stripe</strong>. Les prix sont exprimés en CHF (Francs suisses).
              </p>
              <div className="flex items-center gap-2">
                <Shield className="w-5 h-5 text-green-400" />
                <span className="text-green-400">Paiements 100% sécurisés</span>
              </div>
            </div>
          </section>

          {/* Article 7 - Litiges */}
          <section>
            <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-3">
              <span className="w-8 h-8 rounded-full bg-yellow-500 text-black flex items-center justify-center text-sm font-bold">7</span>
              Litiges et droit applicable
            </h2>
            <div className="pl-11">
              <p className="leading-relaxed">
                Les présentes CGV sont soumises au droit suisse. Tout litige relatif à l'interprétation ou à l'exécution 
                des présentes CGV sera de la compétence exclusive des tribunaux de Lausanne, Suisse.
              </p>
            </div>
          </section>

          {/* Contact */}
          <section className="bg-gray-800/50 rounded-2xl p-6 border border-gray-700">
            <h2 className="text-xl font-bold text-white mb-4">Contact</h2>
            <div className="space-y-3">
              <div className="flex items-center gap-3">
                <Mail className="w-5 h-5 text-yellow-400" />
                <span>contact@titelli.com</span>
              </div>
              <div className="flex items-center gap-3">
                <MapPin className="w-5 h-5 text-yellow-400" />
                <span>Lausanne, Suisse</span>
              </div>
            </div>
          </section>
        </div>

        {/* Footer links */}
        <div className="mt-16 pt-8 border-t border-gray-800 flex flex-wrap gap-6 text-sm text-gray-500">
          <Link to="/mentions-legales" className="hover:text-yellow-400 transition-colors">Mentions Légales</Link>
          <Link to="/about" className="hover:text-yellow-400 transition-colors">À Propos</Link>
          <Link to="/partenaires" className="hover:text-yellow-400 transition-colors">Nos Partenaires</Link>
        </div>
      </div>
    </div>
  );
};

export default CGVPage;
