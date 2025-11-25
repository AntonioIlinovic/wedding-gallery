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
  const [selectedPhotoIndex, setSelectedPhotoIndex] = useState(null);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(false);

  useEffect(() => {
    loadPhotos();
  }, [accessToken, page]);

  // Keyboard navigation for lightbox
  useEffect(() => {
    const handleKeyPress = (e) => {
      if (selectedPhoto === null) return;

      if (e.key === 'ArrowLeft') {
        navigatePrevious();
      } else if (e.key === 'ArrowRight') {
        navigateNext();
      } else if (e.key === 'Escape') {
        closeLightbox();
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [selectedPhoto, selectedPhotoIndex, photos]);

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

  const openLightbox = (photo, index) => {
    setSelectedPhoto(photo);
    setSelectedPhotoIndex(index);
  };

  const closeLightbox = () => {
    setSelectedPhoto(null);
    setSelectedPhotoIndex(null);
  };

  const navigateNext = () => {
    if (selectedPhotoIndex < photos.length - 1) {
      const nextIndex = selectedPhotoIndex + 1;
      setSelectedPhotoIndex(nextIndex);
      setSelectedPhoto(photos[nextIndex]);
    }
  };

  const navigatePrevious = () => {
    if (selectedPhotoIndex > 0) {
      const prevIndex = selectedPhotoIndex - 1;
      setSelectedPhotoIndex(prevIndex);
      setSelectedPhoto(photos[prevIndex]);
    }
  };

  return (
    <div className="gallery">
      <div className="gallery-header">
        <button className="back-button" onClick={onBack}>
          ← Natrag
        </button>
        <h2>Galerija Fotografija</h2>
      </div>

      {loading && page === 1 ? (
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Učitavanje fotografija...</p>
        </div>
      ) : error ? (
        <div className="error-state">
          <p>{error}</p>
          <button onClick={handleRefresh}>Pokušajte Ponovno</button>
        </div>
      ) : photos.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">📷</div>
          <h3>Još Nema Fotografija</h3>
          <p>Budite prvi koji će podijeliti fotografiju s događaja!</p>
        </div>
      ) : (
        <>
          <div className="photo-grid">
            {photos.map((photo, index) => (
              <div
                key={photo.id}
                className="photo-item"
                onClick={() => openLightbox(photo, index)}
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
                {loading ? 'Učitavanje...' : 'Učitaj Više Fotografija'}
              </button>
            </div>
          )}
        </>
      )}

      {selectedPhoto && (
        <div className="lightbox" onClick={closeLightbox}>
          <button className="lightbox-close" onClick={closeLightbox}>
            ✕
          </button>
          
          {/* Previous button - fixed position on left */}
          {selectedPhotoIndex > 0 && (
            <button 
              className="lightbox-nav lightbox-nav-prev" 
              onClick={(e) => { e.stopPropagation(); navigatePrevious(); }}
            >
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="15 18 9 12 15 6"></polyline>
              </svg>
            </button>
          )}
          
          {/* Next button - fixed position on right */}
          {selectedPhotoIndex < photos.length - 1 && (
            <button 
              className="lightbox-nav lightbox-nav-next" 
              onClick={(e) => { e.stopPropagation(); navigateNext(); }}
            >
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="9 18 15 12 9 6"></polyline>
              </svg>
            </button>
          )}
          
          <div className="lightbox-content" onClick={(e) => e.stopPropagation()}>
            <img src={selectedPhoto.url} alt={selectedPhoto.original_filename} />
            
            <div className="lightbox-info">
              <p className="lightbox-filename">{selectedPhoto.original_filename}</p>
              <p className="lightbox-date">
                {new Date(selectedPhoto.uploaded_at).toLocaleString()}
              </p>
              <p className="lightbox-counter">
                {selectedPhotoIndex + 1} / {photos.length}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Gallery;

