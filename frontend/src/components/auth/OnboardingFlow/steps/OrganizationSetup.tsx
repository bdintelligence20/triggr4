import React, { useState } from 'react';
import { Button } from '../../../ui/Button';
import { Input } from '../../../ui/Input';
import { Label } from '../../../ui/label';
import { Building2, Info, AlertCircle } from 'lucide-react';
import * as api from '../../../../services/api';

interface OrganizationFormData {
  organizationName: string;
  organizationSize: string;
  industry: string;
}

interface OrganizationSetupProps {
  onComplete: (data: OrganizationFormData) => void;
}

const OrganizationSetup: React.FC<OrganizationSetupProps> = ({ onComplete }) => {
  const [formData, setFormData] = useState<OrganizationFormData>({
    organizationName: '',
    organizationSize: '1-10',
    industry: '',
  });
  
  const [errors, setErrors] = useState<{
    organizationName?: string;
    industry?: string;
  }>({});
  
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
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
      organizationName?: string;
      industry?: string;
    } = {};
    
    // Validate organizationName
    if (!formData.organizationName.trim()) {
      newErrors.organizationName = 'Organization name is required';
    }
    
    // Validate industry
    if (!formData.industry.trim()) {
      newErrors.industry = 'Industry is required';
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
      setIsSubmitting(true);
      setApiError(null);
      
      // Call the API to create the organization
      const response = await api.createOrganization(
        formData.organizationName,
        formData.industry,
        formData.organizationSize
      );
      
      if (response.error) {
        throw new Error(response.error);
      }
      
      // If successful, continue to the next step
      onComplete(formData);
    } catch (err) {
      console.error('Organization creation failed:', err);
      setApiError(err instanceof Error ? err.message : 'Failed to create organization. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };
  
  return (
    <div className="bg-white rounded-xl shadow-sm p-8">
      <div className="text-center mb-8">
        <h1 className="text-2xl font-bold mb-2">Organization Setup</h1>
        <p className="text-gray-600">
          Set up your organization's knowledge hub
        </p>
      </div>

      <div className="bg-blue-50 p-4 rounded-lg flex items-start gap-3 mb-6">
        <Info size={20} className="text-blue-500 mt-0.5 flex-shrink-0" />
        <p className="text-sm text-blue-700">
          Your organization will have its own dedicated knowledge base with isolated data storage and vector database.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="space-y-2">
          <Label htmlFor="organizationName">Organization Name</Label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Building2 size={16} className="text-gray-400" />
            </div>
            <Input
              id="organizationName"
              name="organizationName"
              type="text"
              value={formData.organizationName}
              onChange={handleChange}
              placeholder="Your company name"
              className="pl-10 w-full"
            />
          </div>
          {errors.organizationName && (
            <p className="text-sm text-red-500">{errors.organizationName}</p>
          )}
        </div>

        <div className="space-y-2">
          <Label htmlFor="industry">Industry</Label>
          <Input
            id="industry"
            name="industry"
            type="text"
            value={formData.industry}
            onChange={handleChange}
            placeholder="e.g. Healthcare, Finance, Education"
            className="w-full"
          />
          {errors.industry && (
            <p className="text-sm text-red-500">{errors.industry}</p>
          )}
        </div>

        <div className="space-y-2">
          <Label htmlFor="organizationSize">Organization Size</Label>
          <select
            id="organizationSize"
            name="organizationSize"
            value={formData.organizationSize}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400"
          >
            <option value="1-10">1-10 employees</option>
            <option value="11-50">11-50 employees</option>
            <option value="51-200">51-200 employees</option>
            <option value="201-500">201-500 employees</option>
            <option value="501+">501+ employees</option>
          </select>
        </div>

        {apiError && (
          <div className="bg-red-50 p-4 rounded-lg flex items-start gap-3">
            <AlertCircle size={20} className="text-red-500 mt-0.5 flex-shrink-0" />
            <p className="text-sm text-red-700">{apiError}</p>
          </div>
        )}

        <Button
          type="submit"
          className="w-full"
          disabled={isSubmitting}
        >
          {isSubmitting ? 'Creating...' : 'Create Organization'}
        </Button>
      </form>
    </div>
  );
};

export default OrganizationSetup;
