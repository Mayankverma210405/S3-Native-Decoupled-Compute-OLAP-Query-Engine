import { Activity, Cloud, Database, Gauge, HardDrive, Rows3 } from "lucide-react";
import { useEffect, useState } from "react";

import { LatestQueryRuns } from "../components/LatestQueryRuns";
import { MetricCard } from "../components/MetricCard";
import { getDashboardSummary } from "../services/dashboardService";
import type { DashboardSummary } from "../types/dashboard";

export function DashboardPage() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    getDashboardSummary()
      .then(setSummary)
      .catch((err: unknown) => {
        setError(err instanceof Error ? err.message : "Could not load dashboard summary");
      });
  }, []);

  if (error) {
    return (
      <div className="rounded-3xl border border-rose-400/20 bg-rose-400/10 p-8 text-rose-100">
        <h2 className="text-xl font-semibold">Backend connection failed</h2>
        <p className="mt-2 text-sm text-rose-200/80">
          Start the FastAPI backend on port 8000, then refresh this page.
        </p>
        <pre className="mt-4 overflow-auto rounded-2xl bg-black/30 p-4 text-xs text-rose-100">
          {error}
        </pre>
      </div>
    );
  }

  if (!summary) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center text-slate-400">
        Loading dashboard metrics...
      </div>
    );
  }

  const averageTime =
    summary.average_execution_time_ms === null
      ? "—"
      : `${summary.average_execution_time_ms} ms`;

  return (
    <div className="space-y-8">
      <section className="overflow-hidden rounded-[2rem] border border-white/10 bg-white/[0.04] p-8 shadow-2xl shadow-black/30 backdrop-blur">
        <div className="max-w-3xl">
          <div className="inline-flex rounded-full border border-cyan-400/20 bg-cyan-400/10 px-3 py-1 text-sm text-cyan-200">
            Serverless-style analytics over raw CSV files in S3
          </div>

          <h2 className="mt-6 text-4xl font-semibold tracking-tight text-white md:text-5xl">
            Query S3 datasets with decoupled compute.
          </h2>

          <p className="mt-5 max-w-2xl text-base leading-7 text-slate-400">
            Upload CSV datasets to private S3 storage, track metadata in PostgreSQL,
            and execute SQL through DuckDB without moving data into a traditional database.
          </p>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard
          title="Datasets"
          value={summary.total_datasets.toLocaleString()}
          helper="Registered CSV datasets"
          icon={Database}
        />
        <MetricCard
          title="Total rows"
          value={summary.total_rows.toLocaleString()}
          helper="Rows discovered during CSV analysis"
          icon={Rows3}
        />
        <MetricCard
          title="Queries"
          value={summary.total_queries.toLocaleString()}
          helper={`${summary.successful_queries} successful / ${summary.failed_queries} failed`}
          icon={Activity}
        />
        <MetricCard
          title="Average time"
          value={averageTime}
          helper="Mean DuckDB execution latency"
          icon={Gauge}
        />
      </section>

      <section className="grid gap-4 lg:grid-cols-2">
        <MetricCard
          title="Storage backend"
          value={summary.storage_backend}
          helper="Active object storage implementation"
          icon={Cloud}
        />
        <MetricCard
          title="Stored data"
          value={`${summary.total_storage_mb} MB`}
          helper={`${summary.total_storage_bytes.toLocaleString()} bytes uploaded`}
          icon={HardDrive}
        />
      </section>

      <LatestQueryRuns runs={summary.latest_query_runs} />
    </div>
  );
}
