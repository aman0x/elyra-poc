import { useState, useCallback, useRef } from 'react';
import { usePolling } from './usePolling';
import { Dag } from '../types/dag';
import { airflowService } from '../services/airflowService';
import { APP_CONFIG } from '../utils/constants';

interface UseDagPollingOptions {
  onSuccess?: (dags: Dag[]) => void;
  onError?: (error: string) => void;
  enabled?: boolean;
}

interface UseDagPollingReturn {
  dags: Dag[];
  loading: boolean;
  error: string | null;
  lastUpdated: Date | null;
  isPolling: boolean;
  startPolling: () => void;
  stopPolling: () => void;
  togglePolling: () => void;
  refreshNow: () => Promise<void>;
  setPollingInterval: (interval: number) => void;
  currentInterval: number;
}

export const useDagPolling = (options: UseDagPollingOptions = {}): UseDagPollingReturn => {
  const { onSuccess, onError, enabled = true } = options;
  
  const [dags, setDags] = useState<Dag[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [currentInterval, setCurrentInterval] = useState(APP_CONFIG.POLLING_INTERVAL);
  
  const isFirstLoad = useRef(true);

  // Smart polling logic: faster interval if DAGs are running
  const getSmartInterval = useCallback((dagList: Dag[]): number => {
    const hasRunningDags = dagList.some(dag => !dag.is_paused);
    
    if (hasRunningDags) {
      return APP_CONFIG.REFRESH_INTERVAL; // 5 seconds for active DAGs
    }
    return APP_CONFIG.POLLING_INTERVAL; // 30 seconds for idle state
  }, []);

  // Fetch DAGs function
  const fetchDags = useCallback(async () => {
    try {
      // Only show loading on first load, not on subsequent polls
      if (isFirstLoad.current) {
        setLoading(true);
      }
      
      const fetchedDags = await airflowService.getDags();
      
      setDags(fetchedDags);
      setError(null);
      setLastUpdated(new Date());
      
      // Update polling interval based on DAG states
      const smartInterval = getSmartInterval(fetchedDags);
      if (smartInterval !== currentInterval) {
        setCurrentInterval(smartInterval);
        pollingControls.setInterval(smartInterval);
      }
      
      onSuccess?.(fetchedDags);
      
      if (isFirstLoad.current) {
        isFirstLoad.current = false;
        setLoading(false);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch DAGs';
      setError(errorMessage);
      onError?.(errorMessage);
      
      if (isFirstLoad.current) {
        setLoading(false);
        isFirstLoad.current = false;
      }
    }
  }, [currentInterval, getSmartInterval, onSuccess, onError]);

  // Set up polling
  const pollingControls = usePolling(fetchDags, {
    interval: currentInterval,
    enabled,
    immediate: true
  });

  // Manual refresh function
  const refreshNow = useCallback(async () => {
    setLoading(true);
    try {
      await fetchDags();
    } finally {
      setLoading(false);
    }
  }, [fetchDags]);

  // Update polling interval
  const setPollingInterval = useCallback((interval: number) => {
    setCurrentInterval(interval);
    pollingControls.setInterval(interval);
  }, [pollingControls]);

  return {
    dags,
    loading,
    error,
    lastUpdated,
    isPolling: pollingControls.isPolling,
    startPolling: pollingControls.start,
    stopPolling: pollingControls.stop,
    togglePolling: pollingControls.toggle,
    refreshNow,
    setPollingInterval,
    currentInterval,
  };
};