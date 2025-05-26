import { useEffect, useRef, useCallback, useState } from 'react';

interface UsePollingOptions {
  interval: number; // Polling interval in milliseconds
  enabled?: boolean; // Whether polling is enabled
  immediate?: boolean; // Whether to execute immediately on mount
}

interface UsePollingReturn {
  isPolling: boolean;
  start: () => void;
  stop: () => void;
  toggle: () => void;
  setInterval: (newInterval: number) => void;
}

export const usePolling = (
  callback: () => void | Promise<void>,
  options: UsePollingOptions
): UsePollingReturn => {
  const { interval, enabled = true, immediate = true } = options;
  
  const [isPolling, setIsPolling] = useState(enabled);
  const [currentInterval, setCurrentInterval] = useState(interval);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const callbackRef = useRef(callback);

  // Update callback ref when callback changes
  useEffect(() => {
    callbackRef.current = callback;
  }, [callback]);

  // Start polling
  const start = useCallback(() => {
    if (intervalRef.current) return; // Already polling

    setIsPolling(true);
    
    const poll = async () => {
      try {
        await callbackRef.current();
      } catch (error) {
        console.error('Polling error:', error);
      }
    };

    // Execute immediately if requested
    if (immediate) {
      poll();
    }

    // Set up interval
    intervalRef.current = globalThis.setInterval(poll, currentInterval);
  }, [currentInterval, immediate]);

  // Stop polling
  const stop = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    setIsPolling(false);
  }, []);

  // Toggle polling
  const toggle = useCallback(() => {
    if (isPolling) {
      stop();
    } else {
      start();
    }
  }, [isPolling, start, stop]);

  // Update interval
  const setInterval = useCallback((newInterval: number) => {
    setCurrentInterval(newInterval);
    
    // Restart polling with new interval if currently polling
    if (isPolling) {
      stop();
      setTimeout(() => start(), 0); // Restart on next tick
    }
  }, [isPolling, start, stop]);

  // Effect to handle enabled/disabled state
  useEffect(() => {
    if (enabled && !isPolling) {
      start();
    } else if (!enabled && isPolling) {
      stop();
    }
  }, [enabled, isPolling, start, stop]);

  // Effect to restart polling when interval changes
  useEffect(() => {
    if (isPolling) {
      stop();
      start();
    }
  }, [currentInterval]); // Don't include start/stop to avoid infinite loop

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  return {
    isPolling,
    start,
    stop,
    toggle,
    setInterval,
  };
};