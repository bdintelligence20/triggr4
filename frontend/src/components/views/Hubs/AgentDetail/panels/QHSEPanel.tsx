import React from 'react';
import { ShieldCheck, AlertTriangle, FileCheck } from 'lucide-react';

const QHSEPanel = () => {
  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <h2 className="text-lg font-semibold mb-6">QHSE Management</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <button className="p-6 border rounded-lg hover:border-emerald-400 hover:bg-emerald-50 transition-colors text-left group">
          <AlertTriangle className="text-emerald-400 mb-4" size={24} />
          <h3 className="font-semibold group-hover:text-emerald-400">Incident Reports</h3>
          <p className="text-gray-500 mt-2">Log and track safety incidents</p>
        </button>

        <button className="p-6 border rounded-lg hover:border-emerald-400 hover:bg-emerald-50 transition-colors text-left group">
          <ShieldCheck className="text-emerald-400 mb-4" size={24} />
          <h3 className="font-semibold group-hover:text-emerald-400">Risk Assessment</h3>
          <p className="text-gray-500 mt-2">Evaluate and manage workplace risks</p>
        </button>

        <button className="p-6 border rounded-lg hover:border-emerald-400 hover:bg-emerald-50 transition-colors text-left group">
          <FileCheck className="text-emerald-400 mb-4" size={24} />
          <h3 className="font-semibold group-hover:text-emerald-400">Compliance</h3>
          <p className="text-gray-500 mt-2">Monitor regulatory compliance</p>
        </button>
      </div>
    </div>
  );
};

export default QHSEPanel;