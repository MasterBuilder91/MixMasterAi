import React, { useState } from 'react';
import { FiSliders, FiMusic } from 'react-icons/fi';

const ProcessingOptions = ({ options, onChange }) => {
  const [localOptions, setLocalOptions] = useState(options);

  const handleChange = (e) => {
    const { name, value } = e.target;
    const newOptions = {
      ...localOptions,
      [name]: name === 'reverbAmount' || name === 'compressionAmount' 
        ? parseFloat(value) 
        : value
    };
    
    setLocalOptions(newOptions);
    onChange(newOptions);
  };

  return (
    <div className="bg-gray-800 rounded-lg p-6 mb-8 shadow-lg">
      <h2 className="text-2xl font-bold mb-6 text-center text-purple-400 flex items-center justify-center">
        <FiSliders className="mr-2" />
        Processing Options
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="space-y-4">
          <div>
            <label className="block text-gray-300 mb-2" htmlFor="genre">
              Genre / Style
            </label>
            <select
              id="genre"
              name="genre"
              value={localOptions.genre}
              onChange={handleChange}
              className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value="default">Auto-Detect</option>
              <option value="trap">Trap</option>
              <option value="hip_hop">Hip-Hop</option>
              <option value="pop">Pop</option>
              <option value="r_and_b">R&B</option>
            </select>
          </div>

          <div>
            <label className="block text-gray-300 mb-2" htmlFor="outputFormat">
              Output Format
            </label>
            <select
              id="outputFormat"
              name="outputFormat"
              value={localOptions.outputFormat}
              onChange={handleChange}
              className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value="wav">WAV (High Quality)</option>
              <option value="mp3">MP3 (Smaller Size)</option>
            </select>
          </div>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-gray-300 mb-2" htmlFor="reverbAmount">
              Reverb Amount: {localOptions.reverbAmount.toFixed(1)}
            </label>
            <input
              id="reverbAmount"
              name="reverbAmount"
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={localOptions.reverbAmount}
              onChange={handleChange}
              className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-purple-500"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>Dry</span>
              <span>Wet</span>
            </div>
          </div>

          <div>
            <label className="block text-gray-300 mb-2" htmlFor="compressionAmount">
              Compression Amount: {localOptions.compressionAmount.toFixed(1)}
            </label>
            <input
              id="compressionAmount"
              name="compressionAmount"
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={localOptions.compressionAmount}
              onChange={handleChange}
              className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-purple-500"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>Subtle</span>
              <span>Heavy</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProcessingOptions;
