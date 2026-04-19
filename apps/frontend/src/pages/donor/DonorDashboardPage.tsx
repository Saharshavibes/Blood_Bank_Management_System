import { DonorImpactDashboard } from "@/components/donor/DonorImpactDashboard";

export function DonorDashboardPage() {
  return (
    <div className="space-y-5">
      <section className="glass-card p-6">
        <p className="text-xs font-mono uppercase tracking-[0.18em] text-black/50">Donor Impact</p>
        <h2 className="mt-2 text-2xl font-extrabold">Your Donation Story</h2>
        <p className="mt-2 text-sm text-black/65">
          Track monthly donation momentum, lives impacted, and milestone progress with your personal impact timeline.
        </p>
      </section>

      <DonorImpactDashboard />
    </div>
  );
}
