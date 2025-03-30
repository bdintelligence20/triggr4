import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { Label } from '../ui/label';

interface RegisterFormData {
  email: string;
  password: string;
  confirmPassword: string;
  fullName: string;
}

const RegisterForm: React.FC = () => {
  const [formData, setFormData] = useState<RegisterFormData>({
    email: '',
    password: '',
    confirmPassword: '',
    fullName: ''
  });
  const [errors, setErrors] = useState<{
    email?: string;
    password?: string;
    confirmPassword?: string;
    fullName?: string;
  }>({});
  const [apiError, setApiError] = useState<string | null>(null);
  const { register, error, isLoading } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Clear error when user types
    if (errors[name as keyof typeof errors]) {
      setErrors(prev => ({
        ...prev,
        [name]: undefined
      }));
    }
  };

  const validateForm = (): boolean => {
    const newErrors: {
      email?: string;
      password?: string;
      confirmPassword?: string;
      fullName?: string;
    } = {};
    
    // Validate fullName
    if (!formData.fullName.trim()) {
      newErrors.fullName = 'Full name is required';
    }
    
    // Validate email
    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }
    
    // Validate password
    if (!formData.password.trim()) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }
    
    // Validate confirmPassword
    if (!formData.confirmPassword.trim()) {
      newErrors.confirmPassword = 'Please confirm your password';
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    try {
      setApiError(null);
      
      console.log('Registering user:', { email: formData.email, fullName: formData.fullName });
      
      // Register user
      const success = await register(formData.email, formData.password, formData.fullName);
      
      console.log('Registration result:', success);
      
      if (success) {
        // Redirect to onboarding
        console.log('Redirecting to onboarding');
        navigate('/onboarding');
      } else {
        console.error('Registration failed but no error was thrown');
        setApiError('Registration failed. Please try again.');
      }
    } catch (err) {
      console.error('Registration error:', err);
      setApiError(err instanceof Error ? err.message : 'An unexpected error occurred');
    }
  };

  return (
    <div className="w-full max-w-md p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-6 text-center text-gray-800">Create an Account</h2>
      
      {(error || apiError) && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4">
          <p className="font-medium">Error</p>
          <p>{apiError || error}</p>
        </div>
      )}
      
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <Label htmlFor="fullName">Full Name</Label>
          <Input
            id="fullName"
            name="fullName"
            type="text"
            value={formData.fullName}
            onChange={handleChange}
            placeholder="John Doe"
            className="w-full"
          />
          {errors.fullName && (
            <p className="text-sm text-red-500">{errors.fullName}</p>
          )}
        </div>
        
        <div className="mb-4">
          <Label htmlFor="email">Email</Label>
          <Input
            id="email"
            name="email"
            type="email"
            value={formData.email}
            onChange={handleChange}
            placeholder="you@example.com"
            className="w-full"
          />
          {errors.email && (
            <p className="text-sm text-red-500">{errors.email}</p>
          )}
        </div>
        
        <div className="mb-4">
          <Label htmlFor="password">Password</Label>
          <Input
            id="password"
            name="password"
            type="password"
            value={formData.password}
            onChange={handleChange}
            placeholder="••••••••"
            className="w-full"
          />
          {errors.password && (
            <p className="text-sm text-red-500">{errors.password}</p>
          )}
        </div>
        
        <div className="mb-6">
          <Label htmlFor="confirmPassword">Confirm Password</Label>
          <Input
            id="confirmPassword"
            name="confirmPassword"
            type="password"
            value={formData.confirmPassword}
            onChange={handleChange}
            placeholder="••••••••"
            className="w-full"
          />
          {errors.confirmPassword && (
            <p className="text-sm text-red-500">{errors.confirmPassword}</p>
          )}
        </div>
        
        <Button
          type="submit"
          className="w-full"
          disabled={isLoading}
          isLoading={isLoading}
        >
          Register
        </Button>
      </form>
      
      <div className="mt-4 text-center">
        <p className="text-sm text-gray-600">
          Already have an account?{' '}
          <a
            href="/login"
            className="text-blue-600 hover:text-blue-800"
            onClick={(e: React.MouseEvent<HTMLAnchorElement>) => {
              e.preventDefault();
              navigate('/login');
            }}
          >
            Log in
          </a>
        </p>
      </div>
    </div>
  );
};

export default RegisterForm;
