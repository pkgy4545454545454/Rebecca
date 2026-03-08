import React from 'react';
import { Link } from 'react-router-dom';
import { Mail, MapPin } from 'lucide-react';

const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-[#0A0A0A] border-t border-white/5" data-testid="main-footer">
      <div className="max-w-7xl mx-auto px-4 md:px-8 py-12">
        <div className="flex flex-col md:flex-row justify-between items-center gap-8">
          {/* Brand */}
          <div className="flex items-center gap-3">
            <img src="/esclava.png" alt="Esclava" className="w-10 h-10 object-contain" />
            <span className="font-semibold text-xl text-white">
              Esclava
            </span>
          </div>
          {/* Contact */}
          <div className="flex flex-col sm:flex-row items-center gap-6">
            <a href="mailto:russesita9@gmail.com" className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors">
              <Mail className="w-4 h-4" />
              <span className="text-sm">russesita9@gmail.com</span>
            </a>
            <div className="flex items-center gap-2 text-gray-400">
              <MapPin className="w-4 h-4" />
              <span className="text-sm">Lausanne, Suisse</span>
            </div>
          </div>
        </div>
        {/* Bottom */}
        <div className="mt-8 pt-6 border-t border-white/5 flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-gray-500 text-sm">
            © {currentYear} Esclava. Tous droits réservés.
          </p>
          <div className="flex items-center gap-4">
            <Link to="/cgv" className="text-gray-500 hover:text-gray-300 text-sm transition-colors">CGV</Link>
            <Link to="/mentions-legales" className="text-gray-500 hover:text-gray-300 text-sm transition-colors">Mentions légales</Link>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
