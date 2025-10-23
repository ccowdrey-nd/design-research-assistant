/**
 * Main App component with Okta authentication.
 */
import React, { useState } from 'react';
import { Security, LoginCallback, SecureRoute } from '@okta/okta-react';
import { OktaAuth, toRelativeUrl } from '@okta/okta-auth-js';
import { useNavigate, Route, Routes, BrowserRouter } from 'react-router-dom';
import ChatWindow from './components/ChatWindow';
import ImageAnalyzer from './components/ImageAnalyzer';
import AdminPanel from './components/AdminPanel';
import Login from './components/Login';
import './App.css';

const oktaAuth = new OktaAuth({
  issuer: process.env.REACT_APP_OKTA_ISSUER,
  clientId: process.env.REACT_APP_OKTA_CLIENT_ID,
  redirectUri: window.location.origin + '/login/callback',
  scopes: ['openid', 'profile', 'email'],
});

function App() {
  const navigate = useNavigate();

  const restoreOriginalUri = async (_oktaAuth, originalUri) => {
    navigate(toRelativeUrl(originalUri || '/', window.location.origin));
  };

  return (
    <Security oktaAuth={oktaAuth} restoreOriginalUri={restoreOriginalUri}>
      <div className="App">
        <Routes>
          <Route path="/login/callback" element={<LoginCallback />} />
          <Route path="/login" element={<Login />} />
          <Route path="/" element={<SecureRoute />}>
            <Route path="/" element={<MainApp />} />
          </Route>
        </Routes>
      </div>
    </Security>
  );
}

function MainApp() {
  const [mode, setMode] = useState('chat'); // 'chat' or 'analyze'

  return (
    <div className="main-container">
      <header className="app-header">
        <div className="header-title">
          <img src="/nextdoor-logo.svg" alt="Nextdoor" className="header-logo" />
          <h1>Design & Research Assistant</h1>
        </div>
        <nav className="mode-toggle">
          <button
            className={mode === 'chat' ? 'active' : ''}
            onClick={() => setMode('chat')}
          >
            Chat
          </button>
          <button
            className={mode === 'analyze' ? 'active' : ''}
            onClick={() => setMode('analyze')}
          >
            Image Analysis
          </button>
          <button
            className={mode === 'admin' ? 'active' : ''}
            onClick={() => setMode('admin')}
          >
            Admin
          </button>
        </nav>
      </header>

      <main className="app-main">
        {mode === 'chat' && <ChatWindow />}
        {mode === 'analyze' && <ImageAnalyzer />}
        {mode === 'admin' && <AdminPanel />}
      </main>
    </div>
  );
}

function AppWithRouter() {
  return (
    <BrowserRouter>
      <App />
    </BrowserRouter>
  );
}

export default AppWithRouter;

