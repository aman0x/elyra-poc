import { format, parseISO } from 'date-fns';

/**
 * Format a date string to a readable format
 */
export const formatDate = (dateString: string | undefined): string => {
  if (!dateString) return 'N/A';
  
  try {
    return format(parseISO(dateString), 'MMM dd, yyyy HH:mm:ss');
  } catch (error) {
    return 'Invalid date';
  }
};

/**
 * Format duration in seconds to human readable format
 */
export const formatDuration = (seconds: number | undefined): string => {
  if (!seconds) return 'N/A';
  
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const remainingSeconds = Math.floor(seconds % 60);
  
  if (hours > 0) {
    return `${hours}h ${minutes}m ${remainingSeconds}s`;
  } else if (minutes > 0) {
    return `${minutes}m ${remainingSeconds}s`;
  } else {
    return `${remainingSeconds}s`;
  }
};

/**
 * Get status color based on DAG or task state
 */
export const getStatusColor = (state: string | undefined): string => {
  switch (state) {
    case 'success':
      return '#52c41a'; // green
    case 'running':
      return '#1890ff'; // blue
    case 'failed':
      return '#ff4d4f'; // red
    case 'queued':
      return '#faad14'; // orange
    case 'skipped':
      return '#d9d9d9'; // gray
    default:
      return '#8c8c8c'; // default gray
  }
};

/**
 * Create Basic Auth header for Airflow API
 */
export const createAuthHeader = (username: string, password: string): string => {
  return `Basic ${btoa(`${username}:${password}`)}`;
};

/**
 * Handle API errors and return user-friendly messages
 */
export const handleApiError = (error: any): string => {
  if (error.response) {
    // Server responded with error status
    return error.response.data?.detail || `Error ${error.response.status}: ${error.response.statusText}`;
  } else if (error.request) {
    // Request was made but no response received
    return 'Network error: Unable to connect to server';
  } else {
    // Something else happened
    return error.message || 'An unexpected error occurred';
  }
};