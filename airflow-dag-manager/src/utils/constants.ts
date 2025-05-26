// Airflow Configuration
export const AIRFLOW_CONFIG = {
  BASE_URL: process.env.REACT_APP_AIRFLOW_BASE_URL || 'http://localhost:8080',
  USERNAME: process.env.REACT_APP_AIRFLOW_USERNAME || 'admin',
  PASSWORD: process.env.REACT_APP_AIRFLOW_PASSWORD || 'admin',
  API_VERSION: 'v1',
  TIMEOUT: parseInt(process.env.REACT_APP_API_TIMEOUT || '10000'),
} as const;

// MinIO Configuration
export const MINIO_CONFIG = {
  ENDPOINT: process.env.REACT_APP_MINIO_ENDPOINT || 'localhost:9000',
  ACCESS_KEY: process.env.REACT_APP_MINIO_ACCESS_KEY || 'minioadmin',
  SECRET_KEY: process.env.REACT_APP_MINIO_SECRET_KEY || 'minioadmin',
  BUCKET_NAME: process.env.REACT_APP_MINIO_BUCKET_NAME || 'airflow-dags',
  USE_SSL: process.env.REACT_APP_MINIO_USE_SSL === 'true',
} as const;

// Application Configuration
export const APP_CONFIG = {
  POLLING_INTERVAL: parseInt(process.env.REACT_APP_POLLING_INTERVAL || '30000'),
  REFRESH_INTERVAL: 5000,
  MAX_RETRIES: 3,
} as const;

// API Endpoints for Airflow 1.10.15 (experimental API)
export const ENDPOINTS = {
  LATEST_RUNS: '/api/experimental/latest_runs', // Gets latest run for each DAG
  DAG_RUNS: '/api/experimental/dags/{dag_id}/dag_runs',
  TASK_INSTANCES: '/api/experimental/dags/{dag_id}/dag_runs/{dag_run_id}/tasks',
  TRIGGER_DAG: '/api/experimental/dags/{dag_id}/dag_runs',
  TEST: '/api/experimental/test',
} as const;