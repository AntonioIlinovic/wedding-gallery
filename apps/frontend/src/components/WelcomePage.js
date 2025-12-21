/**
 * Welcome page component showing event information
 */
import React, { useRef, useState, useCallback, useEffect } from 'react';
import { uploadPhoto } from '../api';
import Modal from './Modal';
import './WelcomePage.css';

function formatBytes(bytes, decimals = 2) {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

function formatTime(seconds) {
  if (seconds === Infinity || isNaN(seconds)) return '...';
  if (seconds < 60) return `${Math.round(seconds)}s`;
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.round(seconds % 60);
  return `${minutes}m ${remainingSeconds}s`;
}

function WelcomePage({ event, onNavigate, accessToken }) {
  const fileInputRef = useRef(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState({});
  const [uploadResults, setUploadResults] = useState([]);
  const [totalFilesCount, setTotalFilesCount] = useState(0);
  const [completedFilesCount, setCompletedFilesCount] = useState(0);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const [totalUploadSize, setTotalUploadSize] = useState(0);
  const [totalUploadedBytes, setTotalUploadedBytes] = useState(0);
  const [uploadSpeed, setUploadSpeed] = useState(0);
  const [remainingTime, setRemainingTime] = useState(0);

  const uploadStartTime = useRef(null);

  const handleFileSelect = () => {
    setIsModalOpen(true);
  };

  const handleContinueOnMobile = () => {
    setIsModalOpen(false);
    fileInputRef.current?.click();
  };

  const handleFileChange = useCallback(async (event) => {
    const files = Array.from(event.target.files || []);
    if (files.length === 0) return;

    setUploading(true);
    setUploadResults([]);
    const totalSize = files.reduce((acc, file) => acc + file.size, 0);
    setTotalUploadSize(totalSize);
    setTotalUploadedBytes(0);
    setTotalFilesCount(files.length);
    setUploadProgress({});
    setCompletedFilesCount(0);
    setUploadSpeed(0);
    setRemainingTime(0);
    uploadStartTime.current = Date.now();
    const results = [];

    const fileUploads = files.map(file => ({ file, loaded: 0, total: file.size }));

    const updateOverallProgress = () => {
      const totalLoaded = fileUploads.reduce((acc, f) => acc + f.loaded, 0);
      setTotalUploadedBytes(totalLoaded);

      const elapsedTime = (Date.now() - uploadStartTime.current) / 1000; // in seconds
      const speed = totalLoaded / elapsedTime;
      setUploadSpeed(speed);

      const remainingBytes = totalSize - totalLoaded;
      const timeRemaining = remainingBytes / speed;
      setRemainingTime(timeRemaining);
    };

    const filePromises = fileUploads.map(async (fileUpload) => {
      try {
        const result = await uploadPhoto(
          accessToken,
          fileUpload.file,
          (progressEvent) => {
            fileUpload.loaded = progressEvent.loaded;
            updateOverallProgress();
            setUploadProgress((prev) => ({
              ...prev,
              [fileUpload.file.name]: (progressEvent.loaded / progressEvent.total) * 100,
            }));
          }
        );
        results.push({ file: fileUpload.file.name, success: true, data: result });
      } catch (error) {
        results.push({
          file: fileUpload.file.name,
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
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  }, [accessToken]);

  const overallPercentage = totalUploadSize > 0 ? (totalUploadedBytes / totalUploadSize) * 100 : 0;
  const successfulUploads = uploadResults.filter(r => r.success).length;
  const failedUploads = uploadResults.length - successfulUploads;

  return (
    <div className="welcome-page">
      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)}>
        <h3 className="modal-title">Napomena</h3>
        <p className="modal-body">
          Za stabilnije učitavanje preporučamo korištenje laptopa. Na mobitelu se učitavanje može prekinuti. Možete kopirati link stranice i nastaviti na laptopu.
        </p>
        <div className="modal-actions">
          <button className="modal-button primary" onClick={handleContinueOnMobile}>
            U redu
          </button>
        </div>
      </Modal>

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
            <span>{uploading ? 'Učitavanje...' : 'Podijelite svoje fotografije'}</span>
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
            <span>Pogledajte fotogaleriju</span>
          </button>
        </div>
      </div>

      {(uploading || uploadResults.length > 0) && (
        <div className="upload-results">
          <h3>Rezultati učitavanja</h3>
          {uploading && (
            <div className="overall-upload-status">
              <div className="progress-details">
                <span>{formatBytes(totalUploadedBytes)} / {formatBytes(totalUploadSize)}</span>
                <span>{formatBytes(uploadSpeed)}/s</span>
                <span>{formatTime(remainingTime)} preostalo</span>
              </div>
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

