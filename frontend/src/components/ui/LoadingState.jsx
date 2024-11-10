// frontend/src/components/ui/LoadingState.jsx
import React from 'react';
import { Card, CardContent } from '@/components/ui/card';

const LoadingSpinner = () => (
  <div className="flex items-center justify-center p-4">
    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
  </div>
);

const LoadingCard = ({ lines = 3 }) => (
  <Card>
    <CardContent className="p-4">
      <div className="space-y-3">
        {[...Array(lines)].map((_, i) => (
          <div 
            key={i} 
            className={`h-4 bg-gray-200 rounded animate-pulse ${
              i === 1 ? 'w-3/4' : i === 2 ? 'w-1/2' : 'w-full'
            }`}
          ></div>
        ))}
      </div>
    </CardContent>
  </Card>
);

const LoadingState = ({ type = 'spinner', count = 3, lines = 3 }) => {
  if (type === 'card') {
    return (
      <div className="space-y-4">
        {[...Array(count)].map((_, i) => (
          <LoadingCard key={i} lines={lines} />
        ))}
      </div>
    );
  }

  return <LoadingSpinner />;
};

export { LoadingState, LoadingSpinner, LoadingCard };
