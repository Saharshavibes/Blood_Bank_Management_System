import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import axios from "axios";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { fetchMyDonorImpact } from "@/services/impact";
import { reportDegradedStateTransition } from "@/services/telemetry";
import { DegradedStateBanner } from "@/components/ui/DegradedStateBanner";
import type { DonorImpact } from "@/types/impact";

const SAMPLE_IMPACT: DonorImpact = {
  donor_id: "sample-donor",
  total_volume_ml: 1800,
  total_donations: 4,
  lives_impacted_estimate: 12,
  current_badge: "Silver Lifeline",
  next_badge: "Gold Lifeline",
  next_milestone_volume_ml: 3600,
  trends: [
    { month: "Nov 2025", volume_ml: 450, donations: 1 },
    { month: "Dec 2025", volume_ml: 0, donations: 0 },
    { month: "Jan 2026", volume_ml: 450, donations: 1 },
    { month: "Feb 2026", volume_ml: 450, donations: 1 },
    { month: "Mar 2026", volume_ml: 0, donations: 0 },
    { month: "Apr 2026", volume_ml: 450, donations: 1 },
  ],
  milestones: [
    { title: "First Lifeline", target_volume_ml: 450, achieved: true, achieved_at: "2025-11-02T08:00:00Z" },
    { title: "Bronze Lifeline", target_volume_ml: 900, achieved: true, achieved_at: "2026-01-10T09:20:00Z" },
    { title: "Silver Lifeline", target_volume_ml: 1800, achieved: true, achieved_at: "2026-04-01T07:10:00Z" },
    { title: "Gold Lifeline", target_volume_ml: 3600, achieved: false, achieved_at: null },
    { title: "Platinum Lifeline", target_volume_ml: 5400, achieved: false, achieved_at: null },
  ],
};

export function DonorImpactDashboard() {
  const [impact, setImpact] = useState<DonorImpact | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isDegraded, setIsDegraded] = useState(false);
  const [sourceLabel, setSourceLabel] = useState("live");
  const [reloadNonce, setReloadNonce] = useState(0);
  const previousDegradedState = useRef(false);

  useEffect(() => {
    const loadImpact = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const data = await fetchMyDonorImpact();
        setImpact(data);
        setSourceLabel("live");
        setIsDegraded(false);
      } catch (loadError) {
        setImpact(SAMPLE_IMPACT);
        setSourceLabel("sample");
        setIsDegraded(true);

        if (axios.isAxiosError(loadError)) {
          setError(loadError.response?.data?.detail ?? "Impact API is unavailable.");
        } else {
          setError("Impact API is unavailable.");
        }
      } finally {
        setIsLoading(false);
      }
    };

    void loadImpact();
  }, [reloadNonce]);

  const retryLiveData = useCallback(() => {
    setReloadNonce((value) => value + 1);
  }, []);

  useEffect(() => {
    if (previousDegradedState.current === isDegraded) {
      return;
    }

    previousDegradedState.current = isDegraded;
    void reportDegradedStateTransition({
      source: "donor_impact",
      state: isDegraded ? "degraded" : "recovered",
      message: error ?? undefined,
    });
  }, [error, isDegraded]);

  const progressPercent = useMemo(() => {
    if (!impact?.next_milestone_volume_ml) {
      return 100;
    }
    const previousMilestone = impact.milestones
      .filter((item) => item.achieved)
      .map((item) => item.target_volume_ml)
      .sort((a, b) => b - a)[0] ?? 0;

    const span = impact.next_milestone_volume_ml - previousMilestone;
    if (span <= 0) {
      return 100;
    }

    return Math.min(100, Math.round(((impact.total_volume_ml - previousMilestone) / span) * 100));
  }, [impact]);

  if (isLoading) {
    return <section className="glass-card p-6 text-sm text-black/65">Loading donor impact metrics...</section>;
  }

  if (!impact) {
    return <section className="glass-card p-6 text-sm text-rose-600">Unable to load donor impact data.</section>;
  }

  return (
    <div className="space-y-5">
      {isDegraded ? (
        <DegradedStateBanner
          title="Live impact analytics are temporarily unavailable"
          message={error ?? "Using sample donor impact metrics until connectivity is restored."}
          onRetry={retryLiveData}
          isRetrying={isLoading}
        />
      ) : null}

      <section className="grid gap-4 md:grid-cols-4">
        <article className="glass-card p-5">
          <p className="text-xs uppercase tracking-wide text-black/55">Total Volume</p>
          <p className="mt-2 text-3xl font-extrabold">{impact.total_volume_ml.toLocaleString()} ml</p>
        </article>
        <article className="glass-card p-5">
          <p className="text-xs uppercase tracking-wide text-black/55">Total Donations</p>
          <p className="mt-2 text-3xl font-extrabold">{impact.total_donations}</p>
        </article>
        <article className="glass-card p-5">
          <p className="text-xs uppercase tracking-wide text-black/55">Lives Impacted</p>
          <p className="mt-2 text-3xl font-extrabold">{impact.lives_impacted_estimate}</p>
        </article>
        <article className="glass-card p-5">
          <p className="text-xs uppercase tracking-wide text-black/55">Current Badge</p>
          <p className="mt-2 text-2xl font-extrabold">{impact.current_badge}</p>
          <p className="mt-2 text-xs text-black/60">source: {sourceLabel}</p>
        </article>
      </section>

      <section className="glass-card p-5">
        <div className="mb-3 flex items-center justify-between gap-3">
          <h3 className="text-lg font-bold">Milestone Progress</h3>
          {impact.next_badge ? (
            <span className="text-sm text-black/70">
              Next: {impact.next_badge} ({impact.next_milestone_volume_ml?.toLocaleString()} ml)
            </span>
          ) : (
            <span className="text-sm text-calm">Top milestone reached</span>
          )}
        </div>
        <div className="h-3 overflow-hidden rounded-full bg-black/10">
          <div className="h-full rounded-full bg-gradient-to-r from-calm to-accent" style={{ width: `${progressPercent}%` }} />
        </div>
      </section>

      <section className="grid gap-4 lg:grid-cols-2">
        <article className="glass-card p-5">
          <h3 className="mb-3 text-lg font-bold">Donation Volume Trend</h3>
          <div className="h-64 w-full">
            <ResponsiveContainer>
              <AreaChart data={impact.trends}>
                <defs>
                  <linearGradient id="impactArea" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#14b8a6" stopOpacity={0.55} />
                    <stop offset="95%" stopColor="#14b8a6" stopOpacity={0.05} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#d7e0e7" />
                <XAxis dataKey="month" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip />
                <Area type="monotone" dataKey="volume_ml" stroke="#0f766e" fill="url(#impactArea)" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </article>

        <article className="glass-card p-5">
          <h3 className="mb-3 text-lg font-bold">Donations per Month</h3>
          <div className="h-64 w-full">
            <ResponsiveContainer>
              <BarChart data={impact.trends}>
                <CartesianGrid strokeDasharray="3 3" stroke="#d7e0e7" />
                <XAxis dataKey="month" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="donations" fill="#f97316" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </article>
      </section>

      <section className="glass-card p-5">
        <h3 className="mb-3 text-lg font-bold">Milestone Ladder</h3>
        <div className="grid gap-2">
          {impact.milestones.map((milestone) => (
            <div
              key={milestone.title}
              className={`flex items-center justify-between rounded-xl border px-4 py-3 ${
                milestone.achieved ? "border-calm/30 bg-calm/10" : "border-black/10 bg-white"
              }`}
            >
              <div>
                <p className="text-sm font-semibold">{milestone.title}</p>
                <p className="text-xs text-black/60">Target {milestone.target_volume_ml.toLocaleString()} ml</p>
              </div>
              <span className={`pill ${milestone.achieved ? "bg-calm/20 text-calm" : "bg-black/10 text-black/70"}`}>
                {milestone.achieved ? "Achieved" : "In Progress"}
              </span>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
