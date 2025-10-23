/**
 * Minimal App component for testing.
 */
import React from 'react';
import './App.css';

function App() {
  return (
    <div className="App">
      <div className="main-container">
        <header className="app-header">
          <div className="header-title">
            <h1>Design & Research Assistant</h1>
          </div>
        </header>
        <main className="app-main">
          <div style={{ padding: '20px', textAlign: 'center' }}>
            <h2>Welcome to the Design & Research Assistant</h2>
            <p>This is a simplified version for testing deployment.</p>
          </div>
        </main>
      </div>
    </div>
  );
}

export default App;

