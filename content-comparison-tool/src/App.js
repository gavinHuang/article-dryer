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
      // split inputtext into paragraphs
      const paragraphs = inputText.split('\n\n');
      // send 3 pragraph everytime:
      const chunks = [];
      for (let i = 0; i < paragraphs.length; i += 3) {
        chunks.push(paragraphs.slice(i, i + 3).join('\n\n'));
      }
      for (const chunk of chunks) {
        // send each chunk to the API
        // Handle streaming response
        let buffer = '';
        const response = await fetch(process.env.REACT_APP_API_BASE_URL+'/dry', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ text: chunk }),
        });
        if (!response.ok) {
          throw new Error('Failed to process text');
        }
        const reader = response.body.getReader();
        processResponseChunk(reader, buffer);
      }
      // setShowComparison(true);
      // processResponseChunk();
    } catch (error) {
      console.error('Error:', error);
      setError(error);
    } finally {
      setIsLoading(false);
    }
  };

  async function processResponseChunk(reader, buffer) {
    const { done, value } = await reader.read();
    if (done) {
      console.log('Stream ended:' + value);
      setShowComparison(true); // Final update
      return;
    }
    // Decode the stream chunk
    const decoder = new TextDecoder();
    const chunk = decoder.decode(value, { stream: true });
    if (chunk.trim() == '') {
      processResponseChunk(reader, buffer);
      return;
    }
    const lines = chunk.trim().split('\n');
    // extract the value from "content" section in the response json
    // filter out empty lines:
    const parsedLines = lines.filter(Boolean).map(line => JSON.parse(line).content);
    let content = '';
    content = parsedLines.join('');
    buffer += content;
    if (buffer.indexOf('}') === -1) {
      console.log('Received object:', content);
      processResponseChunk(reader, buffer);
      return;
    }
    console.log('current buffer:'+buffer);
    setShowComparison(true);
    const content_lines = buffer.split('\n').filter(Boolean);
    buffer = '';
    for (const line of content_lines) {
      console.log('Received JSON object:', line);
      try {
        const parsedResponse = JSON.parse(line);
        setContent((prevContent) => [...prevContent, parsedResponse]);
        setTimeout(processResponseChunk(reader, buffer), 0);
      } catch (error) {
        console.error('Error parsing JSON:', error);
        console.error('Means its still not a whole response yet');
        buffer += line;
      }
    }
  }
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