import type { LucideIcon } from "lucide-react";

type MetricCardProps = {
  title: string;
  value: string;
  helper: string;
  icon: LucideIcon;
};

export function MetricCard({ title, value, helper, icon: Icon }: MetricCardProps) {
  return (
    <div className="rounded-3xl border border-white/10 bg-white/[0.045] p-5 shadow-2xl shadow-black/20 backdrop-blur">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm text-slate-400">{title}</p>
          <p className="mt-3 text-3xl font-semibold tracking-tight text-white">{value}</p>
        </div>

        <div className="rounded-2xl border border-cyan-400/20 bg-cyan-400/10 p-3 text-cyan-300">
          <Icon size={20} />
        </div>
      </div>

      <p className="mt-4 text-sm text-slate-500">{helper}</p>
    </div>
  );
}
