import React, { useState, useEffect } from 'react';
import { ChevronDown, ChevronRight } from 'lucide-react';

interface ParagraphComparisonProps {
  dried: string;
  original: string;
  isAllExpanded: boolean;
}

export const ParagraphComparison: React.FC<ParagraphComparisonProps> = ({ 
  dried, 
  original, 
  isAllExpanded 
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  
  useEffect(() => {
    setIsExpanded(isAllExpanded);
  }, [isAllExpanded]);

  return (
    <div className="border-b last:border-b-0 py-3">
      <div 
        className="flex items-start cursor-pointer group"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        {isExpanded ? (
          <ChevronDown className="w-4 h-4 mt-1 mr-2 flex-shrink-0" />
        ) : (
          <ChevronRight className="w-4 h-4 mt-1 mr-2 flex-shrink-0" />
        )}
        <div className="flex-grow">
          <p className="text-gray-800">{dried}</p>
          {isExpanded && (
            <div className="mt-3 pl-4 border-l-2 border-gray-200">
              <p className="text-gray-600 text-sm">{original}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};