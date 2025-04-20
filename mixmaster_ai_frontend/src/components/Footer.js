import React from 'react';
import { FiGithub, FiHeart } from 'react-icons/fi';

const Footer = () => {
  return (
    <footer className="bg-gray-900 py-8 mt-12">
      <div className="container mx-auto px-4">
        <div className="flex flex-col md:flex-row justify-between items-center">
          <div className="mb-4 md:mb-0">
            <p className="text-gray-400 text-sm">
              &copy; {new Date().getFullYear()} MixMaster AI. All rights reserved.
            </p>
          </div>
          
          <div className="flex items-center">
            <p className="text-gray-400 text-sm mr-4">
              Made with <FiHeart className="inline text-purple-500" /> by MixMaster Team
            </p>
            <a 
              href="#" 
              className="text-gray-400 hover:text-purple-400 transition-colors"
              aria-label="GitHub Repository"
            >
              <FiGithub size={20} />
            </a>
          </div>
        </div>
        
        <div className="mt-6 text-center">
          <p className="text-gray-500 text-xs">
            MixMaster AI uses advanced audio processing algorithms to automatically mix and master your tracks.
            Upload your vocals and beats to get professional-quality results in minutes.
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
