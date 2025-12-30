/**
 * Gallery component to display photos with virtualization using react-virtuoso
 */
import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { getPhotos } from '../api';
import './Gallery.css';
import { Virtuoso } from 'react-virtuoso';

// Custom hook to get window size
function useWindowSize() {
  const [size, setSize] = useState([window.innerWidth, window.innerHeight]);
  useEffect(() => {
    const handleResize = () => {
      setSize([window.innerWidth, window.innerHeight]);
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);
  return size;
}

function Gallery({ accessToken, onBack }) {
  const [photos, setPhotos] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedPhoto, setSelectedPhoto] = useState(null);
  const [selectedPhotoIndex, setSelectedPhotoIndex] = useState(null);
  const [hasMore, setHasMore] = useState(true);
  const [totalPhotos, setTotalPhotos] = useState(0);
  const [nextPageUrl, setNextPageUrl] = useState(null);
  const [width, height] = useWindowSize();

  const loadMoreItems = useCallback(async () => {
    if (loading || !hasMore) return;

    setLoading(true);
    try {
      const pageToFetch = nextPageUrl ? new URL(nextPageUrl).searchParams.get('page') : 1;
      const data = await getPhotos(accessToken, pageToFetch);
      
      setPhotos((prev) => {
        const newPhotos = data.results.filter(
          (newPhoto) => !prev.some((prevPhoto) => prevPhoto.id === newPhoto.id)
        );
        return [...prev, ...newPhotos];
      });
      setHasMore(!!data.next);
      setNextPageUrl(data.next);
      setTotalPhotos(data.count);
      setError(null);
    } catch (err) {
      setError('Failed to load photos');
      console.error('Error loading photos:', err);
    } finally {
      setLoading(false);
    }
  }, [accessToken, loading, hasMore, nextPageUrl]);
  
  // Initial load
  useEffect(() => {
    loadMoreItems();
  }, [loadMoreItems]);

  const handleRefresh = () => {
    setPhotos([]);
    setNextPageUrl(null);
    setHasMore(true);
    loadMoreItems();
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
      loadMoreItems();
    }
  };

  const navigatePrevious = () => {
    if (selectedPhotoIndex > 0) {
      const prevIndex = selectedPhotoIndex - 1;
      setSelectedPhotoIndex(prevIndex);
      setSelectedPhoto(photos[prevIndex]);
    }
  };

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

  // Calculate grid layout with responsive column width
  const minColumnWidth = useMemo(() => {
    if (width >= 1920) return 400; // Large/high-res screens
    if (width >= 1440) return 250; // Medium-large screens
    if (width >= 1024) return 220; // Medium screens
    return 180; // Small screens
  }, [width]);
  const columnCount = useMemo(() => Math.max(1, Math.floor(width / minColumnWidth)), [width, minColumnWidth]);
  const columnWidth = useMemo(() => width / columnCount, [width, columnCount]);
  const rowHeight = columnWidth; // Square thumbnails

  // Group photos into rows for grid display
  const photoRows = useMemo(() => {
    const rows = [];
    for (let i = 0; i < photos.length; i += columnCount) {
      rows.push(photos.slice(i, i + columnCount));
    }
    return rows;
  }, [photos, columnCount]);

  // Handle end reached for infinite scroll
  const handleEndReached = useCallback(() => {
    if (hasMore && !loading) {
      loadMoreItems();
    }
  }, [hasMore, loading, loadMoreItems]);

  // Render a row of photos
  const renderRow = useCallback((index) => {
    const row = photoRows[index];
    if (!row) return null;

    return (
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: `repeat(${columnCount}, 1fr)`,
          gap: '4px',
          padding: '4px 0',
        }}
      >
        {row.map((photo, colIndex) => {
          const photoIndex = index * columnCount + colIndex;
          return (
            <div
              key={photo.id}
              className="photo-item"
              onClick={() => openLightbox(photo, photoIndex)}
              style={{
                width: '100%',
                aspectRatio: '1',
              }}
            >
              <img
                src={photo.thumbnail_url}
                alt={photo.original_filename}
                style={{
                  width: '100%',
                  height: '100%',
                  objectFit: 'cover',
                  borderRadius: '8px',
                  boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
                }}
              />
            </div>
          );
        })}
        {/* Fill remaining columns if row is incomplete */}
        {row.length < columnCount &&
          Array.from({ length: columnCount - row.length }).map((_, idx) => (
            <div key={`empty-${idx}`} />
          ))}
      </div>
    );
  }, [photoRows, columnCount, openLightbox]);

  // Footer component for loading indicator
  const Footer = useCallback(() => {
    if (!loading || !hasMore) return null;
    return (
      <div className="loading-more">
        <div className="spinner"></div>
        <p>Učitavanje fotografija...</p>
      </div>
    );
  }, [loading, hasMore]);

  return (
    <div className="gallery">
      <div className="gallery-header">
        <button className="back-button" onClick={onBack}>
          ← Natrag
        </button>
        <h2>Galerija fotografija</h2>
      </div>
      
      {loading && photos.length === 0 ? (
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Učitavanje fotografija...</p>
        </div>
      ) : error ? (
        <div className="error-state">
          <p>{error}</p>
          <button onClick={handleRefresh}>Pokušajte ponovno</button>
        </div>
      ) : photos.length === 0 && !hasMore ? (
        <div className="empty-state">
          <div className="empty-icon">📷</div>
          <h3>Još nema fotografija</h3>
          <p>Budite prvi koji će podijeliti fotografije sa vjenčanja!</p>
        </div>
      ) : (
        <div className="photo-grid-container" style={{ height: height - 120 }}>
          <Virtuoso
            style={{ height: '100%' }}
            data={photoRows}
            totalCount={photoRows.length}
            endReached={handleEndReached}
            itemContent={renderRow}
            components={{ Footer }}
            overscan={5}
          />
        </div>
      )}

      {selectedPhoto && (
        <div className="lightbox" onClick={closeLightbox}>
          <button className="lightbox-close" onClick={closeLightbox}>
            ✕
          </button>
          
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
          
          {(selectedPhotoIndex < photos.length - 1 || hasMore) && (
            <button 
              className="lightbox-nav lightbox-nav-next" 
              onClick={(e) => { e.stopPropagation(); navigateNext(); }}
              disabled={loading && selectedPhotoIndex === photos.length - 1}
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
                {selectedPhotoIndex + 1} / {totalPhotos}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Gallery;
