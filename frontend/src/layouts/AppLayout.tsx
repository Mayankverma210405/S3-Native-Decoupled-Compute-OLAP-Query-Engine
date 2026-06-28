import { BarChart3, Database, SearchCode, Server } from "lucide-react";
import type { ReactNode } from "react";

type AppLayoutProps = {
  children: ReactNode;
};

const navItems = [
  { label: "Dashboard", icon: BarChart3, active: true },
  { label: "Datasets", icon: Database, active: false },
  { label: "Query Console", icon: SearchCode, active: false },
  { label: "System", icon: Server, active: false }
];

export function AppLayout({ children }: AppLayoutProps) {
  return (
    <div className="min-h-screen">
      <header className="sticky top-0 z-20 border-b border-white/10 bg-slate-950/70 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <div>
            <p className="text-xs uppercase tracking-[0.35em] text-cyan-300">
              S3 Native
            </p>
            <h1 className="mt-1 text-lg font-semibold tracking-tight text-white">
              Decoupled Compute OLAP Engine
            </h1>
          </div>

          <nav className="hidden items-center gap-2 md:flex">
            {navItems.map((item) => {
              const Icon = item.icon;

              return (
                <button
                  key={item.label}
                  className={[
                    "flex items-center gap-2 rounded-full px-4 py-2 text-sm transition",
                    item.active
                      ? "bg-white text-slate-950"
                      : "text-slate-400 hover:bg-white/10 hover:text-white"
                  ].join(" ")}
                >
                  <Icon size={16} />
                  {item.label}
                </button>
              );
            })}
          </nav>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-6 py-8">{children}</main>
    </div>
  );
}
