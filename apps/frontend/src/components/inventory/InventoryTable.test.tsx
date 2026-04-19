import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, beforeEach, vi } from "vitest";

const apiClientMocks = vi.hoisted(() => ({
  get: vi.fn(),
}));

const telemetryServiceMocks = vi.hoisted(() => ({
  reportDegradedStateTransition: vi.fn(),
}));

vi.mock("@/lib/api", () => ({
  default: {
    get: apiClientMocks.get,
  },
}));

vi.mock("@/services/telemetry", () => ({
  reportDegradedStateTransition: telemetryServiceMocks.reportDegradedStateTransition,
}));

import { InventoryTable } from "@/components/inventory/InventoryTable";

const LIVE_BAGS = [
  {
    id: "bag-1",
    bag_number: "BB-20260418-0001",
    donor_id: "donor-1",
    storage_hospital_id: "hospital-1",
    blood_request_id: null,
    blood_type: "O+",
    component: "packed_red_cells",
    volume_ml: 450,
    collection_date: "2026-04-12T00:00:00Z",
    expiration_date: "2026-05-20T00:00:00Z",
    status: "available",
    created_at: "2026-04-12T00:00:00Z",
    updated_at: "2026-04-12T00:00:00Z",
  },
];

describe("InventoryTable", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    telemetryServiceMocks.reportDegradedStateTransition.mockResolvedValue(undefined);
  });

  it("retries live inventory after degraded fallback and reports recovery", async () => {
    apiClientMocks.get
      .mockRejectedValueOnce(new Error("inventory api offline"))
      .mockResolvedValueOnce({ data: LIVE_BAGS });

    render(<InventoryTable />);

    await screen.findByText("Live inventory feed is unavailable");

    await waitFor(() => {
      expect(telemetryServiceMocks.reportDegradedStateTransition).toHaveBeenCalledWith(
        expect.objectContaining({ source: "inventory", state: "degraded" }),
      );
    });

    await userEvent.click(screen.getByRole("button", { name: /retry live data/i }));

    await waitFor(() => {
      expect(apiClientMocks.get).toHaveBeenCalledTimes(2);
    });

    await waitFor(() => {
      expect(screen.queryByText("Live inventory feed is unavailable")).not.toBeInTheDocument();
    });

    await waitFor(() => {
      expect(telemetryServiceMocks.reportDegradedStateTransition).toHaveBeenCalledWith(
        expect.objectContaining({ source: "inventory", state: "recovered" }),
      );
    });

    expect(screen.getByText(/source: live/i)).toBeInTheDocument();
  });
});
