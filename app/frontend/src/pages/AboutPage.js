import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  Play, 
  Check, 
  Star, 
  Shield, 
  Zap, 
  Heart,
  Users,
  TrendingUp,
  Award,
  Clock,
  MapPin,
  ChevronRight,
  Sparkles,
  Target,
  Gift
} from 'lucide-react';

const AboutPage = () => {
  const [activeVideo, setActiveVideo] = useState(null);

  // Vidéos promo lifestyle
  const promoVideos = [
    { id: 1, title: "Hakim et son chauffeur", description: "Découvrez comment Titelli simplifie votre quotidien" },
    { id: 2, title: "Une sortie en famille", description: "Planifiez des moments inoubliables" },
    { id: 3, title: "Grand-mère et son quotidien", description: "La technologie au service de tous" },
    { id: 4, title: "Femme d'affaire, toujours", description: "Efficacité et élégance au quotidien" },
    { id: 5, title: "Business is business", description: "Comment gagner avec Titelli" },
    { id: 6, title: "Soirée entre copines!", description: "Organisez vos sorties en un clic" },
    { id: 7, title: "J'invite ma femme ce soir!", description: "Surprenez vos proches" },
    { id: 8, title: "Surprise pour mâle?", description: "Des idées cadeaux originales" },
  ];

  // Avantages Titelli
  const advantages = [
    {
      icon: Zap,
      title: "Vidéos X",
      description: "retrouve mes vidéos les plus cochonnes, des vidéos exclusives et des vidéos personnalisées !"
    },
    {
      icon: Heart,
      title: "Films X",
      description: "retrouve mes films les plus cochons, des films exclusives et des films personnalisées !"
    },
    {
      icon: Users,
      title: "Tournage vidéos avec moi !",
      description: "Participe à mes vidéos et deviens acteur de mes contenus !"
    },
    {
      icon: Gift,
      title: "Shopping express",
      description: "Un parfum en chemin, une paire de chaussures ou votre snack préféré!"
    },
    {
      icon: Shield,
      title: "Professionnels certifiés",
      description: "Recevez un professionnel de santé à domicile ou un expert comptable."
    },
    {
      icon: Award,
      title: "Prestataires labellisés",
      description: "Les meilleures prestations à domicile avec nos prestataires labellisés."
    }
  ];

  return (
    <div className="min-h-screen bg-[#black]">
      {/* Hero Section */}
      <section className="relative pt-24 pb-20 px-4 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-yellow-500/10 via-transparent to-transparent" />
        
        <div className="max-w-6xl mx-auto relative z-10">
          <div className="text-center mb-16">
            <h1 className="text-5xl md:text-6xl font-bold text-white mb-6" style={{ fontFamily: 'Playfair Display, serif' }}>
              Bienvenue sur mon <span className="text-red-400">site</span>
            </h1>
            <p className="text-2xl md:text-3xl text-red-400 font-medium mb-8">
              LA MEILLEURE ESCORT DE GENEVE,<br />
              SPECIALISTE DES RENCONTRES ET CONTENUS HARD DEPUIS 2010
            </p>
            <p className="text-xl text-gray-400 max-w-3xl mx-auto">
              Retrouve tout mes services ainsi que toutes mes informations !
            </p>
          </div>

          {/* Vision & Mission */}
          <div className="grid md:grid-cols-2 gap-8 mb-20">
            <div className="bg-gradient-to-br from-yellow-500/10 to-orange-500/10 rounded-2xl p-8 border border-yellow-500/20">
              <Target className="w-12 h-12 text-yellow-400 mb-4" />
              <h2 className="text-2xl font-bold text-white mb-4">MES KIFFS ?</h2>
              <p className="text-gray-400 text-lg leading-relaxed">
                Rendre le client le plus heureux et satisfait en proposant mes services de soumission extreme, avec moi tu peut prendre tout le controle
                et evacuer tout ton stress sans limite, du soft aux services extremes je pratique de tout et avec passion.
              </p>
            </div>
            
            <div className="bg-gradient-to-br from-orange-500/10 to-red-500/10 rounded-2xl p-8 border border-orange-500/20">
              <Sparkles className="w-12 h-12 text-orange-400 mb-4" />
              <h2 className="text-2xl font-bold text-white mb-4">QUE PROPOSE LE SITE ?</h2>
              <p className="text-gray-400 text-lg leading-relaxed">
                Je propose des services de soumission extreme, du soft au extreme, des vidéos tres cochonnes, du cashback, des offres de participations a mes vidéos et d'autre avantages !
              </p>
            </div>
          </div>

          {/* Slogan central */}
          <div className="text-center mb-20 py-12 bg-gradient-to-r from-transparent via-yellow-500/10 to-transparent rounded-3xl">
            <blockquote className="text-3xl md:text-4xl font-bold text-white italic mb-4">
              "clairement la numero 1 de la Suisse Romande."
            </blockquote>
            <p className="text-xl text-pink-400">
              « Ne cherchez plus une escort, tu l'a trouvéé ! »
            </p>
          </div>
        </div>
      </section>

      {/* Avantages Section */}
      <section className="py-20 px-4 bg-gradient-to-b from-transparent via-gray-900/50 to-transparent">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold text-white text-center mb-4">
            Liste <span className="text-pink-400">Avantages</span>
          </h2>
          <p className="text-gray-400 text-center mb-12 text-lg">
            Découvrez la liste complete de mes avantages et services exclusifs pour une expérience inoubliable.
          </p>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {advantages.map((adv, index) => (
              <div 
                key={index}
                className="bg-gray-800/50 rounded-xl p-6 border border-gray-700 hover:border-yellow-500/50 transition-all group"
              >
                <adv.icon className="w-10 h-10 text-pink-400 mb-4 group-hover:scale-110 transition-transform" />
                <h3 className="text-xl font-bold text-white mb-2">{adv.title}</h3>
                <p className="text-gray-400">{adv.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Vidéos Promo Section */}
     
      {/* CTA Section */}
      <section className="py-20 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
            Prêt à rejoindre <span className="text-gradient-to-r from-pink-500 to-red-500">ma communauté</span> ?
          </h2>
 
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link 
              to="/inscription-entreprise"
              className="px-8 py-4 bg-gradient-to-r from-pink-500 to-red-500 text-black font-bold rounded-xl hover:from-yellow-600 hover:to-orange-600 transition-all flex items-center justify-center gap-2"
            >
              je te veut ! <ChevronRight className="w-5 h-5" />
            </Link>
            <Link 
              to="/auth"
              className="px-8 py-4 bg-gray-800 text-white font-bold rounded-xl hover:bg-gray-700 transition-all border border-gray-600"
            >
              Créer un compte client
            </Link>
          </div>
        </div>
      </section>

      {/* Footer links */}
      <section className="py-12 px-4 border-t border-gray-800">
        <div className="max-w-6xl mx-auto flex flex-wrap justify-center gap-6 text-sm text-gray-500">
          <Link to="/cgv" className="hover:text-yellow-400 transition-colors">Conditions Générales de Vente</Link>
          <span>•</span>
          <Link to="/mentions-legales" className="hover:text-yellow-400 transition-colors">Mentions Légales</Link>
          <span>•</span>
          <Link to="/partenaires" className="hover:text-yellow-400 transition-colors">Nos Partenaires</Link>
        </div>
      </section>
    </div>
  );
};

export default AboutPage;
