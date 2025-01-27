import React, { useState } from 'react';
import './App.css';

const App = () => {
  const [inputText, setInputText] = useState('');
  const [showComparison, setShowComparison] = useState(false);
  const [content, setContent] = useState([]);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  
  const handleDryIt = async () => {
    setIsLoading(true);
    setError(null);
    setContent([]);
    try {
      const response = await fetch(process.env.REACT_APP_API_BASE_URL+'/dry', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: inputText }),
      });
  
      if (!response.ok) {
        throw new Error('Failed to process text');
      }
      // Handle streaming response
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      while (true) {
        await new Promise((resolve) => setTimeout(resolve, 0));
        const { done, value } = await reader.read();
        if (done) break;
  
        // Decode the stream chunk
        const chunk = decoder.decode(value, { stream: true });
        if (chunk.trim() == '') {
          continue;
        }
        const lines = chunk.trim().split('\n');
        // filter out empty lines:
        const parsedLines = lines.filter(Boolean).map(line => JSON.parse(line).content);
        let content = '';    
        content = parsedLines.join('');
        if (content.trim().at(-1) != '}') {
            buffer += content;
            continue
        }
        // check if content is ready to be parsed as json:
        content = buffer + content
        const content_lines = content.split('\n').filter(Boolean);
        for (const line of content_lines) {
          console.log('Received JSON object:', line);
          const parsedResponse = JSON.parse(line);
          setContent((prevContent) => [...prevContent, parsedResponse]);
          await new Promise((resolve) => setTimeout(resolve, 0));
        }
        setShowComparison(true);
        buffer = '';
      }
      setShowComparison(true);
    } catch (error) {
      console.error('Error:', error);
      setError(error);
    } finally {
      setIsLoading(false);
    }
  };

 
  return (
    <div className="App">
      <h1>Article Dryer</h1>
      <div className="input-section">
        <textarea
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="Paste your original content here..."
          rows="10"
        />
        <button onClick={handleDryIt} className="dry-button">
          Dry It!
        </button>
      </div>
      {isLoading && <div className="loading">Processing your text...</div>}
      {error && <div className="error">Error: {error.message}</div>}


      {showComparison && (
        <div className="comparison-container">
          {content.map((item, index) => (
            <ComparisonRow
              key={index}
              original={item.original}
              shortened={item.shortened}
              keywords={item.keywords}
            />
          ))}
        </div>
      )}
    </div>
  );
};

// Keep the HighlightedText and ComparisonRow components from previous code
const HighlightedText = ({ text, keywords }) => {
  const regex = new RegExp(`(${keywords.map(k => k.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|')})`, 'gi');
  
  const parts = text.split(regex).filter(Boolean);

  return (
    <p>
      {parts.map((part, index) => {
        const match = keywords.find(k => k.toLowerCase() === part.toLowerCase());
        return match ? (
          <mark key={index} className="highlight">
            {part}
          </mark>
        ) : (
          <span key={index}>{part}</span>
        );
      })}
    </p>
  );
};

// In the ComparisonRow component, swap the div order
const ComparisonRow = ({ original, shortened, keywords }) => {
  return (
    <div className="comparison-row">
      <div className="shortened">
        <p>{shortened}</p>
      </div>
      <div className="original">
        <HighlightedText text={original} keywords={keywords} />
      </div>
    </div>
  );
};

export default App;