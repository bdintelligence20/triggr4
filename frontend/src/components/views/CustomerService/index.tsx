import React from 'react';
import { Users, Clock, CheckCircle2, BarChart2, ShieldCheck } from 'lucide-react';
import CustomerServiceHeader from './CustomerServiceHeader';
import OpenTickets from './sections/OpenTickets';
import TrendingIssues from './sections/TrendingIssues';
import SuppliersCustomers from './sections/SuppliersCustomers';

const CustomerService = () => {
  return (
    <div className="min-h-[calc(100vh-64px)] bg-gray-50">
      <CustomerServiceHeader />
      
      <div className="max-w-[1920px] mx-auto px-8 py-8 space-y-8">
        {/* Top Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {/* Open Tickets */}
          <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-100">
            <div className="flex items-center justify-between mb-4">
              <div className="p-2 bg-emerald-50 rounded-lg">
                <Users size={20} className="text-emerald-500" />
              </div>
              <span className="px-2.5 py-1 bg-emerald-50 text-emerald-600 text-xs font-medium rounded-full">
                +12% vs last week
              </span>
            </div>
            <div className="space-y-1">
              <h3 className="text-sm font-medium text-gray-600">Open Tickets</h3>
              <div className="text-3xl font-bold text-gray-900">24</div>
              <p className="text-sm text-emerald-600">12 in progress</p>
            </div>
          </div>
          
          {/* Total Tickets */}
          <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-100">
            <div className="flex items-center justify-between mb-4">
              <div className="p-2 bg-blue-50 rounded-lg">
                <BarChart2 size={20} className="text-blue-500" />
              </div>
              <span className="px-2.5 py-1 bg-blue-50 text-blue-600 text-xs font-medium rounded-full">
                Last 30 days
              </span>
            </div>
            <div className="space-y-1">
              <h3 className="text-sm font-medium text-gray-600">Total Tickets</h3>
              <div className="text-3xl font-bold text-gray-900">156</div>
              <p className="text-sm text-blue-600">89% resolved</p>
            </div>
          </div>
          
          {/* CSAT Score */}
          <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-100">
            <div className="flex items-center justify-between mb-4">
              <div className="p-2 bg-purple-50 rounded-lg">
                <CheckCircle2 size={20} className="text-purple-500" />
              </div>
              <span className="px-2.5 py-1 bg-purple-50 text-purple-600 text-xs font-medium rounded-full">
                +2% vs last month
              </span>
            </div>
            <div className="space-y-1">
              <h3 className="text-sm font-medium text-gray-600">CSAT Score</h3>
              <div className="text-3xl font-bold text-gray-900">94%</div>
              <p className="text-sm text-purple-600">Very Good</p>
            </div>
          </div>
          
          {/* AI Resolution Rate */}
          <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-100">
            <div className="flex items-center justify-between mb-4">
              <div className="p-2 bg-teal-50 rounded-lg">
                <ShieldCheck size={20} className="text-teal-500" />
              </div>
              <span className="px-2.5 py-1 bg-teal-50 text-teal-600 text-xs font-medium rounded-full">
                +5% vs last month
              </span>
            </div>
            <div className="space-y-1">
              <h3 className="text-sm font-medium text-gray-600">AI Resolution Rate</h3>
              <div className="text-3xl font-bold text-gray-900">78%</div>
              <p className="text-sm text-teal-600">No supplier escalation</p>
            </div>
          </div>
        </div>

        {/* Two Column Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="bg-white rounded-lg shadow-sm">
            <OpenTickets />
          </div>
          <div className="bg-white rounded-lg shadow-sm">
            <TrendingIssues />
          </div>
        </div>

        {/* Full Width Suppliers & Customers */}
        <div className="bg-white rounded-lg shadow-sm">
          <SuppliersCustomers />
        </div>
      </div>
    </div>
  );
};

export default CustomerService;