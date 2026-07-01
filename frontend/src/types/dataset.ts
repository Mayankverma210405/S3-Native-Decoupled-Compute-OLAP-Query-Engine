export type DatasetSchema = Record<string, string>;

export type Dataset = {
  id: string;
  name: string;
  original_filename: string;
  s3_key: string;
  storage_format: string;
  content_type: string;
  file_size_bytes: number;
  row_count: number;
  column_count: number;
  schema_json?: DatasetSchema;
  dataset_schema?: DatasetSchema;
  status: string;
  query_count: number;
  last_query_at: string | null;
  created_at: string;
  updated_at: string;
};

export type DatasetListResponse = {
  items: Dataset[];
  count: number;
  limit: number;
  offset: number;
};

export type DatasetPreviewResponse = {
  dataset_id: string;
  columns: string[];
  rows: Record<string, unknown>[];
  row_count: number;
  limit: number;
  execution_time_ms: number;
};

export type DatasetDownloadUrlResponse = {
  dataset_id: string;
  object_key: string;
  download_url: string;
  expires_in_seconds: number;
  storage_backend: string;
};
