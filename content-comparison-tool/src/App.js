import React, { useState, useEffect } from 'react';
import './App.css';
import { flushSync } from 'react-dom';


const App = () => {
  const [inputText, setInputText] = useState('');
  const [showComparison, setShowComparison] = useState(false);
  const [content, setContent] = useState([]);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  
  // // Custom hook to use flushSync
  // const useFlushSync = () => {
  //   const root = React.useRef(null);
  //   React.useEffect(() => {
  //     root.current = document.querySelector('#root');
  //   }, []);
  //   return () => {
  //     if (root.current) {
  //       // Flush state updates synchronously
  //       Object.assign(root.current, root.current);
  //     }
  //   };
  // };

  // useEffect(() => {
  //   if (showComparison && content.length > 0) {
  //     // Your rendering logic here
  //     console.log('Content updated:', content);
  //   }
  // }, [content, showComparison]);

  const handleDryIt = async () => {
    setIsLoading(true);
    setError(null);
    setContent([]);
    setShowComparison(false);
    try {
      // Split input text into paragraphs
      const paragraphs = inputText.split('\n\n');
      // // Send 3 paragraphs at a time:
      // const chunks = [];
      // for (let i = 0; i < paragraphs.length; i += 3) {
      //   chunks.push(paragraphs.slice(i, i + 3).join('\n\n'));
      // }
      for (const paragraph of paragraphs) {
        // Send each chunk to the API
        try {
          const response = await fetch(process.env.REACT_APP_API_BASE_URL + '/dry', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text: paragraph }),
          });
          
          if (!response.ok) {
            throw new Error('Failed to process text');
          }
          
          const reader = response.body.getReader();
          let buffer = '';
          let content = '';
          
          while (true) {
            const { done, value } = await reader.read();
            if (done) {
              console.log("Processing:" + buffer);
              try {
                const lines = buffer.split('\n');
                for (const line of lines) {
                  if (line.trim() !== '') {
                    const data = JSON.parse(line);
                    data["original"] = paragraph;
                    console.log("response: " + data);
                    // Force the UI to update immediately
                    flushSync(() => {
                      setContent((prev) => [...prev, data]);
                      setShowComparison(true);
                    });
                  }
                }
                
              } catch (e) {
                console.error('Error parsing JSON:', e);
              }
              break;
            }
            const decoder = new TextDecoder();
            const chunkStr = decoder.decode(value, { stream: true });
            const lines = chunkStr.trim().split('\n');
            const parsedLines = lines.filter(Boolean).map(line => JSON.parse(line).content);
            content = parsedLines.join('');
            buffer += content;
            console.log("Receiving:" + content);
            
            // // Process the buffer when we have newline characters
            // if (buffer.includes('\n')) {
              
            //   }
            //   // Keep the last line in the buffer for potential next iteration
            //   buffer = lines[lines.length - 1] || '';
            // }

            // Add a small delay to prevent blocking
            await new Promise(resolve => setTimeout(resolve, 0));
          }
        } catch (error) {
          console.error('Chunk processing error:', error);
          throw error;
        }
      }
      setShowComparison(true);
    } catch (error) {
      console.error('Error:', error);
      setError(error.message);
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
      {error && <div className="error">Error: {error}</div>}

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