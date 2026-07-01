import { apiGet, apiPostJson } from "../api/client";
import type {
  QueryExplainResponse,
  QueryRequest,
  QueryResponse,
  QueryRunListResponse
} from "../types/query";

export function executeQuery(payload: QueryRequest): Promise<QueryResponse> {
  return apiPostJson<QueryResponse, QueryRequest>("/api/v1/queries/execute", payload);
}

export function explainQuery(payload: QueryRequest): Promise<QueryExplainResponse> {
  return apiPostJson<QueryExplainResponse, QueryRequest>("/api/v1/queries/explain", payload);
}

export function listQueryRuns(limit = 5): Promise<QueryRunListResponse> {
  return apiGet<QueryRunListResponse>(`/api/v1/queries/runs?limit=${limit}`);
}
