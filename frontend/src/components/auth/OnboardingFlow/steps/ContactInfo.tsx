import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from '../../../ui/Button';
import { Input } from '../../../ui/Input';
import { Label } from '../../../ui/label';

const contactSchema = z.object({
  fullName: z.string().min(2, 'Full name is required'),
  email: z.string().email('Please enter a valid email address'),
  whatsapp: z.string().optional(),
});

type ContactFormData = z.infer<typeof contactSchema>;

interface ContactInfoProps {
  initialData: {
    fullName: string;
    email: string;
    whatsapp?: string;
  };
  onComplete: (data: ContactFormData) => void;
}

const ContactInfo: React.FC<ContactInfoProps> = ({ initialData, onComplete }) => {
  const { register, handleSubmit, formState: { errors } } = useForm<ContactFormData>({
    resolver: zodResolver(contactSchema),
    defaultValues: initialData,
  });

  return (
    <div className="bg-white rounded-xl shadow-sm p-8">
      <div className="text-center mb-8">
        <h1 className="text-2xl font-bold mb-2">Contact Information</h1>
        <p className="text-gray-600">
          How would you like to be contacted?
        </p>
      </div>

      <form onSubmit={handleSubmit(onComplete)} className="space-y-6">
        <div className="space-y-2">
          <Label htmlFor="fullName">Full Name</Label>
          <Input
            id="fullName"
            type="text"
            placeholder="Your full name"
            {...register('fullName')}
          />
          {errors.fullName && (
            <p className="text-sm text-red-500">{errors.fullName.message}</p>
          )}
        </div>

        <div className="space-y-2">
          <Label htmlFor="email">Email Address</Label>
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
          <Label htmlFor="whatsapp">WhatsApp Number (Optional)</Label>
          <Input
            id="whatsapp"
            type="tel"
            placeholder="+27 12 345 6789"
            {...register('whatsapp')}
          />
          {errors.whatsapp && (
            <p className="text-sm text-red-500">{errors.whatsapp.message}</p>
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
