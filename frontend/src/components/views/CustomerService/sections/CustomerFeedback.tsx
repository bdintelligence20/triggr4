import React from 'react';

interface FeedbackEntry {
  id: number;
  message: string;
  sentiment: 'positive' | 'neutral' | 'negative';
  time: string;
}

const demoFeedback: FeedbackEntry[] = [
  {
    id: 1,
    message: 'Great customer support, very helpful!',
    sentiment: 'positive',
    time: '2h ago'
  },
  {
    id: 2,
    message: 'Service was okay, but could be faster',
    sentiment: 'neutral',
    time: '3h ago'
  },
  {
    id: 3,
    message: 'Had issues with delivery timing',
    sentiment: 'negative',
    time: '4h ago'
  },
  {
    id: 4,
    message: 'Very professional and efficient service',
    sentiment: 'positive',
    time: '5h ago'
  }
];

const CustomerFeedback = () => {
  const getSentimentStyles = (sentiment: string) => {
    switch (sentiment) {
      case 'positive':
        return 'bg-green-50 text-green-600';
      case 'neutral':
        return 'bg-yellow-50 text-yellow-600';
      case 'negative':
        return 'bg-red-50 text-red-600';
      default:
        return 'bg-gray-50 text-gray-600';
    }
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {/* Feedback List */}
      <div className="bg-white rounded-xl shadow-sm">
        <div className="px-6 py-4 border-b border-gray-100">
          <h2 className="text-lg font-semibold text-gray-900">Customer Feedback</h2>
        </div>
        
        <div className="divide-y divide-gray-100">
          {demoFeedback.map(feedback => (
            <div key={feedback.id} className="px-6 py-4 hover:bg-gray-50 transition-colors">
              <div className="flex items-start gap-3">
                <span className={`px-2.5 py-1 text-xs font-medium rounded-full whitespace-nowrap ${getSentimentStyles(feedback.sentiment)}`}>
                  {feedback.sentiment}
                </span>
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-gray-700 leading-relaxed">{feedback.message}</p>
                  <span className="text-xs text-gray-500 mt-1 block">{feedback.time}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* CSAT Scores */}
      <div className="bg-white rounded-xl shadow-sm">
        <div className="px-6 py-4 border-b border-gray-100">
          <h2 className="text-lg font-semibold text-gray-900">CSAT Scores</h2>
        </div>
        <div className="p-6 space-y-8">
          <div>
            <div className="flex justify-between items-center mb-3">
              <span className="text-sm text-gray-500">Today</span>
              <span className="text-2xl font-bold text-emerald-400">78%</span>
            </div>
            <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
              <div 
                className="h-full bg-emerald-400 rounded-full transition-all duration-500"
                style={{ width: '78%' }}
              />
            </div>
          </div>

          <div>
            <div className="flex justify-between items-center mb-3">
              <span className="text-sm text-gray-500">Average</span>
              <span className="text-2xl font-bold text-emerald-400">68%</span>
            </div>
            <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
              <div 
                className="h-full bg-emerald-400 rounded-full transition-all duration-500"
                style={{ width: '68%' }}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CustomerFeedback;