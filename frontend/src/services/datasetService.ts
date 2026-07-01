import { apiGet, apiPostForm } from "../api/client";
import type {
  Dataset,
  DatasetDownloadUrlResponse,
  DatasetListResponse,
  DatasetPreviewResponse
} from "../types/dataset";

export async function listDatasets(): Promise<DatasetListResponse> {
  const response = await apiGet<DatasetListResponse>(
    "/api/v1/datasets?limit=100&offset=0"
  );

  console.log("DATASETS API RESPONSE:", response);

  return {
    items: Array.isArray(response.items) ? response.items : [],
    count: response.count ?? 0,
    limit: response.limit ?? 100,
    offset: response.offset ?? 0
  };
}

export function uploadDataset(file: File, name?: string): Promise<Dataset> {
  const formData = new FormData();
  formData.append("file", file);

  if (name?.trim()) {
    formData.append("name", name.trim());
  }

  return apiPostForm<Dataset>("/api/v1/datasets/upload", formData);
}

export function previewDataset(
  datasetId: string,
  limit = 10
): Promise<DatasetPreviewResponse> {
  return apiGet<DatasetPreviewResponse>(
    `/api/v1/datasets/${datasetId}/preview?limit=${limit}`
  );
}

export function getDatasetDownloadUrl(
  datasetId: string,
  expiresInSeconds = 300
): Promise<DatasetDownloadUrlResponse> {
  return apiGet<DatasetDownloadUrlResponse>(
    `/api/v1/datasets/${datasetId}/download-url?expires_in_seconds=${expiresInSeconds}`
  );
}