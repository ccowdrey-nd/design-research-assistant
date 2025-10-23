/**
 * Chat interface component.
 */
import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import apiClient from '../api';
import './ChatWindow.css';

function ChatWindow() {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleExampleClick = (question) => {
    setInputValue(question);
    // Auto-send the message
    setTimeout(() => {
      handleSendMessage(question);
    }, 100);
  };

  const handleSendMessage = async (messageText = null) => {
    const message = messageText || inputValue;
    if (!message.trim() || isLoading) return;

    const userMessage = {
      role: 'user',
      content: message,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      // Build conversation history
      const history = messages.map((msg) => ({
        role: msg.role,
        content: msg.content,
      }));

      // Send message to API
      const response = await apiClient.sendMessage(message, history);

      const assistantMessage = {
        role: 'assistant',
        content: response.response,
        sources: response.sources || [],
        exportData: response.export_data || null,
        exampleImages: response.example_images || null,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString(),
        isError: true,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleDownloadExport = async (exportData, messageIndex) => {
    // Set downloading state for this message
    setMessages((prev) =>
      prev.map((msg, idx) =>
        idx === messageIndex ? { ...msg, isDownloading: true } : msg
      )
    );

    try {
      const response = await fetch('http://localhost:8000/api/export/figma', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(exportData),
      });

      if (!response.ok) {
        throw new Error('Export failed');
      }

      // Download the file
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      const filename = exportData.node_name.toLowerCase().replace(/[^a-z0-9-]/g, '-');
      a.download = `${filename}.svg`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);

      // Show success state
      setMessages((prev) =>
        prev.map((msg, idx) =>
          idx === messageIndex ? { ...msg, isDownloading: false, downloadComplete: true } : msg
        )
      );
    } catch (error) {
      console.error('Export error:', error);
      alert('Failed to export asset. Please try again.');
      
      // Clear downloading state
      setMessages((prev) =>
        prev.map((msg, idx) =>
          idx === messageIndex ? { ...msg, isDownloading: false } : msg
        )
      );
    }
  };

  return (
    <div className="chat-window">
      <div className="messages-container">
        {messages.length === 0 && (
          <div className="welcome-message">
            <h2>Welcome!</h2>
            <p>Ask me anything about our design system, components, or brand guidelines.</p>
            <div className="example-questions">
              <p><strong>Try asking:</strong></p>
              <div className="example-buttons">
                <button 
                  className="example-btn" 
                  onClick={() => handleExampleClick("What are our brand colors?")}
                >
                  What are our brand colors?
                </button>
                <button 
                  className="example-btn" 
                  onClick={() => handleExampleClick("Show me button components")}
                >
                  Show me button components
                </button>
                <button 
                  className="example-btn" 
                  onClick={() => handleExampleClick("What's our typography system?")}
                >
                  What's our typography system?
                </button>
                <button 
                  className="example-btn" 
                  onClick={() => handleExampleClick("How should I use our logo?")}
                >
                  How should I use our logo?
                </button>
              </div>
            </div>
          </div>
        )}

        {messages.map((message, index) => (
          <div key={index} className={`message ${message.role}`}>
            <div className="message-content">
              <ReactMarkdown
                components={{
                  a: ({ node, ...props }) => (
                    <a {...props} target="_blank" rel="noopener noreferrer" />
                  ),
                }}
              >
                {message.content}
              </ReactMarkdown>
            </div>
            {message.exampleImages && message.exampleImages.length > 0 && (
              <div className="message-examples">
                <strong>Visual Examples:</strong>
                <div className="example-images">
                  {message.exampleImages.map((imageUrl, idx) => (
                    <img
                      key={idx}
                      src={imageUrl}
                      alt={`Example ${idx + 1}`}
                      className="example-image"
                    />
                  ))}
                </div>
              </div>
            )}
            {message.exportData && (
              <div className="message-export">
                <button
                  className="download-btn"
                  onClick={() => handleDownloadExport(message.exportData, index)}
                  disabled={message.isDownloading}
                >
                  {message.isDownloading ? (
                    <>
                      <span className="spinner"></span>
                      Exporting...
                    </>
                  ) : message.downloadComplete ? (
                    <>✅ Downloaded!</>
                  ) : (
                    <>
                      📥 Download {message.exportData.node_name.includes('logo') ? 'Logo' : 'Asset'} SVG
                      {message.exportData.color && ` (${message.exportData.color})`}
                    </>
                  )}
                </button>
              </div>
            )}
            {message.sources && message.sources.length > 0 && (
              <div className="message-sources">
                <strong>Sources:</strong>
                <ul>
                  {message.sources.map((source, idx) => (
                    <li key={idx}>
                      <a href={source.url} target="_blank" rel="noopener noreferrer">
                        {source.name} ({source.type})
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            <div className="message-timestamp">
              {new Date(message.timestamp).toLocaleTimeString()}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="message assistant">
            <div className="message-content typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="input-container">
        <textarea
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask about the design system or request asset exports..."
          rows="3"
          disabled={isLoading}
        />
        <button onClick={handleSendMessage} disabled={isLoading || !inputValue.trim()}>
          Send
        </button>
      </div>
    </div>
  );
}

export default ChatWindow;

