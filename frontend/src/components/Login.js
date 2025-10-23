/**
 * Login component for Okta authentication.
 */
import React, { useEffect } from 'react';
import { useOktaAuth } from '@okta/okta-react';
import { useNavigate } from 'react-router-dom';
import './Login.css';

function Login() {
  const { oktaAuth, authState } = useOktaAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (authState?.isAuthenticated) {
      navigate('/');
    }
  }, [authState, navigate]);

  const handleLogin = async () => {
    await oktaAuth.signInWithRedirect();
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <h1>Design Assistant</h1>
        <p>Your AI-powered design system companion</p>
        <button onClick={handleLogin} className="login-button">
          Sign in with Okta
        </button>
      </div>
    </div>
  );
}

export default Login;

