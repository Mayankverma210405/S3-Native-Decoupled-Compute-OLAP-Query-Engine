import {
  Braces,
  Clock,
  Database,
  FileSearch,
  Play,
  RefreshCw,
  Rows3,
  TerminalSquare
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { listDatasets } from "../services/datasetService";
import { executeQuery, explainQuery, listQueryRuns } from "../services/queryService";
import type { Dataset } from "../types/dataset";
import type { QueryExplainResponse, QueryResponse, QueryRun } from "../types/query";

const DEFAULT_SQL = "SELECT * FROM dataset LIMIT 20";

function formatDate(value: string): string {
  return new Date(value).toLocaleString();
}

function formatCell(value: unknown): string {
  if (value === null || value === undefined) {
    return "";
  }

  if (typeof value === "object") {
    return JSON.stringify(value);
  }

  return String(value);
}

export function QueryConsolePage() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [selectedDatasetId, setSelectedDatasetId] = useState("");
  const [sql, setSql] = useState(DEFAULT_SQL);
  const [result, setResult] = useState<QueryResponse | null>(null);
  const [explain, setExplain] = useState<QueryExplainResponse | null>(null);
  const [queryRuns, setQueryRuns] = useState<QueryRun[]>([]);
  const [isLoadingDatasets, setIsLoadingDatasets] = useState(true);
  const [isExecuting, setIsExecuting] = useState(false);
  const [isExplaining, setIsExplaining] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const selectedDataset = useMemo(
    () => datasets.find((dataset) => dataset.id === selectedDatasetId) ?? null,
    [datasets, selectedDatasetId]
  );

  async function loadInitialData() {
    setError("");
    setIsLoadingDatasets(true);

    try {
      const [datasetResponse, runsResponse] = await Promise.all([
        listDatasets(),
        listQueryRuns(5)
      ]);

      setDatasets(datasetResponse.items);
      setQueryRuns(runsResponse.items);

      if (!selectedDatasetId && datasetResponse.items.length > 0) {
        setSelectedDatasetId(datasetResponse.items[0].id);
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Could not load query console data");
    } finally {
      setIsLoadingDatasets(false);
    }
  }

  async function refreshQueryRuns() {
    try {
      const runsResponse = await listQueryRuns(5);
      setQueryRuns(runsResponse.items);
    } catch {
      // Keep the main query flow usable even if history refresh fails.
    }
  }

  useEffect(() => {
    void loadInitialData();
    // We intentionally load once on first render.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function handleExecute() {
    if (!selectedDatasetId) {
      setError("Select a dataset before running SQL.");
      return;
    }

    if (!sql.trim()) {
      setError("SQL cannot be empty.");
      return;
    }

    setError("");
    setMessage("");
    setResult(null);
    setExplain(null);
    setIsExecuting(true);

    try {
      const response = await executeQuery({
        dataset_id: selectedDatasetId,
        sql
      });

      setResult(response);
      setMessage(`Query returned ${response.row_count} rows in ${response.execution_time_ms} ms.`);
      await refreshQueryRuns();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Query execution failed");
    } finally {
      setIsExecuting(false);
    }
  }

  async function handleExplain() {
    if (!selectedDatasetId) {
      setError("Select a dataset before explaining SQL.");
      return;
    }

    if (!sql.trim()) {
      setError("SQL cannot be empty.");
      return;
    }

    setError("");
    setMessage("");
    setExplain(null);
    setIsExplaining(true);

    try {
      const response = await explainQuery({
        dataset_id: selectedDatasetId,
        sql
      });

      setExplain(response);
      setMessage(`EXPLAIN completed in ${response.execution_time_ms} ms.`);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "EXPLAIN failed");
    } finally {
      setIsExplaining(false);
    }
  }

  return (
    <div className="space-y-8">
      <section className="rounded-[2rem] border border-white/10 bg-white/[0.04] p-8 shadow-2xl shadow-black/30 backdrop-blur">
        <div className="flex flex-col justify-between gap-6 lg:flex-row lg:items-end">
          <div>
            <div className="inline-flex rounded-full border border-cyan-400/20 bg-cyan-400/10 px-3 py-1 text-sm text-cyan-200">
              Interactive SQL console
            </div>

            <h2 className="mt-6 text-4xl font-semibold tracking-tight text-white">
              Run SQL directly over S3-backed CSV datasets.
            </h2>

            <p className="mt-4 max-w-2xl text-slate-400">
              Select a registered dataset, write read-only SQL against the virtual table
              named <span className="font-mono text-cyan-200">dataset</span>, and inspect
              results or DuckDB query plans from the browser.
            </p>
          </div>

          <div className="grid gap-3 sm:grid-cols-3 lg:min-w-[32rem]">
            <div className="rounded-2xl border border-white/10 bg-black/20 p-4">
              <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Datasets</p>
              <p className="mt-2 text-2xl font-semibold text-white">{datasets.length}</p>
            </div>

            <div className="rounded-2xl border border-white/10 bg-black/20 p-4">
              <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Selected</p>
              <p className="mt-2 truncate text-lg font-semibold text-white">
                {selectedDataset ? selectedDataset.name : "None"}
              </p>
            </div>

            <div className="rounded-2xl border border-white/10 bg-black/20 p-4">
              <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Rows</p>
              <p className="mt-2 text-2xl font-semibold text-white">
                {selectedDataset ? selectedDataset.row_count.toLocaleString() : "—"}
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
        <div className="space-y-6">
          <section className="rounded-3xl border border-white/10 bg-white/[0.045] p-6 shadow-2xl shadow-black/20 backdrop-blur">
            <div className="flex items-center gap-3">
              <div className="rounded-2xl border border-cyan-400/20 bg-cyan-400/10 p-3 text-cyan-300">
                <Database size={22} />
              </div>
              <div>
                <h3 className="font-semibold text-white">Dataset selector</h3>
                <p className="text-sm text-slate-400">Choose which CSV should be exposed as the table named dataset.</p>
              </div>
            </div>

            <select
              value={selectedDatasetId}
              onChange={(event) => setSelectedDatasetId(event.target.value)}
              disabled={isLoadingDatasets || datasets.length === 0}
              className="mt-6 w-full rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-white outline-none transition focus:border-cyan-300/50"
            >
              {datasets.length === 0 ? (
                <option value="">No datasets available</option>
              ) : (
                datasets.map((dataset) => (
                  <option key={dataset.id} value={dataset.id}>
                    {dataset.name} · {dataset.row_count} rows · {dataset.column_count} columns
                  </option>
                ))
              )}
            </select>

            {selectedDataset ? (
              <div className="mt-4 grid gap-3 sm:grid-cols-3">
                <div className="rounded-2xl border border-white/10 bg-black/20 p-4">
                  <p className="text-xs text-slate-500">File</p>
                  <p className="mt-1 truncate text-sm text-white">{selectedDataset.original_filename}</p>
                </div>
                <div className="rounded-2xl border border-white/10 bg-black/20 p-4">
                  <p className="text-xs text-slate-500">Queries</p>
                  <p className="mt-1 text-sm text-white">{selectedDataset.query_count}</p>
                </div>
                <div className="rounded-2xl border border-white/10 bg-black/20 p-4">
                  <p className="text-xs text-slate-500">Status</p>
                  <p className="mt-1 text-sm text-white">{selectedDataset.status}</p>
                </div>
              </div>
            ) : null}
          </section>

          <section className="rounded-3xl border border-white/10 bg-white/[0.045] p-6 shadow-2xl shadow-black/20 backdrop-blur">
            <div className="flex items-center gap-3">
              <div className="rounded-2xl border border-cyan-400/20 bg-cyan-400/10 p-3 text-cyan-300">
                <TerminalSquare size={22} />
              </div>
              <div>
                <h3 className="font-semibold text-white">SQL editor</h3>
                <p className="text-sm text-slate-400">Only SELECT/WITH queries are accepted by the backend.</p>
              </div>
            </div>

            <textarea
              value={sql}
              onChange={(event) => setSql(event.target.value)}
              spellCheck={false}
              className="mt-6 min-h-56 w-full resize-y rounded-2xl border border-white/10 bg-slate-950/80 p-4 font-mono text-sm leading-6 text-cyan-50 outline-none transition placeholder:text-slate-600 focus:border-cyan-300/50"
              placeholder="SELECT * FROM dataset LIMIT 20"
            />

            <div className="mt-4 flex flex-wrap gap-3">
              <button
                type="button"
                onClick={() => void handleExecute()}
                disabled={isExecuting || datasets.length === 0}
                className="inline-flex items-center gap-2 rounded-2xl bg-white px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-100 disabled:cursor-not-allowed disabled:opacity-60"
              >
                <Play size={18} />
                {isExecuting ? "Executing..." : "Execute query"}
              </button>

              <button
                type="button"
                onClick={() => void handleExplain()}
                disabled={isExplaining || datasets.length === 0}
                className="inline-flex items-center gap-2 rounded-2xl border border-white/10 px-5 py-3 text-sm font-semibold text-slate-200 transition hover:bg-white/10 hover:text-white disabled:cursor-not-allowed disabled:opacity-60"
              >
                <FileSearch size={18} />
                {isExplaining ? "Explaining..." : "EXPLAIN"}
              </button>

              <button
                type="button"
                onClick={() => setSql(DEFAULT_SQL)}
                className="inline-flex items-center gap-2 rounded-2xl border border-white/10 px-5 py-3 text-sm text-slate-300 transition hover:bg-white/10 hover:text-white"
              >
                Reset SQL
              </button>
            </div>

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
          </section>
        </div>

        <section className="rounded-3xl border border-white/10 bg-white/[0.045] p-6 shadow-2xl shadow-black/20 backdrop-blur">
          <div className="flex items-center gap-3">
            <div className="rounded-2xl border border-cyan-400/20 bg-cyan-400/10 p-3 text-cyan-300">
              <Rows3 size={22} />
            </div>
            <div>
              <h3 className="font-semibold text-white">Query results</h3>
              <p className="text-sm text-slate-400">
                {result
                  ? `${result.row_count} rows returned in ${result.execution_time_ms} ms`
                  : "Execute SQL to view result rows."}
              </p>
            </div>
          </div>

          <div className="mt-6 overflow-hidden rounded-2xl border border-white/10">
            {!result ? (
              <div className="p-6 text-sm text-slate-400">
                No query result yet.
              </div>
            ) : result.rows.length === 0 ? (
              <div className="p-6 text-sm text-slate-400">
                Query executed successfully but returned no rows.
              </div>
            ) : (
              <div className="max-h-[31rem] overflow-auto">
                <table className="w-full border-collapse text-left text-sm">
                  <thead className="sticky top-0 bg-slate-950 text-xs uppercase tracking-[0.18em] text-slate-500">
                    <tr>
                      {result.columns.map((column) => (
                        <th key={column} className="whitespace-nowrap px-4 py-3">
                          {column}
                        </th>
                      ))}
                    </tr>
                  </thead>

                  <tbody className="divide-y divide-white/10">
                    {result.rows.map((row, index) => (
                      <tr key={index} className="text-slate-300">
                        {result.columns.map((column) => (
                          <td key={column} className="whitespace-nowrap px-4 py-4">
                            {formatCell(row[column])}
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
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <section className="rounded-3xl border border-white/10 bg-white/[0.045] p-6 shadow-2xl shadow-black/20 backdrop-blur">
          <div className="flex items-center gap-3">
            <div className="rounded-2xl border border-cyan-400/20 bg-cyan-400/10 p-3 text-cyan-300">
              <Braces size={22} />
            </div>
            <div>
              <h3 className="font-semibold text-white">EXPLAIN plan</h3>
              <p className="text-sm text-slate-400">
                Inspect DuckDB's physical query plan for the current SQL.
              </p>
            </div>
          </div>

          <pre className="mt-6 max-h-96 overflow-auto rounded-2xl border border-white/10 bg-slate-950/80 p-4 text-xs leading-6 text-slate-300">
            {explain?.plan_text || "Run EXPLAIN to view the query plan."}
          </pre>
        </section>

        <section className="rounded-3xl border border-white/10 bg-white/[0.045] p-6 shadow-2xl shadow-black/20 backdrop-blur">
          <div className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="rounded-2xl border border-cyan-400/20 bg-cyan-400/10 p-3 text-cyan-300">
                <Clock size={22} />
              </div>
              <div>
                <h3 className="font-semibold text-white">Recent runs</h3>
                <p className="text-sm text-slate-400">Latest persisted query executions.</p>
              </div>
            </div>

            <button
              type="button"
              onClick={() => void refreshQueryRuns()}
              className="inline-flex items-center gap-2 rounded-full border border-white/10 px-4 py-2 text-sm text-slate-300 transition hover:bg-white/10 hover:text-white"
            >
              <RefreshCw size={16} />
              Refresh
            </button>
          </div>

          <div className="mt-6 space-y-3">
            {queryRuns.length === 0 ? (
              <p className="rounded-2xl border border-white/10 p-5 text-sm text-slate-400">
                No query runs yet.
              </p>
            ) : (
              queryRuns.map((run) => (
                <article
                  key={run.id}
                  className="rounded-2xl border border-white/10 bg-slate-950/40 p-4"
                >
                  <div className="flex items-center justify-between gap-3">
                    <span className="rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-1 text-xs font-medium text-emerald-300">
                      {run.status}
                    </span>
                    <span className="text-xs text-slate-500">
                      {formatDate(run.created_at)}
                    </span>
                  </div>

                  <p className="mt-3 truncate font-mono text-xs text-slate-400">
                    {run.sql_text}
                  </p>

                  <div className="mt-3 flex flex-wrap gap-2 text-xs text-slate-500">
                    <span>{run.row_count} rows</span>
                    <span>·</span>
                    <span>
                      {run.execution_time_ms === null ? "—" : `${run.execution_time_ms} ms`}
                    </span>
                    <span>·</span>
                    <span>{run.storage_backend}</span>
                  </div>
                </article>
              ))
            )}
          </div>
        </section>
      </section>
    </div>
  );
}
