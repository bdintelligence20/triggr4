import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { ArrowLeft, Check, LogIn as WhatsappLogo } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { Label } from '../ui/label';
import OnboardingFlow from './OnboardingFlow';

const otpSchema = z.object({
  otp: z.string().length(6, 'Please enter a valid 6-digit code'),
});

type OTPFormData = z.infer<typeof otpSchema>;

const OTPVerification = () => {
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [cooldown, setCooldown] = useState(0);
  const [showOnboarding, setShowOnboarding] = useState(false);
  const navigate = useNavigate();

  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<OTPFormData>({
    resolver: zodResolver(otpSchema),
  });

  useEffect(() => {
    let redirectTimer: NodeJS.Timeout;
    
    if (isSubmitted) {
      redirectTimer = setTimeout(() => {
        setShowOnboarding(true);
      }, 2000);
    }

    return () => {
      if (redirectTimer) {
        clearTimeout(redirectTimer);
      }
    };
  }, [isSubmitted, navigate]);

  const onSubmit = async (data: OTPFormData) => {
    try {
      setError(null);
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Demo: Always succeed for 123456
      if (data.otp === '123456') {
        setIsSubmitted(true);
        setCooldown(30);
        
        // Start cooldown timer
        const timer = setInterval(() => {
          setCooldown((prev) => {
            if (prev <= 1) {
              clearInterval(timer);
              return 0;
            }
            return prev - 1;
          });
        }, 1000);
      } else {
        setError('Invalid verification code. Please try again.');
      }
    } catch (err) {
      setError('An error occurred. Please try again later.');
    }
  };

  if (showOnboarding) {
    return <OnboardingFlow />;
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="w-full max-w-md mx-auto p-6"
    >
      <button
        onClick={() => navigate('/login')}
        className="flex items-center text-gray-600 hover:text-gray-900 mb-8"
      >
        <ArrowLeft className="mr-2" size={20} />
        Back to Login
      </button>

      <div className="text-center mb-8">
        <h1 className="text-2xl font-bold mb-2">Enter Verification Code</h1>
        <p className="text-gray-600">
          Enter the 6-digit code we sent to your email/WhatsApp
        </p>
      </div>

      <AnimatePresence mode="wait">
        {isSubmitted ? (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="text-center space-y-6"
          >
            <div className="bg-emerald-50 text-emerald-600 p-6 rounded-lg">
              <Check className="w-12 h-12 mx-auto mb-4" />
              <h2 className="text-lg font-semibold mb-2">Verification Successful</h2>
              <p className="text-sm">
                Your identity has been verified.
                Setting up your account...
              </p>
            </div>
          </motion.div>
        ) : (
          <motion.form
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            onSubmit={handleSubmit(onSubmit)}
            className="space-y-6"
          >
            <div className="space-y-2">
              <Label htmlFor="otp">Verification Code</Label>
              <Input
                id="otp"
                type="text"
                placeholder="Enter 6-digit code"
                maxLength={6}
                {...register('otp')}
              />
              {errors.otp && (
                <p className="text-sm text-red-500">{errors.otp.message}</p>
              )}
            </div>

            {error && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-red-50 text-red-500 text-sm p-3 rounded-lg"
              >
                {error}
              </motion.div>
            )}

            <Button
              type="submit"
              className="w-full"
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Verifying...' : 'Verify Code'}
            </Button>

            <div className="text-center">
              <button
                type="button"
                disabled={cooldown > 0}
                className={`text-sm ${
                  cooldown > 0 
                    ? 'text-gray-400 cursor-not-allowed' 
                    : 'text-emerald-400 hover:text-emerald-500'
                }`}
              >
                {cooldown > 0 ? `Resend in ${cooldown}s` : 'Resend Code'}
              </button>
            </div>
          </motion.form>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

export default OTPVerification;
