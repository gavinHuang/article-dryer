import React, { useState, useEffect } from 'react';
import { ChevronDown, ChevronRight } from 'lucide-react';

interface ParagraphComparisonProps {
  dried: string;
  original: string;
  isAllExpanded: boolean;
  keywords?: string[]; // Add keywords prop
}

export const ParagraphComparison: React.FC<ParagraphComparisonProps> = ({ 
  dried, 
  original, 
  isAllExpanded,
  keywords = [] // Default to empty array if not provided
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  
  useEffect(() => {
    setIsExpanded(isAllExpanded);
  }, [isAllExpanded]);

  const highlightKeywords = (text: string) => {
    if (keywords.length === 0) return text;

    // Create a regex pattern from provided keywords
    const pattern = new RegExp(`(${keywords.join('|')})`, 'gi');

    // Split the text by keywords and wrap matches in highlight spans
    const parts = text.split(pattern);
    return parts.map((part, i) => {
      if (keywords.includes(part.toLowerCase())) {
        return <span key={i} className="bg-yellow-100 px-1 rounded">{part}</span>;
      }
      return part;
    });
  };

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
              <p className="text-gray-600 text-sm">{highlightKeywords(original)}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};