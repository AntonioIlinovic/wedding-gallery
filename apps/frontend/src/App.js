import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [backendStatus, setBackendStatus] = useState('checking...');

  useEffect(() => {
    // Check backend health (proxy will forward to backend service)
    fetch('/api/health/')
      .then(response => response.json())
      .then(data => {
        setBackendStatus(data.status === 'ok' ? 'connected' : 'error');
      })
      .catch(error => {
        console.error('Error connecting to backend:', error);
        setBackendStatus('disconnected');
      });
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <h1>Wedding Gallery</h1>
        <p>Backend Status: <strong>{backendStatus}</strong></p>
        <p>Welcome to the wedding gallery application!</p>
      </header>
    </div>
  );
}

export default App;

