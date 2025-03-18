import React, { useState } from 'react';
import { Button } from '../../../ui/Button';
import { Input } from '../../../ui/Input';
import { Label } from '../../../ui/label';

interface ContactFormData {
  fullName: string;
  email: string;
  whatsapp?: string;
}

interface ContactInfoProps {
  initialData: {
    fullName: string;
    email: string;
    whatsapp?: string;
  };
  onComplete: (data: ContactFormData) => void;
}

const ContactInfo: React.FC<ContactInfoProps> = ({ initialData, onComplete }) => {
  const [formData, setFormData] = useState<ContactFormData>({
    fullName: initialData.fullName || '',
    email: initialData.email || '',
    whatsapp: initialData.whatsapp || '',
  });
  const [errors, setErrors] = useState<{
    fullName?: string;
    email?: string;
    whatsapp?: string;
  }>({});

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
      fullName?: string;
      email?: string;
      whatsapp?: string;
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
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (validateForm()) {
      onComplete(formData);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm p-8">
      <div className="text-center mb-8">
        <h1 className="text-2xl font-bold mb-2">Contact Information</h1>
        <p className="text-gray-600">
          How would you like to be contacted?
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="space-y-2">
          <Label htmlFor="fullName">Full Name</Label>
          <Input
            id="fullName"
            name="fullName"
            type="text"
            value={formData.fullName}
            onChange={handleChange}
            placeholder="Your full name"
          />
          {errors.fullName && (
            <p className="text-sm text-red-500">{errors.fullName}</p>
          )}
        </div>

        <div className="space-y-2">
          <Label htmlFor="email">Email Address</Label>
          <Input
            id="email"
            name="email"
            type="email"
            value={formData.email}
            onChange={handleChange}
            placeholder="you@company.com"
          />
          {errors.email && (
            <p className="text-sm text-red-500">{errors.email}</p>
          )}
        </div>

        <div className="space-y-2">
          <Label htmlFor="whatsapp">WhatsApp Number (Optional)</Label>
          <Input
            id="whatsapp"
            name="whatsapp"
            type="tel"
            value={formData.whatsapp}
            onChange={handleChange}
            placeholder="+27 12 345 6789"
          />
          {errors.whatsapp && (
            <p className="text-sm text-red-500">{errors.whatsapp}</p>
          )}
          <p className="text-xs text-gray-500">
            We'll use this for WhatsApp notifications if you enable them
          </p>
        </div>

        <Button
          type="submit"
          className="w-full"
        >
          Continue
        </Button>
      </form>
    </div>
  );
};

export default ContactInfo;
