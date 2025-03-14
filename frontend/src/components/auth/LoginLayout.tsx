import React from 'react';
import { motion } from 'framer-motion';
import LoginForm from './LoginForm';

const LoginLayout = () => {
  return (
    <div className="min-h-screen flex">
      {/* Branding Sidebar */}
      <div className="hidden lg:flex lg:flex-1 bg-gray-900 text-white p-8 items-center justify-center">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8 }}
          className="max-w-md"
        >
          <h1 className="text-4xl font-bold mb-4">
            <span className="text-white">triggr</span>
            <span className="text-emerald-400">Hub</span>
          </h1>
          <p className="text-gray-400 text-lg">
            Streamline your operations with our enterprise communication platform.
          </p>
        </motion.div>
      </div>

      {/* Login Form */}
      <div className="flex-1 flex items-center justify-center p-8 bg-gray-50">
        <LoginForm />
      </div>
    </div>
  );
};

export default LoginLayout;