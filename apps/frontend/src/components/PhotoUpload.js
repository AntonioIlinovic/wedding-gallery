/**
 * Photo upload component with drag-and-drop support
 */
import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { uploadPhoto } from '../api';
import './PhotoUpload.css';

function PhotoUpload({ accessToken, onBack }) {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState({});
  const [uploadResults, setUploadResults] = useState([]);

  const onDrop = useCallback((acceptedFiles) => {
    const filesWithPreview = acceptedFiles.map((file) =>
      Object.assign(file, {
        preview: URL.createObjectURL(file),
        id: Math.random().toString(36).substring(7),
      })
    );
    setSelectedFiles((prev) => [...prev, ...filesWithPreview]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.gif', '.webp'],
    },
    multiple: true,
  });

  const removeFile = (fileId) => {
    setSelectedFiles((files) => files.filter((f) => f.id !== fileId));
  };

  const handleUpload = async () => {
    if (selectedFiles.length === 0) return;

    setUploading(true);
    setUploadResults([]);
    const results = [];

    for (const file of selectedFiles) {
      try {
        const result = await uploadPhoto(
          accessToken,
          file,
          (progress) => {
            setUploadProgress((prev) => ({
              ...prev,
              [file.id]: progress,
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
      }
    }

    setUploadResults(results);
    setUploading(false);
    setSelectedFiles([]);
    setUploadProgress({});
  };

  return (
    <div className="photo-upload">
      <div className="upload-header">
        <button className="back-button" onClick={onBack}>
          ← Back
        </button>
        <h2>Upload Your Photos</h2>
      </div>

      <div
        {...getRootProps()}
        className={`dropzone ${isDragActive ? 'active' : ''}`}
      >
        <input {...getInputProps()} />
        <div className="dropzone-content">
          <div className="upload-icon">📤</div>
          {isDragActive ? (
            <p>Drop the photos here...</p>
          ) : (
            <>
              <p>Drag and drop photos here, or click to select</p>
              <small>Supported formats: JPEG, PNG, GIF, WebP</small>
            </>
          )}
        </div>
      </div>

      {selectedFiles.length > 0 && (
        <div className="selected-files">
          <h3>Selected Photos ({selectedFiles.length})</h3>
          <div className="file-grid">
            {selectedFiles.map((file) => (
              <div key={file.id} className="file-preview">
                <img src={file.preview} alt={file.name} />
                <button
                  className="remove-button"
                  onClick={() => removeFile(file.id)}
                  disabled={uploading}
                >
                  ✕
                </button>
                {uploadProgress[file.id] !== undefined && (
                  <div className="upload-progress">
                    <div
                      className="progress-bar"
                      style={{ width: `${uploadProgress[file.id]}%` }}
                    />
                  </div>
                )}
              </div>
            ))}
          </div>

          <button
            className="upload-button"
            onClick={handleUpload}
            disabled={uploading}
          >
            {uploading ? 'Uploading...' : `Upload ${selectedFiles.length} Photo${selectedFiles.length > 1 ? 's' : ''}`}
          </button>
        </div>
      )}

      {uploadResults.length > 0 && (
        <div className="upload-results">
          <h3>Upload Results</h3>
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
  );
}

export default PhotoUpload;

