export type QueryRequest = {
  dataset_id: string;
  sql: string;
};

export type QueryResponse = {
  dataset_id: string;
  sql: string;
  columns: string[];
  rows: Record<string, unknown>[];
  row_count: number;
  execution_time_ms: number;
};

export type QueryExplainResponse = {
  dataset_id: string;
  sql: string;
  plan: Record<string, unknown>[];
  plan_text: string;
  execution_time_ms: number;
};

export type QueryRun = {
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

export type QueryRunListResponse = {
  items: QueryRun[];
  count: number;
  limit: number;
  offset: number;
};
