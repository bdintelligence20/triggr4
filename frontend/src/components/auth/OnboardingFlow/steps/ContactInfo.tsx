import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { User, Mail, Phone } from 'lucide-react';

const contactSchema = z.object({
  fullName: z.string().min(2, 'Full name must be at least 2 characters'),
  email: z.string().email('Please enter a valid email address'),
  whatsapp: z.string().min(10, 'Please enter a valid phone number'),
});

type ContactFormData = z.infer<typeof contactSchema>;

interface ContactInfoProps {
  initialData: {
    fullName: string;
    email: string;
    whatsapp: string;
  };
  onComplete: (data: ContactFormData) => void;
}

const ContactInfo: React.FC<ContactInfoProps> = ({ initialData, onComplete }) => {
  const { register, handleSubmit, formState: { errors } } = useForm<ContactFormData>({
    resolver: zodResolver(contactSchema),
    defaultValues: initialData
  });

  return (
    <div className="bg-white rounded-xl shadow-sm p-8">
      <div className="text-center mb-8">
        <h1 className="text-2xl font-bold mb-2">Contact Information</h1>
        <p className="text-gray-600">
          Please provide your contact details
        </p>
      </div>

      <form onSubmit={handleSubmit(onComplete)} className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Full Name
          </label>
          <div className="relative">
            <input
              type="text"
              {...register('fullName')}
              className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400"
              placeholder="Enter your full name"
            />
            <User className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
          </div>
          {errors.fullName && (
            <p className="mt-1 text-sm text-red-500">{errors.fullName.message}</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Email Address
          </label>
          <div className="relative">
            <input
              type="email"
              {...register('email')}
              className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400"
              placeholder="Enter your email"
            />
            <Mail className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
          </div>
          {errors.email && (
            <p className="mt-1 text-sm text-red-500">{errors.email.message}</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            WhatsApp Number
          </label>
          <div className="relative">
            <input
              type="tel"
              {...register('whatsapp')}
              className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400"
              placeholder="Enter your WhatsApp number"
            />
            <Phone className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
          </div>
          {errors.whatsapp && (
            <p className="mt-1 text-sm text-red-500">{errors.whatsapp.message}</p>
          )}
        </div>

        <button
          type="submit"
          className="w-full py-2 px-4 bg-emerald-400 text-white rounded-lg hover:bg-emerald-300"
        >
          Continue
        </button>
      </form>
    </div>
  );
};

export default ContactInfo;