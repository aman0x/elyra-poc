import React from 'react';
import { formatDistanceToNow } from 'date-fns';

interface PollingControlsProps {
  isPolling: boolean;
  onToggle: () => void;
  onRefresh: () => void;
  lastUpdated: Date | null;
  currentInterval: number;
  onIntervalChange: (interval: number) => void;
  loading?: boolean;
}

const INTERVAL_OPTIONS = [
  { label: '5s', value: 5000 },
  { label: '10s', value: 10000 },
  { label: '30s', value: 30000 },
  { label: '1m', value: 60000 },
  { label: '5m', value: 300000 },
];

const PollingControls: React.FC<PollingControlsProps> = ({
  isPolling,
  onToggle,
  onRefresh,
  lastUpdated,
  currentInterval,
  onIntervalChange,
  loading = false
}) => {
  const formatLastUpdated = (date: Date | null): string => {
    if (!date) return 'Never';
    
    try {
      return formatDistanceToNow(date, { addSuffix: true });
    } catch {
      return 'Just now';
    }
  };

  return (
    <div className="polling-controls">
      <div className="polling-status">
        <div className="status-indicator">
          <span className={`status-dot ${isPolling ? 'active' : 'inactive'}`}></span>
          <span className="status-text">
            {isPolling ? 'Auto-refresh ON' : 'Auto-refresh OFF'}
          </span>
        </div>
        
        <div className="last-updated">
          <span className="label">Last updated:</span>
          <span className="time">{formatLastUpdated(lastUpdated)}</span>
          {loading && <span className="loading-spinner">⟳</span>}
        </div>
      </div>

      <div className="polling-actions">
        <div className="interval-selector">
          <label htmlFor="interval-select">Interval:</label>
          <select
            id="interval-select"
            value={currentInterval}
            onChange={(e) => onIntervalChange(Number(e.target.value))}
            className="interval-select"
          >
            {INTERVAL_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        <button
          onClick={onToggle}
          className={`toggle-btn ${isPolling ? 'active' : 'inactive'}`}
          title={isPolling ? 'Stop auto-refresh' : 'Start auto-refresh'}
        >
          {isPolling ? '⏸️' : '▶️'}
        </button>

        <button
          onClick={onRefresh}
          disabled={loading}
          className="refresh-btn"
          title="Refresh now"
        >
          {loading ? '⟳' : '🔄'}
        </button>
      </div>
    </div>
  );
};

export default PollingControls;