export const DEGRADED_STATE_SOURCES = ["donor_impact", "inventory", "urgent_routing"] as const;
export type DegradedStateSource = (typeof DEGRADED_STATE_SOURCES)[number];

export const DEGRADED_STATES = ["degraded", "recovered"] as const;
export type DegradedState = (typeof DEGRADED_STATES)[number];

export interface DegradedStateEventPayload {
  source: DegradedStateSource;
  state: DegradedState;
  message?: string;
}
