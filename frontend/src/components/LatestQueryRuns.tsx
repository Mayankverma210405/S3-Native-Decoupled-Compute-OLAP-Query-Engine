import type { LatestQueryRunSummary } from "../types/dashboard";
import { StatusPill } from "./StatusPill";

type LatestQueryRunsProps = {
  runs: LatestQueryRunSummary[];
};

export function LatestQueryRuns({ runs }: LatestQueryRunsProps) {
  return (
    <section className="rounded-3xl border border-white/10 bg-white/[0.045] p-6 shadow-2xl shadow-black/20 backdrop-blur">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-semibold text-white">Latest query runs</h2>
          <p className="mt-1 text-sm text-slate-400">
            Recent SQL executions captured from the backend observability layer.
          </p>
        </div>
      </div>

      <div className="mt-6 overflow-hidden rounded-2xl border border-white/10">
        <table className="w-full border-collapse text-left text-sm">
          <thead className="bg-white/[0.04] text-xs uppercase tracking-[0.18em] text-slate-500">
            <tr>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Rows</th>
              <th className="px-4 py-3">Time</th>
              <th className="px-4 py-3">Storage</th>
              <th className="px-4 py-3">SQL</th>
            </tr>
          </thead>

          <tbody className="divide-y divide-white/10">
            {runs.length === 0 ? (
              <tr>
                <td className="px-4 py-6 text-slate-400" colSpan={5}>
                  No query runs yet. Execute a query from the API to populate this table.
                </td>
              </tr>
            ) : (
              runs.map((run) => (
                <tr key={run.id} className="text-slate-300">
                  <td className="px-4 py-4">
                    <StatusPill status={run.status} />
                  </td>
                  <td className="px-4 py-4">{run.row_count}</td>
                  <td className="px-4 py-4">
                    {run.execution_time_ms === null ? "—" : `${run.execution_time_ms} ms`}
                  </td>
                  <td className="px-4 py-4">{run.storage_backend}</td>
                  <td className="max-w-xl truncate px-4 py-4 font-mono text-xs text-slate-400">
                    {run.sql_text}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
