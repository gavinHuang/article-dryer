import React, { useState } from 'react';
import { 
  BookOpen, 
  ChevronDown, 
  ChevronRight, 
  Wand2,
  ArrowUpDown,
  BarChart,
  Loader2
} from 'lucide-react';
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardContent, CardFooter } from "@/components/ui/card";
import { Tabs, TabsContent} from "@/components/ui/tabs";
import { ParagraphComparison } from './ParagraphComparison';
import { InputSelector } from './InputSelector';
import { flushSync } from 'react-dom';

const debug = true;
export const ArticleSummarizer = () => {
  interface Paragraph {
    original: string;
    shortened: string;
    keywords: string[];
    status?: string;
  }
  const [inputType, setInputType] = useState('url');
  const [text, setText] = useState('');
  const [url, setUrl] = useState('');
  const [isAllExpanded, setIsAllExpanded] = useState(false);
  const [processedContent, setProcessedContent] = useState<Paragraph[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleParagraphs = async (paragraphs: string[]) => {
    setIsLoading(true);
    setProcessedContent([]);
    
    try {
      let buffer = '';
      const mergedParagraphs = [];
      let tempParagraph = '';

      for (const paragraph of paragraphs) {
        if ((tempParagraph + paragraph).length < 140) {
          tempParagraph += paragraph + ' ';
        } else {
          if (tempParagraph) {
            mergedParagraphs.push(tempParagraph + paragraph.trim());
            tempParagraph = '';
          }else {
            mergedParagraphs.push(paragraph);
          }
        }
      }

      if (tempParagraph) {
        mergedParagraphs.push(tempParagraph.trim());
      }

      for (const paragraph of mergedParagraphs) {
        if (debug) console.log("sending:", paragraph);
        if (paragraph.trim() === '') continue;
        try {
          const response = await fetch('api/dry', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text: paragraph }),
          });
          
          if (!response.ok || !response.body) {
            throw new Error('Failed to process text');
          }
          const reader = response.body.getReader();
          while (true) {
            const { done, value } = await reader.read();
            if (done)  {
              if (debug) console.log("Done one request!");
              break;
            }
            const decoder = new TextDecoder();
            const chunkStr = decoder.decode(value, { stream: true });
            const lines = chunkStr.trim().split('\n');
            const parsedLines = lines.filter(Boolean).map(line => JSON.parse(line).content);
            const new_chunk = parsedLines.join('');
            if (debug) console.log("received:", new_chunk);

            function update_buffer(new_chunk:string) {
              buffer += new_chunk
              const responed_paragraphs = buffer.split('# Shortened');
              const _processedContent = responed_paragraphs.filter(paragraph => paragraph.trim() !== '').map((paragraph) => {
                const rows = paragraph.split('# Keywords');
                const current_paragraph: Paragraph = {
                  original: paragraph,
                  shortened: "",
                  keywords: [],
                };
                if (rows.length >= 1) {
                  current_paragraph["shortened"] = rows[0].trim();
                }
                if (rows.length == 2) {
                  current_paragraph["keywords"] = rows[1].trim().split('\n').map(line => line.replace(/^[\s-]+/, ''));
                }
                return current_paragraph;
              });
              if (debug) console.log("processedContent:", _processedContent);
              if ( new_chunk.trim().length > 0 ){
                flushSync(() => {
                  setProcessedContent(_processedContent);
                });
                
              }
            }
            update_buffer(new_chunk);
            await new Promise(resolve => setTimeout(resolve, 0));
          }
        } catch (error) {
          console.error('Chunk processing error:', error);
          throw error;
        }
      }
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setIsLoading(false);
    }
  }
  const handleProcessContent = async () => {
    handleParagraphs(text.split('\n\n'));
  };

  const handleProcessUrl = async () => {
    setIsLoading(true);
    try {
      // validate url
      try {
        const urlObj = new URL(url);
        if (!['http:', 'https:'].includes(urlObj.protocol)) {
          throw new Error('URL must use HTTP or HTTPS protocol');
        }
      } catch {
        setIsLoading(false);
        throw new Error('Invalid URL format');
      }
      // send request to https://r.jina.ai/{url}, expect response as plain text:
      const response = await fetch(`https://r.jina.ai/${url}`, {
        headers: {
          'Accept': 'text/plain'
        }
      });
      if (!response.ok) {
        throw new Error('Failed to process URL');
      }
      setProcessedContent([]);
      const data = await response.text();

      const paragraphs = data.split('\n\n').splice(3).filter((paragraph: string) => !paragraph.trim().startsWith('![Image'));

      //skip first 3 paragraphs
      handleParagraphs(paragraphs);
    } catch (error) {
      console.error('Error:', error);
    }
  };

  const dryIt = async () => {
    if (inputType === 'text') {
      handleProcessContent();
    }
    if (inputType === 'url') {  
      handleProcessUrl();
    }
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
              className={`w-full p-3 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary transition-all duration-300 ${isLoading ? 'h-12' : 'h-48'}`}
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
            onClick={dryIt}
            disabled={isLoading}
          >
            {isLoading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Wand2 className="w-4 h-4" />
            )}
            <span>{isLoading ? 'Processing...' : 'Dry It!'}</span>
          </Button>
        </CardFooter>
      </Card>

      <Tabs defaultValue="summary" className="w-full">
       

        <TabsContent value="summary">
            <Card className={`bg-white shadow-lg ${processedContent.length === 0 ? 'hidden' : ''}`}>
            <CardHeader className="border-b">
              <div className="flex justify-between items-center">
                <div className="space-y-1" >
                  <div className="flex items-center justify-between">
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
                  {Math.round((processedContent.reduce((acc, p) => acc + p.shortened.length, 0) / 
                             processedContent.reduce((acc, p) => acc + p.original.length, 0)) * 100)}% of original
                </div>
              </div>
            </CardHeader>
            <CardContent className="p-4">
              <div className="divide-y">
                {processedContent.map((paragraph, index) => (
                  <ParagraphComparison 
                    key={index}
                    dried={paragraph.shortened}
                    original={paragraph.original}
                    isAllExpanded={isAllExpanded}
                    keywords={paragraph.keywords}
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