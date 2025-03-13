// components/layout/Footer.tsx
import React from 'react';

const Footer: React.FC = () => {
  return (
    <footer className="bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700 py-6 text-center text-sm text-gray-500 dark:text-gray-400 mt-8">
      <div className="flex flex-col items-center justify-center space-y-2">
        <p className="text-emerald-500 font-bold">triggrHub</p>
        <p>Made by triggrHub © 2025</p>
        <p>Powered by Claude 3.5 Sonnet</p>
      </div>
    </footer>
  );
};

export default Footer;