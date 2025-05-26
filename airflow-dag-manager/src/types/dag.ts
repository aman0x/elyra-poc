export interface Dag {
    dag_id: string;
    description?: string;
    file_token: string;
    fileloc: string;
    is_active: boolean;
    is_paused: boolean;
    last_parsed_time?: string;
    last_pickled?: string;
    last_expired?: string;
    scheduler_lock?: boolean;
    pickle_id?: number;
    default_view?: string;
    orientation?: string;
    tags?: string[];
    owners?: string[];
    start_date?: string;
    end_date?: string;
    max_active_tasks?: number;
    max_active_runs?: number;
    has_task_concurrency_limits?: boolean;
    has_import_errors?: boolean;
    next_dagrun?: string;
    next_dagrun_data_interval_start?: string;
    next_dagrun_data_interval_end?: string;
    next_dagrun_create_after?: string;
  }
  
  export interface DagRun {
    dag_run_id: string;
    dag_id: string;
    execution_date: string;
    start_date?: string;
    end_date?: string;
    state: 'running' | 'success' | 'failed' | 'queued';
    external_trigger: boolean;
    conf?: any;
  }
  
  export interface TaskInstance {
    task_id: string;
    dag_id: string;
    execution_date: string;
    start_date?: string;
    end_date?: string;
    duration?: number;
    state?: 'running' | 'success' | 'failed' | 'queued' | 'skipped';
    try_number?: number;
    max_tries?: number;
    hostname?: string;
    unixname?: string;
    job_id?: number;
    pool?: string;
    queue?: string;
    priority_weight?: number;
    operator?: string;
    queued_dttm?: string;
    pid?: number;
    executor_config?: any;
  }