export type SystemOverview = {
  project_name: string;
  api_version: string;
  environment: string;
  debug: boolean;
  status: string;
  storage_backend: string;
  aws_region: string;
  s3_configured: boolean;
  database_configured: boolean;
  total_datasets: number;
  total_query_runs: number;
};