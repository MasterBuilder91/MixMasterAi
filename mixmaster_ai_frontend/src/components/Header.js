import React from 'react';
import { FiMusic, FiGithub } from 'react-icons/fi';

const Header = () => {
  return (
    <header className="bg-gray-900 shadow-md">
      <div className="container mx-auto px-4 py-4 flex justify-between items-center">
        <div className="flex items-center">
          <FiMusic className="text-purple-500 text-2xl mr-2" />
          <span className="text-white font-bold text-xl">MixMaster AI</span>
        </div>
        <nav>
          <ul className="flex space-x-6">
            <li>
              <a 
                href="#" 
                className="text-gray-300 hover:text-purple-400 transition-colors"
              >
                Home
              </a>
            </li>
            <li>
              <a 
                href="#" 
                className="text-gray-300 hover:text-purple-400 transition-colors"
              >
                How It Works
              </a>
            </li>
            <li>
              <a 
                href="#" 
                className="text-gray-300 hover:text-purple-400 transition-colors"
              >
                Pricing
              </a>
            </li>
          </ul>
        </nav>
      </div>
    </header>
  );
};

export default Header;
