import axios, { AxiosInstance } from 'axios';
import { AIRFLOW_CONFIG, ENDPOINTS } from '../utils/constants';
import { createAuthHeader, handleApiError } from '../utils/helpers';
import { Dag, DagRun, TaskInstance } from '../types/dag';
import { 
  DagListResponse,
  DagRunListResponse,
  TaskInstanceListResponse,
  TriggerDagRequest,
  TriggerDagResponse,
  LatestRunsResponse
} from '../types/api';

class AirflowService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: AIRFLOW_CONFIG.BASE_URL,
      timeout: AIRFLOW_CONFIG.TIMEOUT,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': createAuthHeader(AIRFLOW_CONFIG.USERNAME, AIRFLOW_CONFIG.PASSWORD)
      }
    });

    // Add response interceptor for error handling
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('Airflow API Error:', handleApiError(error));
        return Promise.reject(error);
      }
    );
  }

  /**
   * Get all DAGs via latest runs (workaround for 1.10.15 limitation)
   * The experimental API doesn't have a direct DAGs endpoint, so we use latest_runs
   */
  async getDags(limit: number = 100, offset: number = 0): Promise<Dag[]> {
    try {
      const response = await this.api.get<any>(ENDPOINTS.LATEST_RUNS);
      
      // Log the actual response to understand its structure
      console.log('Latest runs response:', JSON.stringify(response.data, null, 2));
      
      const latestRuns = response.data;
      
      // Handle different possible response formats
      let runsData: any[] = [];
      
      if (Array.isArray(latestRuns)) {
        // If it's an array, use it directly
        runsData = latestRuns;
      } else if (latestRuns && typeof latestRuns === 'object') {
        // If it's an object, it might be keyed by DAG ID
        // Try to extract values or look for a specific property
        if (latestRuns.items) {
          runsData = Array.isArray(latestRuns.items) ? latestRuns.items : [];
        } else if (latestRuns.data) {
          runsData = Array.isArray(latestRuns.data) ? latestRuns.data : [];
        } else {
          // Assume it's keyed by DAG ID, extract values
          runsData = Object.values(latestRuns);
        }
      }
      
      if (!Array.isArray(runsData)) {
        console.warn('Could not extract array from latest_runs response:', latestRuns);
        return [];
      }
      
      // Convert runs to DAG objects, removing duplicates by dag_id
      const dagMap = new Map<string, Dag>();
      
      runsData.forEach((run: any) => {
        if (run && run.dag_id && !dagMap.has(run.dag_id)) {
          // Create a DAG object from the run information
          const dag: Dag = {
            dag_id: run.dag_id,
            description: run.description || '',
            file_token: '', // Not available in latest_runs
            fileloc: run.fileloc || '',
            is_active: true, // Assume active if it has recent runs
            is_paused: run.is_paused || false,
            last_parsed_time: undefined, // Not available in latest_runs
            last_pickled: undefined,
            last_expired: undefined,
            scheduler_lock: undefined,
            pickle_id: undefined,
            default_view: undefined,
            orientation: undefined,
            tags: run.tags || [],
            owners: run.owners || [],
            start_date: run.start_date,
            end_date: run.end_date,
            max_active_tasks: undefined,
            max_active_runs: undefined,
            has_task_concurrency_limits: undefined,
            has_import_errors: undefined,
            next_dagrun: undefined,
            next_dagrun_data_interval_start: undefined,
            next_dagrun_data_interval_end: undefined,
            next_dagrun_create_after: undefined,
          };
          dagMap.set(run.dag_id, dag);
        }
      });
      
      const result = Array.from(dagMap.values());
      console.log(`Extracted ${result.length} DAGs from latest_runs`);
      
      return result;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  /**
   * Get a specific DAG by ID (workaround for experimental API limitation)
   * Since experimental API doesn't have a direct DAG endpoint, we get all DAGs and filter
   */
  async getDag(dagId: string): Promise<Dag> {
    try {
      // Get all DAGs and find the specific one
      const allDags = await this.getDags();
      const dag = allDags.find(d => d.dag_id === dagId);
      
      if (!dag) {
        throw new Error(`DAG with ID '${dagId}' not found`);
      }
      
      return dag;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  /**
   * Get DAG runs for a specific DAG (experimental API)
   */
  async getDagRuns(dagId: string, limit: number = 25): Promise<DagRun[]> {
    try {
      const endpoint = ENDPOINTS.DAG_RUNS.replace('{dag_id}', dagId);
      const response = await this.api.get<DagRunListResponse>(endpoint);
      
      // The experimental API returns an array directly, not wrapped in a data object
      return Array.isArray(response.data) ? response.data : [];
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  /**
   * Trigger a new DAG run
   */
  async triggerDag(dagId: string, config?: TriggerDagRequest): Promise<TriggerDagResponse> {
    try {
      const endpoint = ENDPOINTS.TRIGGER_DAG.replace('{dag_id}', dagId);
      const response = await this.api.post<TriggerDagResponse>(endpoint, config || {});
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  /**
   * Get task instances for a specific DAG run (experimental API)
   */
  async getTaskInstances(dagId: string, dagRunId: string): Promise<TaskInstance[]> {
    try {
      const endpoint = ENDPOINTS.TASK_INSTANCES
        .replace('{dag_id}', dagId)
        .replace('{dag_run_id}', dagRunId);
      const response = await this.api.get<TaskInstanceListResponse>(endpoint);
      
      // The experimental API returns an array directly
      return Array.isArray(response.data) ? response.data : [];
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }
}

export const airflowService = new AirflowService();