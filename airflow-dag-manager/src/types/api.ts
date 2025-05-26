import { Dag, DagRun, TaskInstance } from './dag';

// For Airflow 1.10.15 experimental API - responses are usually direct arrays or objects
export interface ApiResponse<T> {
  data?: T; // Modern API wraps in data
  // Experimental API often returns data directly
}

// Experimental API responses (arrays directly, no wrapper)
export type DagListResponse = Dag[]; // experimental/latest_runs returns array directly
export type DagRunListResponse = DagRun[]; // experimental/dags/{id}/dag_runs returns array directly  
export type TaskInstanceListResponse = TaskInstance[]; // experimental API returns array directly

export interface TriggerDagRequest {
  conf?: any;
  execution_date?: string;
  replace_microseconds?: boolean;
  run_id?: string; // Experimental API uses run_id
}

export interface TriggerDagResponse {
  dag_run_id?: string;
  dag_id: string;
  execution_date: string;
  state: string;
  external_trigger: boolean;
  message?: string; // Experimental API often returns a message
}

export interface ApiError {
  detail?: string;
  status?: number;
  title?: string;
  type?: string;
  message?: string; // Experimental API error format
}

export interface MinioObject {
  name: string;
  lastModified: Date;
  etag: string;
  size: number;
}

// For experimental API latest_runs endpoint
export interface LatestRunsResponse {
  dag_id: string;
  execution_date?: string;
  start_date?: string;
  end_date?: string;
  state?: string;
  run_id?: string;
  external_trigger?: boolean;
  conf?: any;
  // DAG metadata that might be included
  description?: string;
  fileloc?: string;
  is_paused?: boolean;
  owners?: string[];
  tags?: string[];
}