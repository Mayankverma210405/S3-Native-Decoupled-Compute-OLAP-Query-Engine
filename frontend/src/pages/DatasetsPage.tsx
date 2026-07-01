import {
  ArrowDownToLine,
  Database,
  Eye,
  FileSpreadsheet,
  RefreshCw,
  UploadCloud
} from "lucide-react";
import type { ChangeEvent, FormEvent } from "react";
import { useEffect, useMemo, useState } from "react";

import {
  getDatasetDownloadUrl,
  listDatasets,
  previewDataset,
  uploadDataset
} from "../services/datasetService";
import type { Dataset, DatasetPreviewResponse, DatasetSchema } from "../types/dataset";

function formatBytes(bytes: number): string {
  if (bytes === 0) return "0 B";

  const units = ["B", "KB", "MB", "GB"];
  const index = Math.floor(Math.log(bytes) / Math.log(1024));
  const safeIndex = Math.min(index, units.length - 1);
  const value = bytes / 1024 ** safeIndex;

  return `${value.toFixed(value >= 10 ? 1 : 2)} ${units[safeIndex]}`;
}

function getSchema(dataset: Dataset): DatasetSchema {
  const rawSchema = dataset.schema_json ?? dataset.dataset_schema ?? {};

  if (!rawSchema || typeof rawSchema !== "object" || Array.isArray(rawSchema)) {
    return {};
  }

  const cleanedSchema: DatasetSchema = {};

  for (const [key, value] of Object.entries(rawSchema)) {
    cleanedSchema[String(key)] = String(value);
  }

  return cleanedSchema;
}

export function DatasetsPage() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [datasetName, setDatasetName] = useState("");
  const [preview, setPreview] = useState<DatasetPreviewResponse | null>(null);
  const [previewDatasetName, setPreviewDatasetName] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isUploading, setIsUploading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const totalRows = useMemo(
    () => datasets.reduce((sum, dataset) => sum + dataset.row_count, 0),
    [datasets]
  );

  const totalSize = useMemo(
    () => datasets.reduce((sum, dataset) => sum + dataset.file_size_bytes, 0),
    [datasets]
  );

  async function loadDatasets() {
    setError("");
    setIsLoading(true);

    try {
      const response = await listDatasets();
      setDatasets(response.items);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Could not load datasets");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void loadDatasets();
  }, []);

  function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0] ?? null;
    setSelectedFile(file);

    if (file && !datasetName.trim()) {
      setDatasetName(file.name.replace(/\.csv$/i, ""));
    }
  }

  async function handleUpload(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!selectedFile) {
      setError("Please choose a CSV file first.");
      return;
    }

    setError("");
    setMessage("");
    setIsUploading(true);

    try {
      const uploaded = await uploadDataset(selectedFile, datasetName);
      setMessage(`Uploaded ${uploaded.name} successfully to S3.`);
      setSelectedFile(null);
      setDatasetName("");
      setPreview(null);

      const fileInput = document.getElementById("dataset-file") as HTMLInputElement | null;
      if (fileInput) {
        fileInput.value = "";
      }

      await loadDatasets();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setIsUploading(false);
    }
  }

  async function handlePreview(dataset: Dataset) {
    setError("");
    setMessage("");

    try {
      const response = await previewDataset(dataset.id, 10);
      setPreview(response);
      setPreviewDatasetName(dataset.name);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Preview failed");
    }
  }

  async function handleDownload(dataset: Dataset) {
    setError("");
    setMessage("");

    try {
      const response = await getDatasetDownloadUrl(dataset.id, 300);
      window.open(response.download_url, "_blank", "noopener,noreferrer");
      setMessage(`Generated temporary download URL for ${dataset.name}.`);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Could not generate download URL");
    }
  }

  return (
    <div className="space-y-8">
      <section className="rounded-[2rem] border border-white/10 bg-white/[0.04] p-8 shadow-2xl shadow-black/30 backdrop-blur">
        <div className="flex flex-col justify-between gap-6 lg:flex-row lg:items-end">
          <div>
            <div className="inline-flex rounded-full border border-cyan-400/20 bg-cyan-400/10 px-3 py-1 text-sm text-cyan-200">
              Dataset catalog
            </div>

            <h2 className="mt-6 text-4xl font-semibold tracking-tight text-white">
              Upload, inspect, and query raw CSV files.
            </h2>

            <p className="mt-4 max-w-2xl text-slate-400">
              Every CSV is stored in private S3, analyzed for schema metadata, and made
              queryable through DuckDB without loading it into a traditional database.
            </p>
          </div>

          <div className="grid gap-3 sm:grid-cols-3 lg:min-w-[28rem]">
            <div className="rounded-2xl border border-white/10 bg-black/20 p-4">
              <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Datasets</p>
              <p className="mt-2 text-2xl font-semibold text-white">{datasets.length}</p>
            </div>

            <div className="rounded-2xl border border-white/10 bg-black/20 p-4">
              <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Rows</p>
              <p className="mt-2 text-2xl font-semibold text-white">
                {totalRows.toLocaleString()}
              </p>
            </div>

            <div className="rounded-2xl border border-white/10 bg-black/20 p-4">
              <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Size</p>
              <p className="mt-2 text-2xl font-semibold text-white">
                {formatBytes(totalSize)}
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-6 lg:grid-cols-[0.85fr_1.15fr]">
        <form
          onSubmit={handleUpload}
          className="rounded-3xl border border-white/10 bg-white/[0.045] p-6 shadow-2xl shadow-black/20 backdrop-blur"
        >
          <div className="flex items-center gap-3">
            <div className="rounded-2xl border border-cyan-400/20 bg-cyan-400/10 p-3 text-cyan-300">
              <UploadCloud size={22} />
            </div>
            <div>
              <h3 className="font-semibold text-white">Upload CSV</h3>
              <p className="text-sm text-slate-400">Store dataset object in S3.</p>
            </div>
          </div>

          <label className="mt-6 block text-sm text-slate-300" htmlFor="dataset-file">
            CSV file
          </label>
          <input
            id="dataset-file"
            type="file"
            accept=".csv,text/csv"
            onChange={handleFileChange}
            className="mt-2 w-full rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-slate-300 file:mr-4 file:rounded-full file:border-0 file:bg-white file:px-4 file:py-2 file:text-sm file:font-medium file:text-slate-950"
          />

          <label className="mt-5 block text-sm text-slate-300" htmlFor="dataset-name">
            Dataset name
          </label>
          <input
            id="dataset-name"
            value={datasetName}
            onChange={(event) => setDatasetName(event.target.value)}
            placeholder="sales_analytics_q2"
            className="mt-2 w-full rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-white outline-none transition placeholder:text-slate-600 focus:border-cyan-300/50"
          />

          <button
            type="submit"
            disabled={isUploading}
            className="mt-6 inline-flex w-full items-center justify-center gap-2 rounded-2xl bg-white px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-100 disabled:cursor-not-allowed disabled:opacity-60"
          >
            <UploadCloud size={18} />
            {isUploading ? "Uploading..." : "Upload to S3"}
          </button>

          {message ? (
            <p className="mt-4 rounded-2xl border border-emerald-400/20 bg-emerald-400/10 p-3 text-sm text-emerald-200">
              {message}
            </p>
          ) : null}

          {error ? (
            <p className="mt-4 rounded-2xl border border-rose-400/20 bg-rose-400/10 p-3 text-sm text-rose-200">
              {error}
            </p>
          ) : null}
        </form>

        <section className="rounded-3xl border border-white/10 bg-white/[0.045] p-6 shadow-2xl shadow-black/20 backdrop-blur">
          <div className="flex items-center justify-between gap-4">
            <div>
              <h3 className="font-semibold text-white">Registered datasets</h3>
              <p className="mt-1 text-sm text-slate-400">
                Metadata catalog backed by PostgreSQL.
              </p>
            </div>

            <button
              type="button"
              onClick={() => void loadDatasets()}
              className="inline-flex items-center gap-2 rounded-full border border-white/10 px-4 py-2 text-sm text-slate-300 transition hover:bg-white/10 hover:text-white"
            >
              <RefreshCw size={16} />
              Refresh
            </button>
          </div>

          <div className="mt-6 max-h-[32rem] space-y-3 overflow-auto pr-1">
            {isLoading ? (
              <p className="rounded-2xl border border-white/10 p-5 text-slate-400">
                Loading datasets...
              </p>
            ) : datasets.length === 0 ? (
              <p className="rounded-2xl border border-white/10 p-5 text-slate-400">
                No datasets yet. Upload your first CSV file.
              </p>
            ) : (
              datasets.map((dataset) => {
                const schema = getSchema(dataset);
                const schemaEntries = Object.entries(schema).slice(0, 4);

                return (
                  <article
                    key={dataset.id}
                    className="rounded-2xl border border-white/10 bg-slate-950/40 p-4"
                  >
                    <div className="flex flex-col justify-between gap-4 xl:flex-row xl:items-start">
                      <div>
                        <div className="flex items-center gap-3">
                          <div className="rounded-xl border border-cyan-400/20 bg-cyan-400/10 p-2 text-cyan-300">
                            <FileSpreadsheet size={18} />
                          </div>
                          <div>
                            <h4 className="font-semibold text-white">{dataset.name}</h4>
                            <p className="mt-0.5 text-xs text-slate-500">
                              {dataset.original_filename}
                            </p>
                          </div>
                        </div>

                        <div className="mt-4 flex flex-wrap gap-2 text-xs text-slate-400">
                          <span className="rounded-full bg-white/5 px-3 py-1">
                            {dataset.row_count.toLocaleString()} rows
                          </span>
                          <span className="rounded-full bg-white/5 px-3 py-1">
                            {dataset.column_count} columns
                          </span>
                          <span className="rounded-full bg-white/5 px-3 py-1">
                            {formatBytes(dataset.file_size_bytes)}
                          </span>
                          <span className="rounded-full bg-white/5 px-3 py-1">
                            {dataset.query_count} queries
                          </span>
                        </div>

                        <div className="mt-4 flex flex-wrap gap-2">
                          {schemaEntries.map(([column, type]) => (
                            <span
                              key={column}
                              className="rounded-full border border-white/10 px-3 py-1 text-xs text-slate-400"
                            >
                              <span className="text-slate-200">{column}</span> · {type}
                            </span>
                          ))}
                        </div>
                      </div>

                      <div className="flex gap-2">
                        <button
                          type="button"
                          onClick={() => void handlePreview(dataset)}
                          className="inline-flex items-center gap-2 rounded-full border border-white/10 px-4 py-2 text-sm text-slate-300 transition hover:bg-white/10 hover:text-white"
                        >
                          <Eye size={16} />
                          Preview
                        </button>

                        <button
                          type="button"
                          onClick={() => void handleDownload(dataset)}
                          className="inline-flex items-center gap-2 rounded-full bg-white px-4 py-2 text-sm font-medium text-slate-950 transition hover:bg-cyan-100"
                        >
                          <ArrowDownToLine size={16} />
                          Download
                        </button>
                      </div>
                    </div>
                  </article>
                );
              })
            )}
          </div>
        </section>
      </section>

      <section className="rounded-3xl border border-white/10 bg-white/[0.045] p-6 shadow-2xl shadow-black/20 backdrop-blur">
        <div className="flex items-center gap-3">
          <div className="rounded-2xl border border-cyan-400/20 bg-cyan-400/10 p-3 text-cyan-300">
            <Database size={22} />
          </div>
          <div>
            <h3 className="font-semibold text-white">Dataset preview</h3>
            <p className="text-sm text-slate-400">
              {preview
                ? `Showing ${preview.row_count} rows from ${previewDatasetName}`
                : "Choose a dataset and click Preview."}
            </p>
          </div>
        </div>

        <div className="mt-6 overflow-hidden rounded-2xl border border-white/10">
          {!preview ? (
            <div className="p-6 text-sm text-slate-400">
              No preview selected yet.
            </div>
          ) : (
            <div className="overflow-auto">
              <table className="w-full border-collapse text-left text-sm">
                <thead className="bg-white/[0.04] text-xs uppercase tracking-[0.18em] text-slate-500">
                  <tr>
                    {preview.columns.map((column) => (
                      <th key={column} className="px-4 py-3">
                        {column}
                      </th>
                    ))}
                  </tr>
                </thead>

                <tbody className="divide-y divide-white/10">
                  {preview.rows.map((row, index) => (
                    <tr key={index} className="text-slate-300">
                      {preview.columns.map((column) => (
                        <td key={column} className="px-4 py-4">
                          {String(row[column] ?? "")}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </section>
    </div>
  );
}
