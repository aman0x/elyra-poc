import React, { useState, useEffect } from 'react';
import './App.css';
import { Dag } from './types/dag';
import { minioService } from './services/minioService';
import { useDagPolling } from './hooks/useDagPolling';
import DagList from './components/DagList';
import DagDetails from './components/DagDetails';

function App() {
  const [selectedDag, setSelectedDag] = useState<Dag | null>(null);
  const [minioConnected, setMinioConnected] = useState<boolean>(false);

  // Use the DAG polling hook
  const {
    dags,
    loading,
    error,
    lastUpdated,
    isPolling,
    startPolling,
    stopPolling,
    togglePolling,
    refreshNow,
    setPollingInterval,
    currentInterval,
  } = useDagPolling({
    onSuccess: (fetchedDags) => {
      console.log(`✅ Successfully fetched ${fetchedDags.length} DAGs`);
    },
    onError: (error) => {
      console.error('❌ Error fetching DAGs:', error);
    },
  });

  // Check MinIO connection on component mount
  useEffect(() => {
    checkMinioConnection();
  }, []);

  const checkMinioConnection = async () => {
    try {
      const connected = await minioService.checkConnection();
      setMinioConnected(connected);
    } catch (err) {
      console.error('MinIO connection check failed:', err);
      setMinioConnected(false);
    }
  };

  const handleDagSelect = (dag: Dag) => {
    setSelectedDag(dag);
  };

  const handleBackToList = () => {
    setSelectedDag(null);
  };

  // Manual refresh function that forces a reload
  const handleRefresh = async () => {
    await refreshNow();
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Airflow DAG Manager</h1>
        <div className="connection-status">
          <span className={`status-indicator ${minioConnected ? 'connected' : 'disconnected'}`}>
            MinIO: {minioConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
      </header>

      <main className="App-main">
        {error && (
          <div className="error-message">
            <p>Error: {error}</p>
            <button onClick={handleRefresh}>Retry</button>
          </div>
        )}

        {!selectedDag ? (
          <DagList 
            dags={dags}
            loading={loading}
            onDagSelect={handleDagSelect}
            onRefresh={handleRefresh}
            // Polling props
            isPolling={isPolling}
            onTogglePolling={togglePolling}
            lastUpdated={lastUpdated}
            currentInterval={currentInterval}
            onIntervalChange={setPollingInterval}
          />
        ) : (
          <DagDetails 
            dag={selectedDag}
            onBack={handleBackToList}
          />
        )}
      </main>
    </div>
  );
}

export default App;