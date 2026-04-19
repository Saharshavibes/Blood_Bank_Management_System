import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, beforeEach, vi } from "vitest";

const routingServiceMocks = vi.hoisted(() => ({
  fetchNearestBanksForRequest: vi.fn(),
}));

const telemetryServiceMocks = vi.hoisted(() => ({
  reportDegradedStateTransition: vi.fn(),
}));

vi.mock("@/services/routing", () => ({
  fetchNearestBanksForRequest: routingServiceMocks.fetchNearestBanksForRequest,
}));

vi.mock("@/services/telemetry", () => ({
  reportDegradedStateTransition: telemetryServiceMocks.reportDegradedStateTransition,
}));

vi.mock("@/components/maps/UrgentRoutingMap", () => ({
  UrgentRoutingMap: () => <div data-testid="routing-map" />,
}));

import { HospitalUrgentPage } from "@/pages/hospital/HospitalUrgentPage";

const ROUTING_RESULT = {
  request_id: "request-1",
  request_number: "REQ-2026-0042",
  urgency: "critical",
  units_requested: 3,
  requesting_hospital: {
    hospital_id: "hospital-9",
    hospital_name: "General Hospital",
    city: "Cairo",
    latitude: 30.0444,
    longitude: 31.2357,
  },
  candidates: [
    {
      source_hospital_id: "hospital-1",
      source_hospital_name: "City Blood Bank",
      source_city: "Giza",
      latitude: 30.0131,
      longitude: 31.2089,
      distance_km: 8.5,
      available_units: 5,
      available_volume_ml: 2250,
    },
  ],
};

describe("HospitalUrgentPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    telemetryServiceMocks.reportDegradedStateTransition.mockResolvedValue(undefined);
  });

  it("retries urgent routing lookup after degraded failure and emits recovery", async () => {
    routingServiceMocks.fetchNearestBanksForRequest
      .mockRejectedValueOnce(new Error("routing api offline"))
      .mockResolvedValueOnce(ROUTING_RESULT);

    render(<HospitalUrgentPage />);

    await userEvent.type(screen.getByLabelText(/urgent request id/i), "request-1");
    await userEvent.click(screen.getByRole("button", { name: /find nearest blood banks/i }));

    await screen.findByText("Routing recommendations are temporarily degraded");

    await waitFor(() => {
      expect(telemetryServiceMocks.reportDegradedStateTransition).toHaveBeenCalledWith(
        expect.objectContaining({ source: "urgent_routing", state: "degraded" }),
      );
    });

    await userEvent.click(screen.getByRole("button", { name: /retry live data/i }));

    await waitFor(() => {
      expect(routingServiceMocks.fetchNearestBanksForRequest).toHaveBeenCalledTimes(2);
    });

    expect(routingServiceMocks.fetchNearestBanksForRequest).toHaveBeenNthCalledWith(1, "request-1");
    expect(routingServiceMocks.fetchNearestBanksForRequest).toHaveBeenNthCalledWith(2, "request-1");

    await waitFor(() => {
      expect(screen.queryByText("Routing recommendations are temporarily degraded")).not.toBeInTheDocument();
    });

    await waitFor(() => {
      expect(telemetryServiceMocks.reportDegradedStateTransition).toHaveBeenCalledWith(
        expect.objectContaining({ source: "urgent_routing", state: "recovered" }),
      );
    });

    expect(screen.getByText(/request req-2026-0042/i)).toBeInTheDocument();
    expect(screen.getByTestId("routing-map")).toBeInTheDocument();
  });
});
