import React from 'react';
import { Play, ArrowRight } from 'lucide-react';

interface OnboardingVideoProps {
  onComplete: () => void;
  onSkip: () => void;
}

const OnboardingVideo: React.FC<OnboardingVideoProps> = ({ onComplete, onSkip }) => {
  return (
    <div className="bg-white rounded-xl shadow-sm p-8">
      <div className="text-center mb-8">
        <h1 className="text-2xl font-bold mb-2">Welcome to triggrHub</h1>
        <p className="text-gray-600">
          Watch a quick overview of how to use the platform
        </p>
      </div>

      <div className="aspect-video bg-gray-100 rounded-lg mb-8 flex items-center justify-center">
        <button className="p-4 bg-emerald-400 rounded-full text-white hover:bg-emerald-300 transition-colors">
          <Play size={32} />
        </button>
      </div>

      <div className="flex gap-4">
        <button
          onClick={onSkip}
          className="flex-1 py-2 px-4 border border-gray-200 text-gray-600 rounded-lg hover:bg-gray-50"
        >
          Skip for now
        </button>
        <button
          onClick={onComplete}
          className="flex-1 py-2 px-4 bg-emerald-400 text-white rounded-lg hover:bg-emerald-300 flex items-center justify-center gap-2"
        >
          Continue to Dashboard
          <ArrowRight size={18} />
        </button>
      </div>
    </div>
  );
};

export default OnboardingVideo;