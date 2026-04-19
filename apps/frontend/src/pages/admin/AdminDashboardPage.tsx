const snapshots = [
  { label: "Active Donors", value: "2,318", delta: "+4.2% week" },
  { label: "Usable Bags", value: "764", delta: "42 expiring in 5 days" },
  { label: "Urgent Requests", value: "19", delta: "5 critical" },
];

export function AdminDashboardPage() {
  return (
    <div className="space-y-5">
      <section className="glass-card p-6">
        <p className="text-xs font-mono uppercase tracking-[0.18em] text-black/50">Control Center</p>
        <h2 className="mt-2 text-2xl font-extrabold tracking-tight">National Blood Flow Overview</h2>
        <p className="mt-2 max-w-2xl text-sm text-black/65">
          Monitor donor throughput, inventory resilience, and urgent demand signals in one operational cockpit.
        </p>
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        {snapshots.map((item, index) => (
          <article
            key={item.label}
            className="glass-card p-5"
            style={{ animationDelay: `${index * 80}ms` }}
          >
            <p className="text-xs uppercase tracking-wide text-black/55">{item.label}</p>
            <p className="mt-2 text-3xl font-extrabold">{item.value}</p>
            <p className="mt-2 text-sm text-calm">{item.delta}</p>
          </article>
        ))}
      </section>
    </div>
  );
}
