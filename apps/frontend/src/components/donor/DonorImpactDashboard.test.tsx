import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, beforeEach, vi } from "vitest";

const impactServiceMocks = vi.hoisted(() => ({
  fetchMyDonorImpact: vi.fn(),
}));

const telemetryServiceMocks = vi.hoisted(() => ({
  reportDegradedStateTransition: vi.fn(),
}));

vi.mock("@/services/impact", () => ({
  fetchMyDonorImpact: impactServiceMocks.fetchMyDonorImpact,
}));

vi.mock("@/services/telemetry", () => ({
  reportDegradedStateTransition: telemetryServiceMocks.reportDegradedStateTransition,
}));

vi.mock("recharts", () => {
  const MockChartPrimitive = () => null;

  return {
    Area: MockChartPrimitive,
    AreaChart: MockChartPrimitive,
    Bar: MockChartPrimitive,
    BarChart: MockChartPrimitive,
    CartesianGrid: MockChartPrimitive,
    ResponsiveContainer: MockChartPrimitive,
    Tooltip: MockChartPrimitive,
    XAxis: MockChartPrimitive,
    YAxis: MockChartPrimitive,
  };
});

import { DonorImpactDashboard } from "@/components/donor/DonorImpactDashboard";

const LIVE_IMPACT = {
  donor_id: "donor-1",
  total_volume_ml: 2200,
  total_donations: 5,
  lives_impacted_estimate: 15,
  current_badge: "Silver Lifeline",
  next_badge: "Gold Lifeline",
  next_milestone_volume_ml: 3600,
  trends: [
    { month: "Mar 2026", volume_ml: 450, donations: 1 },
    { month: "Apr 2026", volume_ml: 450, donations: 1 },
  ],
  milestones: [
    { title: "First Lifeline", target_volume_ml: 450, achieved: true, achieved_at: "2026-01-10T00:00:00Z" },
    { title: "Gold Lifeline", target_volume_ml: 3600, achieved: false, achieved_at: null },
  ],
};

describe("DonorImpactDashboard", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    telemetryServiceMocks.reportDegradedStateTransition.mockResolvedValue(undefined);
  });

  it("retries live data after degraded fallback and emits degraded transitions", async () => {
    impactServiceMocks.fetchMyDonorImpact
      .mockRejectedValueOnce(new Error("impact api offline"))
      .mockResolvedValueOnce(LIVE_IMPACT);

    render(<DonorImpactDashboard />);

    await screen.findByText("Live impact analytics are temporarily unavailable");

    await waitFor(() => {
      expect(telemetryServiceMocks.reportDegradedStateTransition).toHaveBeenCalledWith(
        expect.objectContaining({ source: "donor_impact", state: "degraded" }),
      );
    });

    await userEvent.click(screen.getByRole("button", { name: /retry live data/i }));

    await waitFor(() => {
      expect(impactServiceMocks.fetchMyDonorImpact).toHaveBeenCalledTimes(2);
    });

    await waitFor(() => {
      expect(screen.queryByText("Live impact analytics are temporarily unavailable")).not.toBeInTheDocument();
    });

    await waitFor(() => {
      expect(telemetryServiceMocks.reportDegradedStateTransition).toHaveBeenCalledWith(
        expect.objectContaining({ source: "donor_impact", state: "recovered" }),
      );
    });

    expect(screen.getByText(/source: live/i)).toBeInTheDocument();
  });
});
