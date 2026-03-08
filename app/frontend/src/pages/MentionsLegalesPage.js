import React from 'react';
import { Link } from 'react-router-dom';
import { 
  Shield, 
  Building2, 
  Server, 
  Lock, 
  Eye,
  FileText,
  Mail,
  MapPin,
  Globe,
  Users,
  Database,
  Trash2,
  RefreshCw
} from 'lucide-react';

const MentionsLegalesPage = () => {
  return (
    <div className="min-h-screen bg-[#050505] pt-24 px-4">
      <div className="max-w-4xl mx-auto py-16">
        <div className="flex items-center gap-4 mb-8">
          <Shield className="w-12 h-12 text-yellow-400" />
          <h1 className="text-4xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
            Mentions Légales
          </h1>
        </div>

        <p className="text-gray-400 mb-12 text-lg">
          Dernière mise à jour : Février 2026
        </p>

        <div className="space-y-12 text-gray-400">
          {/* Éditeur */}
          <section className="bg-gray-800/30 rounded-2xl p-6 border border-gray-700">
            <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-3">
              <Building2 className="w-8 h-8 text-yellow-400" />
              Éditeur du site
            </h2>
            <div className="space-y-3 pl-2">
              <p><strong className="text-white">Raison sociale :</strong> Titelli SA</p>
              <p><strong className="text-white">Forme juridique :</strong> Société Anonyme de droit suisse</p>
              <p><strong className="text-white">Siège social :</strong> Lausanne, Suisse</p>
              <p><strong className="text-white">Capital social :</strong> CHF 100'000.-</p>
              <p><strong className="text-white">Numéro IDE :</strong> CHE-XXX.XXX.XXX</p>
              <p><strong className="text-white">Email :</strong> contact@titelli.com</p>
            </div>
          </section>

          {/* Directeur de publication */}
          <section>
            <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-3">
              <Users className="w-8 h-8 text-yellow-400" />
              Direction de la publication
            </h2>
            <p className="pl-2">
              Le directeur de la publication est le représentant légal de Titelli SA.
            </p>
          </section>

          {/* Hébergement */}
          <section>
            <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-3">
              <Server className="w-8 h-8 text-yellow-400" />
              Hébergement
            </h2>
            <div className="pl-2 space-y-2">
              <p>Les données sont hébergées de manière sécurisée sur des serveurs conformes aux normes suisses et européennes.</p>
              <div className="flex items-center gap-2 mt-4">
                <Lock className="w-5 h-5 text-green-400" />
                <span className="text-green-400">Hébergement sécurisé en Suisse</span>
              </div>
            </div>
          </section>

          {/* Protection des données */}
          <section className="bg-gradient-to-r from-green-900/20 to-blue-900/20 rounded-2xl p-6 border border-green-700/30">
            <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-3">
              <Database className="w-8 h-8 text-green-400" />
              Protection des données personnelles
            </h2>
            
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-bold text-white mb-2">Conformité légale</h3>
                <p className="leading-relaxed">
                  Conformément à la <strong className="text-white">Loi fédérale sur la protection des données (LPD)</strong> suisse 
                  et au <strong className="text-white">Règlement Général sur la Protection des Données (RGPD)</strong> européen, 
                  vos données personnelles sont protégées.
                </p>
              </div>

              <div>
                <h3 className="text-lg font-bold text-white mb-2">Données collectées</h3>
                <ul className="space-y-2 pl-4">
                  <li className="flex items-start gap-2">
                    <span className="text-yellow-400">•</span>
                    Données d'identification (nom, prénom, email)
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-yellow-400">•</span>
                    Données de connexion (adresse IP, logs)
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-yellow-400">•</span>
                    Données de transaction (commandes, paiements)
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-yellow-400">•</span>
                    Données professionnelles pour les prestataires
                  </li>
                </ul>
              </div>

              <div>
                <h3 className="text-lg font-bold text-white mb-2">Vos droits</h3>
                <div className="grid md:grid-cols-2 gap-4">
                  <div className="flex items-center gap-3 bg-black/20 rounded-lg p-3">
                    <Eye className="w-5 h-5 text-blue-400" />
                    <span>Droit d'accès</span>
                  </div>
                  <div className="flex items-center gap-3 bg-black/20 rounded-lg p-3">
                    <RefreshCw className="w-5 h-5 text-blue-400" />
                    <span>Droit de rectification</span>
                  </div>
                  <div className="flex items-center gap-3 bg-black/20 rounded-lg p-3">
                    <Trash2 className="w-5 h-5 text-blue-400" />
                    <span>Droit à l'effacement</span>
                  </div>
                  <div className="flex items-center gap-3 bg-black/20 rounded-lg p-3">
                    <Lock className="w-5 h-5 text-blue-400" />
                    <span>Droit à la portabilité</span>
                  </div>
                </div>
              </div>
            </div>
          </section>

          {/* Cookies */}
          <section>
            <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-3">
              <Globe className="w-8 h-8 text-yellow-400" />
              Cookies
            </h2>
            <div className="pl-2 space-y-4">
              <p className="leading-relaxed">
                Le site Titelli utilise des cookies pour améliorer l'expérience utilisateur, analyser le trafic 
                et personnaliser les contenus. En continuant à naviguer sur le site, vous acceptez l'utilisation des cookies.
              </p>
              <div className="bg-gray-800/50 rounded-xl p-4 border border-gray-700">
                <h4 className="font-bold text-white mb-2">Types de cookies utilisés :</h4>
                <ul className="space-y-1 text-sm">
                  <li>• <strong className="text-white">Cookies essentiels</strong> : nécessaires au fonctionnement du site</li>
                  <li>• <strong className="text-white">Cookies analytiques</strong> : pour comprendre l'utilisation du site</li>
                  <li>• <strong className="text-white">Cookies de préférence</strong> : pour mémoriser vos choix</li>
                </ul>
              </div>
            </div>
          </section>

          {/* Propriété intellectuelle */}
          <section>
            <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-3">
              <FileText className="w-8 h-8 text-yellow-400" />
              Propriété intellectuelle
            </h2>
            <div className="pl-2 space-y-4">
              <p className="leading-relaxed">
                L'ensemble des éléments constituant le site Titelli (textes, graphismes, logiciels, photographies, 
                images, sons, plans, logos, marques, etc.) sont la propriété exclusive de Titelli SA ou de ses partenaires.
              </p>
              <p className="leading-relaxed">
                Toute reproduction, représentation, modification, publication ou adaptation de tout ou partie des éléments 
                du site, quel que soit le moyen ou le procédé utilisé, est interdite sans autorisation préalable écrite.
              </p>
            </div>
          </section>

          {/* Limitation de responsabilité */}
          <section className="bg-orange-900/20 rounded-2xl p-6 border border-orange-700/30">
            <h2 className="text-2xl font-bold text-white mb-4">Limitation de responsabilité</h2>
            <p className="leading-relaxed">
              Titelli SA s'efforce d'assurer au mieux de ses possibilités l'exactitude et la mise à jour des informations 
              diffusées sur ce site. Toutefois, Titelli SA ne peut garantir l'exactitude, la précision ou l'exhaustivité 
              des informations mises à disposition.
            </p>
          </section>

          {/* Contact */}
          <section className="bg-gray-800/50 rounded-2xl p-6 border border-gray-700">
            <h2 className="text-xl font-bold text-white mb-4">Contact & Réclamations</h2>
            <p className="mb-4 leading-relaxed">
              Pour toute question relative à la protection de vos données personnelles ou pour exercer vos droits, 
              vous pouvez nous contacter :
            </p>
            <div className="space-y-3">
              <div className="flex items-center gap-3">
                <Mail className="w-5 h-5 text-yellow-400" />
                <span>privacy@titelli.com</span>
              </div>
              <div className="flex items-center gap-3">
                <Mail className="w-5 h-5 text-yellow-400" />
                <span>contact@titelli.com</span>
              </div>
              <div className="flex items-center gap-3">
                <MapPin className="w-5 h-5 text-yellow-400" />
                <span>Titelli SA - Lausanne, Suisse</span>
              </div>
            </div>
          </section>
        </div>

        {/* Footer links */}
        <div className="mt-16 pt-8 border-t border-gray-800 flex flex-wrap gap-6 text-sm text-gray-500">
          <Link to="/cgv" className="hover:text-yellow-400 transition-colors">Conditions Générales de Vente</Link>
          <Link to="/about" className="hover:text-yellow-400 transition-colors">À Propos</Link>
          <Link to="/partenaires" className="hover:text-yellow-400 transition-colors">Nos Partenaires</Link>
        </div>
      </div>
    </div>
  );
};

export default MentionsLegalesPage;
