/**
 * Welcome page component showing event information
 */
import React from 'react';
import './WelcomePage.css';

function WelcomePage({ event, onNavigate }) {
  return (
    <div className="welcome-page">
      <div className="welcome-hero">
        <h1 className="welcome-title">{event.name}</h1>
        {event.date && (
          <p className="welcome-date">
            {new Date(event.date).toLocaleDateString('en-US', {
              weekday: 'long',
              year: 'numeric',
              month: 'long',
              day: 'numeric',
            })}
          </p>
        )}
      </div>

      <div className="welcome-content">
        <div className="welcome-message">
          <p>{event.description || 'Welcome to our special day!'}</p>
        </div>

        <div className="welcome-actions">
          <button
            className="action-button primary"
            onClick={() => onNavigate('upload')}
          >
            📸 Share Your Photos
          </button>
          <button
            className="action-button secondary"
            onClick={() => onNavigate('gallery')}
          >
            🖼️ View Gallery
          </button>
        </div>
      </div>
    </div>
  );
}

export default WelcomePage;

