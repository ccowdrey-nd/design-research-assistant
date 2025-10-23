/**
 * Simplified App without Okta - for development/internal use
 */
import React, { useState } from 'react';
import ChatWindow from './components/ChatWindow';
import ImageAnalyzer from './components/ImageAnalyzer';
import AdminPanel from './components/AdminPanel';
import './App.css';

function SimpleApp() {
  const [mode, setMode] = useState('chat'); // 'chat' or 'analyze' or 'admin'

  return (
    <div className="App">
      <div className="main-container">
        <header className="app-header">
          <div className="header-branding">
            <img src="/nextdoor-logo.svg" alt="Nextdoor" className="nextdoor-logo" />
            <span className="assistant-label">Design & Research Assistant</span>
          </div>
          <nav className="mode-toggle">
            <button
              className={mode === 'chat' ? 'active' : ''}
              onClick={() => setMode('chat')}
            >
              💬 Chat
            </button>
            <button
              className={mode === 'analyze' ? 'active' : ''}
              onClick={() => setMode('analyze')}
            >
              🖼️ Image Analysis
            </button>
            <button
              className={mode === 'admin' ? 'active' : ''}
              onClick={() => setMode('admin')}
            >
              ⚙️ Admin
            </button>
          </nav>
        </header>

        <main className="app-main">
          {mode === 'chat' && <ChatWindow />}
          {mode === 'analyze' && <ImageAnalyzer />}
          {mode === 'admin' && <AdminPanel />}
        </main>
      </div>
    </div>
  );
}

export default SimpleApp;

