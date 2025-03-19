import React from 'react';
import { MessageSquare, Mail, Bell, Settings } from 'lucide-react';

interface CustomerServiceHeaderProps {
  title?: string;
  subtitle?: string;
}

const CustomerServiceHeader: React.FC<CustomerServiceHeaderProps> = ({
  title = "Customer Service Hub",
  subtitle = "Manage client relationships and support"
}) => {
  return (
    <div className="relative mb-8">
      {/* Background Image Container */}
      <div className="absolute inset-0 h-48">
        <img 
          src="https://images.unsplash.com/photo-1664575602276-acd073f104c1?q=80&w=2070&auto=format&fit=crop"
          alt="Customer Service Background"
          className="w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-b from-black/60 to-transparent" />
      </div>

      {/* Content Container */}
      <div className="relative pt-8 pb-4">
        <div className="max-w-[1920px] mx-auto px-6">
          {/* White Background Container */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
              {/* Title and Subtitle */}
              <div className="flex-1 min-w-0">
                <h1 className="text-2xl font-bold text-gray-900 leading-tight truncate">
                  {title}
                </h1>
                <p className="text-sm text-gray-500 mt-1.5">{subtitle}</p>
              </div>

              {/* Action Buttons */}
              <div className="flex flex-wrap items-center gap-3">
                <button className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-50 text-emerald-600 rounded-lg hover:bg-emerald-100 transition-colors">
                  <MessageSquare size={18} />
                  <span className="hidden sm:inline font-medium">Send Message</span>
                </button>
                
                <button className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-50 text-emerald-600 rounded-lg hover:bg-emerald-100 transition-colors">
                  <Mail size={18} />
                  <span className="hidden sm:inline font-medium">Send Email</span>
                </button>
                
                <button className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-50 text-emerald-600 rounded-lg hover:bg-emerald-100 transition-colors">
                  <Bell size={18} />
                  <span className="hidden sm:inline font-medium">Send Notification</span>
                </button>

                <div className="w-px h-8 bg-gray-200 mx-1 hidden sm:block"></div>

                <button 
                  className="p-2 text-emerald-600 hover:bg-emerald-50 rounded-lg transition-colors"
                  aria-label="Hub Settings"
                >
                  <Settings size={20} />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CustomerServiceHeader;