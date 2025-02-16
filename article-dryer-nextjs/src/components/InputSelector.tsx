import React from 'react';
import { Type, Link } from 'lucide-react';
import { Button } from "@/components/ui/button";

interface InputSelectorProps {
  activeInput: string;
  onInputChange: (type: string) => void;
}

export const InputSelector: React.FC<InputSelectorProps> = ({ 
  activeInput, 
  onInputChange 
}) => {
  return (
    <div className="flex space-x-2 mb-4">
      <Button
        variant={activeInput === 'text' ? 'default' : 'outline'}
        className="flex items-center space-x-2"
        onClick={() => onInputChange('text')}
      >
        <Type className="w-4 h-4" />
        <span>Paste Text</span>
      </Button>
      <Button
        variant={activeInput === 'url' ? 'default' : 'outline'}
        className="flex items-center space-x-2"
        onClick={() => onInputChange('url')}
      >
        <Link className="w-4 h-4" />
        <span>Enter URL</span>
      </Button>
    </div>
  );
};