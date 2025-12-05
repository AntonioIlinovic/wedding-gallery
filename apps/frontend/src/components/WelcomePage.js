/**
 * Welcome page component showing event information
 */
import React, { useRef, useState, useCallback, useEffect } from 'react';
import { uploadPhoto } from '../api';
import './WelcomePage.css';

function WelcomePage({ event, onNavigate, accessToken }) {
  const fileInputRef = useRef(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState({});
  const [uploadResults, setUploadResults] = useState([]);
  const [totalFilesCount, setTotalFilesCount] = useState(0);
  const [completedFilesCount, setCompletedFilesCount] = useState(0);

  const handleFileSelect = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = useCallback(async (event) => {
    const files = Array.from(event.target.files || []);
    if (files.length === 0) return;

    setUploading(true);
    setUploadResults([]);
    setTotalFilesCount(files.length);
    setUploadProgress({}); // Reset individual progress for new batch
    setCompletedFilesCount(0);
    const results = [];

    const filePromises = files.map(async (file) => {
      const fileId = file.name + '-' + file.size;
      try {
        const result = await uploadPhoto(
          accessToken,
          file,
          (progress) => {
            setUploadProgress((prev) => ({
              ...prev,
              [fileId]: progress,
            }));
          }
        );
        results.push({ file: file.name, success: true, data: result });
      } catch (error) {
        results.push({
          file: file.name,
          success: false,
          error: error.response?.data?.error || 'Upload failed',
        });
      } finally {
        setCompletedFilesCount((prev) => prev + 1);
      }
    });

    await Promise.allSettled(filePromises);

    setUploadResults(results);
    setUploading(false);
    // Reset file input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  }, [accessToken]);

  const overallPercentage = totalFilesCount > 0 ? (completedFilesCount / totalFilesCount) * 100 : 0;
  const successfulUploads = uploadResults.filter(r => r.success).length;
  const failedUploads = uploadResults.length - successfulUploads;

  return (
    <div className="welcome-page">
      <div className="welcome-hero">
        <h1 className="welcome-title">{event.name}</h1>
        {event.date && (
          <p className="welcome-date">
            {(() => {
              const date = new Date(event.date);
              return `${date.getDate()}.${date.getMonth() + 1}.${date.getFullYear()}.`;
            })()}
          </p>
        )}
      </div>

      <div className="welcome-content">
        <div className="welcome-message">
          <p>{event.description || 'Welcome to our special day!'}</p>
        </div>

        <div className="welcome-actions">
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            multiple
            onChange={handleFileChange}
            style={{ display: 'none' }}
          />
          <button
            className="action-button primary"
            onClick={handleFileSelect}
            disabled={uploading}
          >
            <span className="button-icon">
              <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="white">
                <path d="M440-440ZM120-120q-33 0-56.5-23.5T40-200v-480q0-33 23.5-56.5T120-760h126l74-80h240v80H355l-73 80H120v480h640v-360h80v360q0 33-23.5 56.5T760-120H120Zm640-560v-80h-80v-80h80v-80h80v80h80v80h-80v80h-80ZM440-260q75 0 127.5-52.5T620-440q0-75-52.5-127.5T440-620q-75 0-127.5 52.5T260-440q0 75 52.5 127.5T440-260Zm0-80q-42 0-71-29t-29-71q0-42 29-71t71-29q42 0 71 29t29 71q0 42-29 71t-71 29Z"/>
              </svg>
            </span>
            <span>{uploading ? 'Učitavanje...' : 'Podijelite vaše fotografije'}</span>
          </button>
          <button
            className="action-button secondary"
            onClick={() => onNavigate('gallery')}
            disabled={uploading}
          >
            <span className="button-icon">
              <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="white">
                <path d="M360-400h400L622-580l-92 120-62-80-108 140Zm-40 160q-33 0-56.5-23.5T240-320v-480q0-33 23.5-56.5T320-880h480q33 0 56.5 23.5T880-800v480q0 33-23.5 56.5T800-240H320Zm0-80h480v-480H320v480ZM160-80q-33 0-56.5-23.5T80-160v-560h80v560h560v80H160Zm160-720v480-480Z"/>
              </svg>
            </span>
            <span>Pogledajte galeriju</span>
          </button>
        </div>
      </div>

      {(uploading || uploadResults.length > 0) && (
        <div className="upload-results">
          <h3>Rezultati učitavanja</h3>
          {uploading && (
            <div className="overall-upload-status">
              <p className="overall-progress-text">
                Učitano: {completedFilesCount} / {totalFilesCount} fotografija
              </p>
              <div className="overall-progress-container">
                <div className="overall-progress-bar" style={{ width: `${overallPercentage}%` }}>
                </div>
              </div>
              <p className="upload-warning">
                Molimo ne zatvarajte i ne osvježavajte stranicu dok se fotografije učitavaju.
              </p>
            </div>
          )}
          {!uploading && uploadResults.length > 0 && (
            <div>
              <p className="upload-summary">
                {successfulUploads} uspješno
                {failedUploads > 0 && `, ${failedUploads} neuspješno`}
              </p>
              {uploadResults.map((result, index) => (
                <div
                  key={index}
                  className={`result-item ${result.success ? 'success' : 'error'}`}
                >
                  <span className="result-icon">
                    {result.success ? '✓' : '✗'}
                  </span>
                  <span className="result-file">{result.file}</span>
                  {!result.success && (
                    <span className="result-error">{result.error}</span>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default WelcomePage;

