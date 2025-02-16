import React from 'react';
import { Button } from '@/components/ui/button';
import { Copy, ArrowDownToLine } from 'lucide-react';

interface ToolbarProps {
  onCopy: () => void;
  onExport: () => void;
  isCopied: boolean;
}

export const Toolbar: React.FC<ToolbarProps> = ({ onCopy, onExport, isCopied }) => {
  return (
    <div className="flex gap-2">
      <Button
        variant="outline"
        size="sm"
        className="text-gray-600"
        onClick={onCopy}
      >
        <Copy className="w-4 h-4 mr-2" />
        {isCopied ? 'Copied!' : 'Copy'}
      </Button>
      <Button
        variant="outline"
        size="sm"
        className="text-gray-600"
        onClick={onExport}
      >
        <ArrowDownToLine className="w-4 h-4 mr-2" />
        Export
      </Button>
    </div>
  );
};