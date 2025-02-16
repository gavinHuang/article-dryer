import React from 'react';
import { Card, CardContent } from '@/components/ui/card';

interface Summary {
  keyPoints: string[];
  limitations: string[];
}

interface SummaryOutputProps {
  summary: Summary;
}

export const SummaryOutput: React.FC<SummaryOutputProps> = ({ summary }) => {
  return (
    <Card>
      <CardContent className="p-4 space-y-4">
        <div className="p-3 border-l-4 border-emerald-500 bg-emerald-50">
          <h3 className="font-semibold text-gray-800">Key Points</h3>
          {summary.keyPoints.map((point, index) => (
            <p key={index} className="text-gray-600 mt-1">
              {point}
            </p>
          ))}
        </div>
        
        <div className="p-3 border-l-4 border-blue-500 bg-blue-50">
          <h3 className="font-semibold text-gray-800">Limitations</h3>
          {summary.limitations.map((limitation, index) => (
            <p key={index} className="text-gray-600 mt-1">
              {limitation}
            </p>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};