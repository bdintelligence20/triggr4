import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { ArrowLeft, Eye, EyeOff, Loader2, Check, AlertCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { Label } from '../ui/label';

const passwordSchema = z.object({
  password: z
    .string()
    .min(8, 'Password must be at least 8 characters')
    .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
    .regex(/[0-9]/, 'Password must contain at least one number')
    .regex(/[^A-Za-z0-9]/, 'Password must contain at least one special character'),
  confirmPassword: z.string()
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
});

type ResetPasswordFormData = z.infer<typeof passwordSchema>;

const PasswordStrengthIndicator = ({ password }: { password: string }) => {
  const getStrength = () => {
    if (!password) return 0;
    let strength = 0;
    if (password.length >= 8) strength++;
    if (/[A-Z]/.test(password)) strength++;
    if (/[0-9]/.test(password)) strength++;
    if (/[^A-Za-z0-9]/.test(password)) strength++;
    return strength;
  };

  const strength = getStrength();
  const width = (strength / 4) * 100;
  const getColor = () => {
    if (strength <= 1) return 'bg-red-400';
    if (strength <= 2) return 'bg-yellow-400';
    if (strength <= 3) return 'bg-blue-400';
    return 'bg-green-400';
  };

  const getLabel = () => {
    if (strength <= 1) return 'Weak';
    if (strength <= 2) return 'Fair';
    if (strength <= 3) return 'Good';
    return 'Strong';
  };

  return (
    <div className="space-y-2">
      <div className="h-1.5 w-full bg-gray-100 rounded-full overflow-hidden">
        <motion.div
          className={`h-full ${getColor()}`}
          initial={{ width: 0 }}
          animate={{ width: `${width}%` }}
          transition={{ duration: 0.3 }}
        />
      </div>
      <div className="flex justify-between text-xs">
        <span className={`font-medium ${getColor().replace('bg-', 'text-')}`}>
          {getLabel()}
        </span>
        <span className="text-gray-500">
          {strength}/4 requirements met
        </span>
      </div>
    </div>
  );
};

const ResetPassword = () => {
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const { register, handleSubmit, watch, formState: { errors, isSubmitting } } = useForm<ResetPasswordFormData>({
    resolver: zodResolver(passwordSchema)
  });

  const password = watch('password', '');

  const onSubmit = async (data: ResetPasswordFormData) => {
    try {
      setError(null);
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Demo: Always succeed
      setIsSuccess(true);
      
      // Redirect to login after 2 seconds
      setTimeout(() => {
        navigate('/login');
      }, 2000);
    } catch (err) {
      setError('Failed to reset password. Please try again.');
    }
  };

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
        <h1 className="text-2xl font-bold mb-2">Reset Your Password</h1>
        <p className="text-gray-600">
          Please enter a new password for your account
        </p>
      </div>

      <AnimatePresence mode="wait">
        {isSuccess ? (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="text-center"
          >
            <div className="bg-emerald-50 text-emerald-600 p-6 rounded-lg">
              <Check className="w-12 h-12 mx-auto mb-4" />
              <h2 className="text-lg font-semibold mb-2">Password Reset Successful</h2>
              <p className="text-sm">
                Your password has been successfully reset. You will be redirected to login...
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
              <Label htmlFor="password">New Password</Label>
              <div className="relative">
                <Input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  {...register('password')}
                  className={errors.password ? 'border-red-400' : ''}
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
              <PasswordStrengthIndicator password={password} />
            </div>

            <div className="space-y-2">
              <Label htmlFor="confirmPassword">Confirm Password</Label>
              <div className="relative">
                <Input
                  id="confirmPassword"
                  type={showConfirmPassword ? 'text' : 'password'}
                  {...register('confirmPassword')}
                  className={errors.confirmPassword ? 'border-red-400' : ''}
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
                >
                  {showConfirmPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
              </div>
              {errors.confirmPassword && (
                <p className="text-sm text-red-500">{errors.confirmPassword.message}</p>
              )}
            </div>

            {error && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex items-center gap-2 bg-red-50 text-red-500 text-sm p-3 rounded-lg"
              >
                <AlertCircle size={16} />
                {error}
              </motion.div>
            )}

            <Button
              type="submit"
              className="w-full"
              disabled={isSubmitting}
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Resetting Password...
                </>
              ) : (
                'Reset Password'
              )}
            </Button>
          </motion.form>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

export default ResetPassword;
