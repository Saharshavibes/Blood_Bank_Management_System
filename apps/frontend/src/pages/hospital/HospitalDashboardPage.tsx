const queue = [
  { type: "Critical", value: "3" },
  { type: "Urgent", value: "7" },
  { type: "Routine", value: "14" },
];

export function HospitalDashboardPage() {
  return (
    <div className="space-y-5">
      <section className="glass-card p-6">
        <p className="text-xs font-mono uppercase tracking-[0.18em] text-black/50">Hospital Portal</p>
        <h2 className="mt-2 text-2xl font-extrabold">Request Coordination Board</h2>
        <p className="mt-2 text-sm text-black/65">
          Manage routine and urgent blood requests with role-protected API workflows.
        </p>
      </section>

      <section className="grid gap-4 sm:grid-cols-3">
        {queue.map((item) => (
          <article key={item.type} className="glass-card p-5">
            <p className="text-xs uppercase tracking-wide text-black/55">{item.type}</p>
            <p className="mt-2 text-3xl font-extrabold">{item.value}</p>
          </article>
        ))}
      </section>
    </div>
  );
}
