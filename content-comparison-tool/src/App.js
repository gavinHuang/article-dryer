import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardContent, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { BookOpen, Wand2, ArrowUpDown, BarChart, ChevronDown, ChevronRight, Link, Type } from 'lucide-react';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';

const ParagraphComparison = ({ dried, original, isAllExpanded }) => {
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

const InputSelector = ({ activeInput, onInputChange }) => {
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

const ArticleSummarizer = () => {
  const [inputType, setInputType] = useState('text');
  const [text, setText] = useState('');
  const [url, setUrl] = useState('');
  const [isAllExpanded, setIsAllExpanded] = useState(false);
  const [processedContent, setProcessedContent] = useState([
    {
      dried: "The '10x engineer' concept suggests some engineers have 10 times the impact of average ones.",
      original: "The '10x engineer' concept suggests some engineers have 10 times the impact of average ones. This idea may extend to other professions as AI advances, creating more '10x professionals.'"
    },
    {
      dried: "Physical limits create performance ceilings in many roles.",
      original: "The gap between the best and average workers has a ceiling in many roles due to physical limits. For example, a supermarket clerk can't scan groceries 10x faster, and a doctor can't heal patients 10x quicker."
    }
  ]);

  const handleProcessContent = () => {
    // Add processing logic here
  };

  return (
    <div className="max-w-6xl mx-auto p-4 space-y-6">
      <div className="flex items-center space-x-2 mb-6">
        <BookOpen className="w-6 h-6 text-primary" />
        <h1 className="text-2xl font-bold">Article Dryer</h1>
      </div>

      <Card className="bg-white shadow-lg">
        <CardHeader className="border-b">
          <div className="flex justify-between items-center">
            <h2 className="text-lg font-semibold">Original Text</h2>
            <div className="text-sm text-gray-500">
              {inputType === 'text' ? `${text.length} characters` : 'URL input'}
            </div>
          </div>
        </CardHeader>
        <CardContent className="p-4">
          <InputSelector 
            activeInput={inputType} 
            onInputChange={setInputType}
          />
          
          {inputType === 'text' ? (
            <textarea
              className="w-full h-48 p-3 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
              placeholder="Paste your article here..."
              value={text}
              onChange={(e) => setText(e.target.value)}
            />
          ) : (
            <div className="space-y-4">
              <input
                type="url"
                className="w-full p-3 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="Enter article URL (e.g., https://example.com/article)"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
              />
              <div className="text-sm text-gray-500">
                Supported sources:
                <ul className="list-disc ml-5 mt-1">
                  <li>Medium articles</li>
                  <li>News websites</li>
                  <li>Blog posts</li>
                  <li>Documentation pages</li>
                </ul>
              </div>
            </div>
          )}
        </CardContent>
        <CardFooter className="border-t bg-gray-50 p-4">
          <Button 
            className="flex items-center space-x-2 bg-primary hover:bg-primary/90"
            onClick={handleProcessContent}
          >
            <Wand2 className="w-4 h-4" />
            <span>Dry It!</span>
          </Button>
        </CardFooter>
      </Card>

      <Tabs defaultValue="summary" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="summary">Dried Content</TabsTrigger>
          <TabsTrigger value="analysis">Analysis</TabsTrigger>
        </TabsList>

        <TabsContent value="summary">
          <Card className="bg-white shadow-lg">
            <CardHeader className="border-b">
              <div className="flex justify-between items-center">
                <div className="space-y-1">
                  <div className="flex items-center justify-between">
                    <h2 className="text-lg font-semibold">Dried Version</h2>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setIsAllExpanded(!isAllExpanded)}
                      className="flex items-center space-x-1 text-gray-600 hover:text-gray-900"
                    >
                      {isAllExpanded ? (
                        <>
                          <ChevronDown className="w-4 h-4" />
                          <span>Collapse All</span>
                        </>
                      ) : (
                        <>
                          <ChevronRight className="w-4 h-4" />
                          <span>Expand All</span>
                        </>
                      )}
                    </Button>
                  </div>
                  <p className="text-sm text-gray-500">Click on any paragraph to see the original text</p>
                </div>
                <div className="text-sm text-gray-500">
                  {Math.round((processedContent.reduce((acc, p) => acc + p.dried.length, 0) / 
                             processedContent.reduce((acc, p) => acc + p.original.length, 0)) * 100)}% of original
                </div>
              </div>
            </CardHeader>
            <CardContent className="p-4">
              <div className="divide-y">
                {processedContent.map((paragraph, index) => (
                  <ParagraphComparison 
                    key={index}
                    dried={paragraph.dried}
                    original={paragraph.original}
                    isAllExpanded={isAllExpanded}
                  />
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="analysis">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card className="bg-white shadow-lg">
              <CardHeader className="border-b">
                <div className="flex items-center space-x-2">
                  <ArrowUpDown className="w-4 h-4" />
                  <h2 className="text-lg font-semibold">Performance Gap Analysis</h2>
                </div>
              </CardHeader>
              <CardContent className="p-4">
                <div className="space-y-4">
                  <div className="border-l-4 border-blue-500 pl-4">
                    <h3 className="font-medium mb-2">Current Limitations</h3>
                    <p className="text-gray-600">Physical and practical limits create performance ceilings in many roles:</p>
                    <ul className="list-disc ml-4 mt-2 text-gray-600">
                      <li>Supermarket clerks: Physical scanning speed limits</li>
                      <li>Medical procedures: Human biological healing rates</li>
                      <li>Customer service: Natural conversation pacing</li>
                    </ul>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-white shadow-lg">
              <CardHeader className="border-b">
                <div className="flex items-center space-x-2">
                  <BarChart className="w-4 h-4" />
                  <h2 className="text-lg font-semibold">AI Impact Potential</h2>
                </div>
              </CardHeader>
              <CardContent className="p-4">
                <div className="space-y-4">
                  <div className="border-l-4 border-green-500 pl-4">
                    <h3 className="font-medium mb-2">Growth Opportunities</h3>
                    <p className="text-gray-600">AI augmentation can create new "10x professionals" across industries:</p>
                    <ul className="list-disc ml-4 mt-2 text-gray-600">
                      <li>Software Engineering: Enhanced coding capabilities</li>
                      <li>Data Analysis: Faster pattern recognition</li>
                      <li>Content Creation: Accelerated production</li>
                    </ul>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default ArticleSummarizer;