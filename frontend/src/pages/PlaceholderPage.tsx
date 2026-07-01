type PlaceholderPageProps = {
  title: string;
  description: string;
};

export function PlaceholderPage({ title, description }: PlaceholderPageProps) {
  return (
    <section className="rounded-[2rem] border border-white/10 bg-white/[0.04] p-8 shadow-2xl shadow-black/30 backdrop-blur">
      <div className="inline-flex rounded-full border border-cyan-400/20 bg-cyan-400/10 px-3 py-1 text-sm text-cyan-200">
        Coming next
      </div>

      <h2 className="mt-6 text-4xl font-semibold tracking-tight text-white">
        {title}
      </h2>

      <p className="mt-4 max-w-2xl text-slate-400">{description}</p>
    </section>
  );
}
