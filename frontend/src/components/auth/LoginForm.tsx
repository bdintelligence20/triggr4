import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Eye, EyeOff, MapIcon as WhatsappIcon } from 'lucide-react';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { Label } from '../ui/label';
import { useNavigate } from 'react-router-dom';

const loginSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
});

type LoginFormData = z.infer<typeof loginSchema>;

const LoginForm = () => {
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginFormData) => {
    try {
      setError(null);
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Navigate to OTP verification
      navigate('/verify');
    } catch (err) {
      setError('Invalid credentials. Please try again.');
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="w-full max-w-md space-y-8"
    >
      <div className="text-center">
        <h2 className="text-2xl font-bold tracking-tight">Welcome back</h2>
        <p className="text-sm text-gray-500 mt-2">
          Sign in to your account to continue
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        <div className="space-y-2">
          <Label htmlFor="email">Email</Label>
          <Input
            id="email"
            type="email"
            placeholder="you@company.com"
            {...register('email')}
          />
          {errors.email && (
            <p className="text-sm text-red-500">{errors.email.message}</p>
          )}
        </div>

        <div className="space-y-2">
          <Label htmlFor="password">Password</Label>
          <div className="relative">
            <Input
              id="password"
              type={showPassword ? 'text' : 'password'}
              placeholder="Enter your password"
              {...register('password')}
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
            >
              {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
            </button>
          </div>
          {errors.password && (
            <p className="text-sm text-red-500">{errors.password.message}</p>
          )}
        </div>

        {error && (
          <div className="bg-red-50 text-red-500 text-sm p-3 rounded-lg">
            {error}
          </div>
        )}

        <div className="flex items-center justify-between">
          <button
            type="button"
            onClick={() => navigate('/forgot-password')}
            className="text-sm text-emerald-400 hover:text-emerald-300"
          >
            Forgot password?
          </button>
        </div>

        <div className="space-y-4">
          <Button
            type="submit"
            className="w-full"
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Signing in...' : 'Sign in'}
          </Button>

          <Button
            type="button"
            variant="whatsapp"
            className="w-full"
          >
            <WhatsappIcon className="mr-2 h-5 w-5" />
            Sign in with WhatsApp
          </Button>
        </div>
      </form>
    </motion.div>
  );
};

export default LoginForm;
