import {
  Activity,
  Cloud,
  Database,
  Gauge,
  Lock,
  Server,
  Settings,
  ShieldCheck
} from "lucide-react";
import { useEffect, useState } from "react";

import { getSystemOverview } from "../services/systemService";
import type { SystemOverview } from "../types/system";

type SystemCardProps = {
  label: string;
  value: string;
  helper: string;
  icon: typeof Server;
};

function SystemCard({ label, value, helper, icon: Icon }: SystemCardProps) {
  return (
    <div className="rounded-3xl border border-white/10 bg-white/[0.045] p-5 shadow-2xl shadow-black/20 backdrop-blur">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm text-slate-400">{label}</p>
          <p className="mt-3 text-2xl font-semibold tracking-tight text-white">{value}</p>
        </div>

        <div className="rounded-2xl border border-cyan-400/20 bg-cyan-400/10 p-3 text-cyan-300">
          <Icon size={20} />
        </div>
      </div>

      <p className="mt-4 text-sm text-slate-500">{helper}</p>
    </div>
  );
}

function boolLabel(value: boolean): string {
  return value ? "Configured" : "Not configured";
}

export function SystemPage() {
  const [overview, setOverview] = useState<SystemOverview | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getSystemOverview()
      .then(setOverview)
      .catch((err: unknown) => {
        setError(err instanceof Error ? err.message : "Could not load system overview");
      });
  }, []);

  if (error) {
    return (
      <div className="rounded-3xl border border-rose-400/20 bg-rose-400/10 p-8 text-rose-100">
        <h2 className="text-xl font-semibold">System overview failed</h2>
        <p className="mt-2 text-sm text-rose-200/80">
          The frontend could not load backend system information.
        </p>
        <pre className="mt-4 overflow-auto rounded-2xl bg-black/30 p-4 text-xs text-rose-100">
          {error}
        </pre>
      </div>
    );
  }

  if (!overview) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center text-slate-400">
        Loading system overview...
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <section className="rounded-[2rem] border border-white/10 bg-white/[0.04] p-8 shadow-2xl shadow-black/30 backdrop-blur">
        <div className="max-w-3xl">
          <div className="inline-flex rounded-full border border-cyan-400/20 bg-cyan-400/10 px-3 py-1 text-sm text-cyan-200">
            System overview
          </div>

          <h2 className="mt-6 text-4xl font-semibold tracking-tight text-white">
            Runtime health, configuration, and storage mode.
          </h2>

          <p className="mt-4 max-w-2xl text-slate-400">
            This page exposes safe operational metadata for the demo without revealing
            secrets, access keys, or private credentials.
          </p>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <SystemCard
          label="Backend status"
          value={overview.status}
          helper="FastAPI application state"
          icon={Activity}
        />
        <SystemCard
          label="Environment"
          value={overview.environment}
          helper={overview.debug ? "Debug mode enabled" : "Debug mode disabled"}
          icon={Settings}
        />
        <SystemCard
          label="API version"
          value={overview.api_version}
          helper={overview.project_name}
          icon={Server}
        />
        <SystemCard
          label="AWS region"
          value={overview.aws_region}
          helper="Configured object storage region"
          icon={Cloud}
        />
      </section>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <SystemCard
          label="Storage backend"
          value={overview.storage_backend}
          helper="Active object storage implementation"
          icon={Database}
        />
        <SystemCard
          label="S3 configuration"
          value={boolLabel(overview.s3_configured)}
          helper="Bucket value exists in backend config"
          icon={ShieldCheck}
        />
        <SystemCard
          label="Database"
          value={boolLabel(overview.database_configured)}
          helper="PostgreSQL connection string loaded"
          icon={Lock}
        />
        <SystemCard
          label="Catalog activity"
          value={`${overview.total_datasets} datasets`}
          helper={`${overview.total_query_runs} query runs recorded`}
          icon={Gauge}
        />
      </section>

      <section className="rounded-3xl border border-white/10 bg-white/[0.045] p-6 shadow-2xl shadow-black/20 backdrop-blur">
        <h3 className="text-lg font-semibold text-white">Security posture</h3>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">
          The frontend displays only safe runtime metadata. AWS access keys, secret keys,
          database passwords, and private bucket names are intentionally not exposed through
          this endpoint.
        </p>

        <div className="mt-6 grid gap-3 md:grid-cols-3">
          <div className="rounded-2xl border border-white/10 bg-black/20 p-4">
            <p className="text-sm font-medium text-white">Private object storage</p>
            <p className="mt-2 text-sm text-slate-500">
              Dataset objects are stored behind the backend storage abstraction.
            </p>
          </div>

          <div className="rounded-2xl border border-white/10 bg-black/20 p-4">
            <p className="text-sm font-medium text-white">No secret exposure</p>
            <p className="mt-2 text-sm text-slate-500">
              Credentials stay inside backend environment variables.
            </p>
          </div>

          <div className="rounded-2xl border border-white/10 bg-black/20 p-4">
            <p className="text-sm font-medium text-white">Read-only query layer</p>
            <p className="mt-2 text-sm text-slate-500">
              The query engine accepts SELECT/WITH queries only in v1.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}