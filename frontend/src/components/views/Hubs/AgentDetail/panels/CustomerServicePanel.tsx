import React from 'react';
import { 
  CustomerServiceHeader, 
  OpenTickets, 
  CustomerFeedback, 
  CSATMetrics,
  TicketStats,
  TrendingIssues,
  SuppliersCustomers
} from '../sections';

const CustomerServicePanel = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <CustomerServiceHeader />
      
      <div className="max-w-[1920px] mx-auto px-6 pb-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Column - Primary Content */}
          <div className="space-y-8">
            {/* Open Tickets Section */}
            <div className="w-full">
              <OpenTickets />
            </div>
            
            {/* Customer Feedback and CSAT Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Customer Feedback - Wider Column */}
              <div className="md:col-span-2">
                <CustomerFeedback />
              </div>
              
              {/* CSAT Metrics - Narrower Column */}
              <div className="space-y-6">
                <CSATMetrics />
              </div>
            </div>
          </div>

          {/* Right Column - Analytics */}
          <div className="space-y-8">
            {/* Stats and Trending Issues Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Ticket Stats - Narrower Column */}
              <div className="md:col-span-1">
                <TicketStats />
              </div>
              
              {/* Trending Issues - Wider Column */}
              <div className="md:col-span-2">
                <TrendingIssues />
              </div>
            </div>

            {/* Suppliers and Customers Section */}
            <div className="w-full">
              <SuppliersCustomers />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CustomerServicePanel;