import React from 'react';
import { Dag } from '../types/dag';
import { formatDate, getStatusColor } from '../utils/helpers';
import PollingControls from './PollingControls';

interface DagListProps {
  dags: Dag[];
  loading: boolean;
  onDagSelect: (dag: Dag) => void;
  onRefresh: () => void;
  // Polling props
  isPolling: boolean;
  onTogglePolling: () => void;
  lastUpdated: Date | null;
  currentInterval: number;
  onIntervalChange: (interval: number) => void;
}

const DagList: React.FC<DagListProps> = ({ 
  dags, 
  loading, 
  onDagSelect, 
  onRefresh,
  isPolling,
  onTogglePolling,
  lastUpdated,
  currentInterval,
  onIntervalChange
}) => {
  if (loading && dags.length === 0) {
    return (
      <div className="loading">
        <p>Loading DAGs...</p>
      </div>
    );
  }

  if (dags.length === 0 && !loading) {
    return (
      <div className="empty-state">
        <p>No DAGs found</p>
        <button onClick={onRefresh} className="refresh-btn">
          Refresh
        </button>
      </div>
    );
  }

  return (
    <div className="dag-list">
      <PollingControls
        isPolling={isPolling}
        onToggle={onTogglePolling}
        onRefresh={onRefresh}
        lastUpdated={lastUpdated}
        currentInterval={currentInterval}
        onIntervalChange={onIntervalChange}
        loading={loading}
      />

      <div className="dag-list-header">
        <h2>DAGs ({dags.length})</h2>
        <button onClick={onRefresh} className="refresh-btn" disabled={loading}>
          {loading ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>

      <div className="dag-table-container">
        <table className="dag-table">
          <thead>
            <tr>
              <th>DAG ID</th>
              <th>Status</th>
              <th>Description</th>
              <th>Owner</th>
              <th>Last Parsed</th>
              <th>Next Run</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {dags.map((dag) => (
              <tr key={dag.dag_id} className="dag-row">
                <td className="dag-id">
                  <span className="dag-name">{dag.dag_id}</span>
                  {dag.tags && dag.tags.length > 0 && (
                    <div className="dag-tags">
                      {dag.tags.map((tag, index) => (
                        <span key={index} className="tag">
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}
                </td>
                <td className="dag-status">
                  <span 
                    className="status-badge"
                    style={{ 
                      backgroundColor: dag.is_paused ? '#ff4d4f' : '#52c41a',
                      color: 'white'
                    }}
                  >
                    {dag.is_paused ? 'Paused' : 'Active'}
                  </span>
                </td>
                <td className="dag-description">
                  {dag.description || 'No description'}
                </td>
                <td className="dag-owner">
                  {dag.owners && dag.owners.length > 0 ? dag.owners.join(', ') : 'N/A'}
                </td>
                <td className="dag-last-parsed">
                  {formatDate(dag.last_parsed_time)}
                </td>
                <td className="dag-next-run">
                  {formatDate(dag.next_dagrun)}
                </td>
                <td className="dag-actions">
                  <button 
                    onClick={() => onDagSelect(dag)}
                    className="view-btn"
                  >
                    View Details
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default DagList;