/**
 * Export asset component for downloading Figma assets with custom colors.
 */
import React, { useState } from 'react';
import apiClient from '../api';
import './ExportAsset.css';

function ExportAsset({ show, onClose }) {
  const [assetName, setAssetName] = useState('logo-nextdoor-wordmark-0513');
  const [color, setColor] = useState('#1B8751');
  const [isExporting, setIsExporting] = useState(false);
  const [error, setError] = useState(null);

  if (!show) return null;

  const handleExport = async () => {
    setIsExporting(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/api/export/figma', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          node_name: assetName,
          color: color,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Export failed');
      }

      // Download the SVG
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${assetName.toLowerCase().replace(/[^a-z0-9-]/g, '-')}.svg`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);

      // Close modal after successful export
      setTimeout(() => onClose(), 500);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <h3>Export Asset from Figma</h3>

        <div className="form-group">
          <label>Asset Name:</label>
          <input
            type="text"
            value={assetName}
            onChange={(e) => setAssetName(e.target.value)}
            placeholder="logo-nextdoor-wordmark-0513"
          />
          <p className="hint">Enter the exact name of the asset in Figma</p>
        </div>

        <div className="form-group">
          <label>Color (optional):</label>
          <input
            type="text"
            value={color}
            onChange={(e) => setColor(e.target.value)}
            placeholder="#1B8751"
          />
          <p className="hint">
            Brand colors: Lawn (#1B8751), Dusk (#232F46), Vista Blue (#85AFCC)
          </p>
        </div>

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        <div className="modal-actions">
          <button onClick={handleExport} disabled={isExporting || !assetName}>
            {isExporting ? 'Exporting...' : 'Export SVG'}
          </button>
          <button onClick={onClose} className="secondary">
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}

export default ExportAsset;

