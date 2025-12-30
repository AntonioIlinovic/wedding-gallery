/**
 * Gallery component to display photos
 */
import React, { useState, useEffect, useRef } from 'react';
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
  const [totalPhotos, setTotalPhotos] = useState(0);
  const loader = useRef(null);

  const loadPhotos = async () => {
    try {
      setLoading(true);
      const data = await getPhotos(accessToken, page);
      
      setPhotos((prev) => {
        const newPhotos = data.results.filter(
          (newPhoto) => !prev.some((prevPhoto) => prevPhoto.id === newPhoto.id)
        );
        return [...prev, ...newPhotos];
      });
      setHasMore(!!data.next);
      setTotalPhotos(data.count); // Assume API returns total count
      setError(null);
    } catch (err) {
      setError('Failed to load photos');
      console.error('Error loading photos:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPhotos();
  }, [page, accessToken]);

  useEffect(() => {
    const handleObserver = (entities) => {
      const target = entities[0];
      if (target.isIntersecting && hasMore && !loading) {
        setPage((prev) => prev + 1);
      }
    };

    const observer = new IntersectionObserver(handleObserver, {
      root: null,
      rootMargin: '20px',
      threshold: 1.0,
    });

    if (loader.current) {
      observer.observe(loader.current);
    }

    return () => {
      if (loader.current) {
        observer.unobserve(loader.current);
      }
    };
  }, [hasMore, loading, loader.current]);

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
  }, [selectedPhoto, selectedPhotoIndex, photos, hasMore, loading]);

  const handleRefresh = () => {
    setPage(1);
    setPhotos([]);
    loadPhotos();
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
    } else if (hasMore && !loading) {
      setPage((prev) => prev + 1);
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
        <h2>Galerija fotografija</h2>
      </div>

      {loading && page === 1 ? (
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Učitavanje fotografija...</p>
        </div>
      ) : error ? (
        <div className="error-state">
          <p>{error}</p>
          <button onClick={handleRefresh}>Pokušajte ponovno</button>
        </div>
      ) : photos.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">📷</div>
          <h3>Još nema fotografija</h3>
          <p>Budite prvi koji će podijeliti fotografije sa vjenčanja!</p>
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
                <img src={photo.thumbnail_url} alt={photo.original_filename} />
              </div>
            ))}
          </div>

          {hasMore && (
            <div ref={loader} className="loading-more">
              <div className="spinner"></div>
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
          {(selectedPhotoIndex < photos.length - 1 || hasMore) && (
            <button 
              className="lightbox-nav lightbox-nav-next" 
              onClick={(e) => { e.stopPropagation(); navigateNext(); }}
              disabled={loading}
            >
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="9 18 15 12 9 6"></polyline>
              </svg>
            </button>
          )}
          
          <div className="lightbox-content" onClick={(e) => e.stopPropagation()}>
            <img src={selectedPhoto.fullscreen_url} alt={selectedPhoto.original_filename} />
            
            <div className="lightbox-info">
              <p className="lightbox-counter">
                {selectedPhotoIndex + 1} / {totalPhotos > 0 ? totalPhotos : photos.length}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Gallery;
