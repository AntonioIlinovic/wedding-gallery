import React, { useState, useEffect } from 'react';
import WelcomePage from './components/WelcomePage';
import PhotoUpload from './components/PhotoUpload';
import Gallery from './components/Gallery';
import { validateToken } from './api';
import './App.css';

function App() {
  const [view, setView] = useState('welcome');
  const [accessToken, setAccessToken] = useState(null);
  const [event, setEvent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const checkToken = async () => {
      const params = new URLSearchParams(window.location.search);
      const token = params.get('token');

      if (token) {
        try {
          const response = await validateToken(token);
          if (response.valid) {
            setAccessToken(token);
            setEvent(response.event);
          } else {
            setError('Nevažeći ili istekao QR kod.');
          }
        } catch (err) {
          setError('Neuspjela validacija pristupnog tokena.');
          console.error('Token validation error:', err);
        }
      } else {
        setError('Nije priložen pristupni token. Molimo skenirajte QR kod ponovno.');
      }
      setLoading(false);
    };

    checkToken();
  }, []);

  if (loading) {
    return (
      <div className="App-loading">
        <div className="spinner"></div>
        <p>Učitavanje galerije vjenčanja...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="App-error">
        <h1>⚠️ Greška Pristupa</h1>
        <p>{error}</p>
      </div>
    );
  }

  const renderView = () => {
    switch (view) {
      case 'upload':
        return <PhotoUpload accessToken={accessToken} onBack={() => setView('welcome')} />;
      case 'gallery':
        return <Gallery accessToken={accessToken} onBack={() => setView('welcome')} />;
      default:
        return <WelcomePage event={event} onNavigate={setView} />;
    }
  };

  return (
    <div className="App">
      <main className="App-content">
        {renderView()}
      </main>
      <footer className="App-footer">
        <p>Made with ❤️ for {event?.name}</p>
      </footer>
    </div>
  );
}

export default App;

