/**
 * Admin panel for syncing data sources.
 */
import React, { useState, useEffect } from 'react';
import apiClient from '../api';
import './AdminPanel.css';

function AdminPanel() {
  const [stats, setStats] = useState(null);
  const [isSyncing, setIsSyncing] = useState({ figma: false, slides: false });
  const [syncResults, setSyncResults] = useState({ figma: null, slides: null });

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const data = await apiClient.getStats();
      setStats(data);
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  const handleSyncFigma = async () => {
    setIsSyncing((prev) => ({ ...prev, figma: true }));
    setSyncResults((prev) => ({ ...prev, figma: null }));

    try {
      const result = await apiClient.syncFigma(false);
      setSyncResults((prev) => ({ ...prev, figma: result }));
      await loadStats();
    } catch (error) {
      console.error('Error syncing Figma:', error);
      setSyncResults((prev) => ({
        ...prev,
        figma: { status: 'error', message: error.message },
      }));
    } finally {
      setIsSyncing((prev) => ({ ...prev, figma: false }));
    }
  };

  const handleSyncSlides = async () => {
    setIsSyncing((prev) => ({ ...prev, slides: true }));
    setSyncResults((prev) => ({ ...prev, slides: null }));

    try {
      const result = await apiClient.syncSlides(false);
      setSyncResults((prev) => ({ ...prev, slides: result }));
      await loadStats();
    } catch (error) {
      console.error('Error syncing Slides:', error);
      setSyncResults((prev) => ({
        ...prev,
        slides: { status: 'error', message: error.message },
      }));
    } finally {
      setIsSyncing((prev) => ({ ...prev, slides: false }));
    }
  };

  return (
    <div className="admin-panel">
      <h2>Admin Panel</h2>

      <div className="stats-section">
        <h3>Database Statistics</h3>
        {stats ? (
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-value">{stats.total_documents}</div>
              <div className="stat-label">Total Documents</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{stats.collection_name}</div>
              <div className="stat-label">Collection</div>
            </div>
          </div>
        ) : (
          <p>Loading stats...</p>
        )}
      </div>

      <div className="sync-section">
        <h3>Data Sources</h3>

        <div className="sync-card">
          <div className="sync-header">
            <h4>Figma</h4>
            <button onClick={handleSyncFigma} disabled={isSyncing.figma}>
              {isSyncing.figma ? 'Syncing...' : 'Sync Figma Files'}
            </button>
          </div>
          <p>Sync design components, styles, and tokens from Figma</p>

          {syncResults.figma && (
            <div className={`sync-result ${syncResults.figma.status}`}>
              {syncResults.figma.status === 'success' ? (
                <div>
                  <p>
                    <strong>Successfully synced!</strong>
                  </p>
                  <p>Files synced: {syncResults.figma.synced_files?.length || 0}</p>
                  <p>Total documents: {syncResults.figma.total_documents}</p>
                  {syncResults.figma.synced_files && (
                    <ul className="synced-files">
                      {syncResults.figma.synced_files.map((file, idx) => (
                        <li key={idx}>
                          {file.name} - {file.components} components, {file.styles} styles
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              ) : (
                <p>Error: {syncResults.figma.message}</p>
              )}
            </div>
          )}
        </div>

        <div className="sync-card">
          <div className="sync-header">
            <h4>Google Slides</h4>
            <button onClick={handleSyncSlides} disabled={isSyncing.slides}>
              {isSyncing.slides ? 'Syncing...' : 'Sync Google Slides'}
            </button>
          </div>
          <p>Sync design documentation from Google Slides presentations</p>

          {syncResults.slides && (
            <div className={`sync-result ${syncResults.slides.status}`}>
              {syncResults.slides.status === 'success' ? (
                <div>
                  <p>
                    <strong>Successfully synced!</strong>
                  </p>
                  <p>Presentations synced: {syncResults.slides.synced_presentations?.length || 0}</p>
                  <p>Total documents: {syncResults.slides.total_documents}</p>
                  {syncResults.slides.synced_presentations && (
                    <ul className="synced-files">
                      {syncResults.slides.synced_presentations.map((pres, idx) => (
                        <li key={idx}>
                          {pres.name} - {pres.slides} slides
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              ) : (
                <p>Error: {syncResults.slides.message}</p>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default AdminPanel;

