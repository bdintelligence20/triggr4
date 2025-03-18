import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from '../../../ui/Button';
import { Input } from '../../../ui/Input';
import { Label } from '../../../ui/label';
import { Building2, Info, AlertCircle } from 'lucide-react';
import * as api from '../../../../services/api';

const organizationSchema = z.object({
  organizationName: z.string().min(1, 'Organization name is required').trim(),
  organizationSize: z.enum(['1-10', '11-50', '51-200', '201-500', '501+']),
  industry: z.string().min(1, 'Industry is required').trim(),
});

type OrganizationFormData = z.infer<typeof organizationSchema>;

interface OrganizationSetupProps {
  onComplete: (data: OrganizationFormData) => void;
}

const OrganizationSetup: React.FC<OrganizationSetupProps> = ({ onComplete }) => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const { register, handleSubmit, formState: { errors } } = useForm<OrganizationFormData>({
    resolver: zodResolver(organizationSchema),
    defaultValues: {
      organizationSize: '1-10',
    },
  });

  const handleFormSubmit = async (data: OrganizationFormData) => {
    try {
      setIsSubmitting(true);
      setError(null);
      
      // Call the API to create the organization
      const response = await api.createOrganization(
        data.organizationName,
        data.industry,
        data.organizationSize
      );
      
      if (response.error) {
        throw new Error(response.error);
      }
      
      // If successful, continue to the next step
      onComplete(data);
    } catch (err) {
      console.error('Organization creation failed:', err);
      setError(err instanceof Error ? err.message : 'Failed to create organization. Please try again.');
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

      <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-6">
        <div className="space-y-2">
          <Label htmlFor="organizationName">Organization Name</Label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Building2 size={16} className="text-gray-400" />
            </div>
            <Input
              id="organizationName"
              type="text"
              placeholder="Your company name"
              className="pl-10"
              {...register('organizationName')}
            />
          </div>
          {errors.organizationName && (
            <p className="text-sm text-red-500">{errors.organizationName.message}</p>
          )}
        </div>

        <div className="space-y-2">
          <Label htmlFor="industry">Industry</Label>
          <Input
            id="industry"
            type="text"
            placeholder="e.g. Healthcare, Finance, Education"
            {...register('industry')}
          />
          {errors.industry && (
            <p className="text-sm text-red-500">{errors.industry.message}</p>
          )}
        </div>

        <div className="space-y-2">
          <Label htmlFor="organizationSize">Organization Size</Label>
          <select
            id="organizationSize"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-400"
            {...register('organizationSize')}
          >
            <option value="1-10">1-10 employees</option>
            <option value="11-50">11-50 employees</option>
            <option value="51-200">51-200 employees</option>
            <option value="201-500">201-500 employees</option>
            <option value="501+">501+ employees</option>
          </select>
          {errors.organizationSize && (
            <p className="text-sm text-red-500">{errors.organizationSize.message}</p>
          )}
        </div>

        {error && (
          <div className="bg-red-50 p-4 rounded-lg flex items-start gap-3">
            <AlertCircle size={20} className="text-red-500 mt-0.5 flex-shrink-0" />
            <p className="text-sm text-red-700">{error}</p>
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
