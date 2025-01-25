import React, { useState } from 'react';
import './App.css';

const App = () => {
  const [inputText, setInputText] = useState('');
  const [showComparison, setShowComparison] = useState(false);
  const [content, setContent] = useState([]);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  // Add this before the return statement
  if (error) {
    return ;
  }
  
  const handleDryIt = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch('http://localhost:5000/api/dry', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: inputText }),
      });
  
      if (!response.ok) {
        throw new Error('Failed to process text');
      }
  
      const data = await response.json();
      setContent(data.processedContent);
      setShowComparison(true);
    } catch (error) {
      setError(error);
    } finally {
      setIsLoading(false);
    }
  };

 
  return (
    <div className="App">
      <h1>Content Dryer</h1>
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