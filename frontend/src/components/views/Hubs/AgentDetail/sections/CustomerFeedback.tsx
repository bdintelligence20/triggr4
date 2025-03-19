import React from 'react';

interface FeedbackEntry {
  id: number;
  message: string;
  sentiment: 'positive' | 'neutral' | 'negative';
  date: string;
}

const demoFeedback: FeedbackEntry[] = [
  {
    id: 1,
    message: 'Great customer support, very helpful!',
    sentiment: 'positive',
    date: '2h ago'
  },
  {
    id: 2,
    message: 'Service was okay, but could be faster',
    sentiment: 'neutral',
    date: '3h ago'
  },
  {
    id: 3,
    message: 'Had issues with delivery timing',
    sentiment: 'negative',
    date: '4h ago'
  },
  {
    id: 4,
    message: 'Very professional and efficient service',
    sentiment: 'positive',
    date: '5h ago'
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
    <div className="bg-white rounded-lg shadow-sm h-full">
      <div className="px-5 py-4 border-b border-gray-100">
        <h2 className="text-base font-semibold text-gray-900">Customer Feedback</h2>
      </div>
      
      <div className="divide-y divide-gray-100 max-h-[320px] overflow-y-auto">
        {demoFeedback.map(feedback => (
          <div key={feedback.id} className="px-5 py-4 hover:bg-gray-50 transition-colors">
            <div className="flex items-start gap-3">
              <span className={`px-2 py-1 text-xs font-medium rounded-full whitespace-nowrap ${getSentimentStyles(feedback.sentiment)}`}>
                {feedback.sentiment}
              </span>
              <div className="flex-1 min-w-0">
                <p className="text-sm text-gray-700 leading-relaxed">{feedback.message}</p>
                <span className="text-xs text-gray-500 mt-1 block">{feedback.date}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default CustomerFeedback;