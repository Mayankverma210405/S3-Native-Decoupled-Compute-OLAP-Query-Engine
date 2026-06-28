export type LatestQueryRunSummary = {
  id: string;
  dataset_id: string;
  sql_text: string;
  status: string;
  storage_backend: string;
  row_count: number;
  execution_time_ms: number | null;
  error_message: string | null;
  created_at: string;
};

export type DashboardSummary = {
  total_datasets: number;
  total_rows: number;
  total_storage_bytes: number;
  total_storage_mb: number;
  total_queries: number;
  successful_queries: number;
  failed_queries: number;
  average_execution_time_ms: number | null;
  storage_backend: string;
  latest_query_runs: LatestQueryRunSummary[];
};
