import React from 'react';
import { motion } from 'framer-motion';
import { Moon, Sun, Type, Globe } from 'lucide-react';

interface UIPreferencesProps {
  preferences: {
    darkMode: boolean;
    fontSize: string;
    language: string;
  };
  onUpdate: (updates: any) => void;
}

const UIPreferences: React.FC<UIPreferencesProps> = ({
  preferences,
  onUpdate
}) => {
  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white rounded-lg shadow-sm p-6"
      >
        <h2 className="text-lg font-semibold mb-6">Display Settings</h2>
        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 border rounded-lg">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-emerald-50 rounded-lg">
                {preferences.darkMode ? (
                  <Moon className="text-emerald-400" size={20} />
                ) : (
                  <Sun className="text-emerald-400" size={20} />
                )}
              </div>
              <div>
                <div className="font-medium">Dark Mode</div>
                <div className="text-sm text-gray-500">Switch between light and dark themes</div>
              </div>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={preferences.darkMode}
                onChange={() => onUpdate({
                  preferences: {
                    ...preferences,
                    darkMode: !preferences.darkMode
                  }
                })}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-emerald-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-emerald-400"></div>
            </label>
          </div>

          <div className="flex items-center justify-between p-4 border rounded-lg">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-emerald-50 rounded-lg">
                <Type className="text-emerald-400" size={20} />
              </div>
              <div>
                <div className="font-medium">Font Size</div>
                <div className="text-sm text-gray-500">Adjust the text size</div>
              </div>
            </div>
            <select
              value={preferences.fontSize}
              onChange={(e) => onUpdate({
                preferences: {
                  ...preferences,
                  fontSize: e.target.value
                }
              })}
              className="px-3 py-2 border rounded-lg focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400"
            >
              <option value="small">Small</option>
              <option value="normal">Normal</option>
              <option value="large">Large</option>
            </select>
          </div>
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-white rounded-lg shadow-sm p-6"
      >
        <h2 className="text-lg font-semibold mb-6">Language & Region</h2>
        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 border rounded-lg">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-emerald-50 rounded-lg">
                <Globe className="text-emerald-400" size={20} />
              </div>
              <div>
                <div className="font-medium">Language</div>
                <div className="text-sm text-gray-500">Choose your preferred language</div>
              </div>
            </div>
            <select
              value={preferences.language}
              onChange={(e) => onUpdate({
                preferences: {
                  ...preferences,
                  language: e.target.value
                }
              })}
              className="px-3 py-2 border rounded-lg focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400"
            >
              <option value="en">English</option>
              <option value="es">Español</option>
              <option value="fr">Français</option>
              <option value="de">Deutsch</option>
            </select>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default UIPreferences;