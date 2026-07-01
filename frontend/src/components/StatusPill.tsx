type StatusPillProps = {
  status: string;
};

export function StatusPill({ status }: StatusPillProps) {
  const isSuccess = status.toLowerCase() === "success";

  return (
    <span
      className={[
        "inline-flex rounded-full border px-2.5 py-1 text-xs font-medium",
        isSuccess
          ? "border-emerald-400/25 bg-emerald-400/10 text-emerald-300"
          : "border-rose-400/25 bg-rose-400/10 text-rose-300"
      ].join(" ")}
    >
      {status}
    </span>
  );
}
