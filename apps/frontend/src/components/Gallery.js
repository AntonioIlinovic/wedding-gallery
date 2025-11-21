/**
 * Gallery component to display photos
 */
import React, { useState, useEffect } from 'react';
import { getPhotos } from '../api';
import './Gallery.css';

function Gallery({ accessToken, onBack }) {
  const [photos, setPhotos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedPhoto, setSelectedPhoto] = useState(null);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(false);

  useEffect(() => {
    loadPhotos();
  }, [accessToken, page]);

  const loadPhotos = async () => {
    try {
      setLoading(true);
      const data = await getPhotos(accessToken, page);
      
      if (page === 1) {
        setPhotos(data.results);
      } else {
        setPhotos((prev) => [...prev, ...data.results]);
      }
      
      setHasMore(!!data.next);
      setError(null);
    } catch (err) {
      setError('Failed to load photos');
      console.error('Error loading photos:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    setPage(1);
    loadPhotos();
  };

  const loadMore = () => {
    setPage((prev) => prev + 1);
  };

  const openLightbox = (photo) => {
    setSelectedPhoto(photo);
  };

  const closeLightbox = () => {
    setSelectedPhoto(null);
  };

  return (
    <div className="gallery">
      <div className="gallery-header">
        <button className="back-button" onClick={onBack}>
          ← Back
        </button>
        <h2>Photo Gallery</h2>
        <button className="refresh-button" onClick={handleRefresh}>
          🔄 Refresh
        </button>
      </div>

      {loading && page === 1 ? (
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading photos...</p>
        </div>
      ) : error ? (
        <div className="error-state">
          <p>{error}</p>
          <button onClick={handleRefresh}>Try Again</button>
        </div>
      ) : photos.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">📷</div>
          <h3>No Photos Yet</h3>
          <p>Be the first to share a photo from the event!</p>
        </div>
      ) : (
        <>
          <div className="photo-grid">
            {photos.map((photo) => (
              <div
                key={photo.id}
                className="photo-item"
                onClick={() => openLightbox(photo)}
              >
                <img src={photo.url} alt={photo.original_filename} />
                <div className="photo-overlay">
                  <span className="photo-date">
                    {new Date(photo.uploaded_at).toLocaleDateString()}
                  </span>
                </div>
              </div>
            ))}
          </div>

          {hasMore && (
            <div className="load-more">
              <button onClick={loadMore} disabled={loading}>
                {loading ? 'Loading...' : 'Load More Photos'}
              </button>
            </div>
          )}
        </>
      )}

      {selectedPhoto && (
        <div className="lightbox" onClick={closeLightbox}>
          <div className="lightbox-content" onClick={(e) => e.stopPropagation()}>
            <button className="lightbox-close" onClick={closeLightbox}>
              ✕
            </button>
            <img src={selectedPhoto.url} alt={selectedPhoto.original_filename} />
            <div className="lightbox-info">
              <p className="lightbox-filename">{selectedPhoto.original_filename}</p>
              <p className="lightbox-date">
                {new Date(selectedPhoto.uploaded_at).toLocaleString()}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Gallery;

