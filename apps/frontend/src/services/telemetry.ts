import apiClient from "@/lib/api";
import type { DegradedStateEventPayload } from "@/types/telemetry";

export async function reportDegradedStateTransition(payload: DegradedStateEventPayload): Promise<void> {
  try {
    await apiClient.post("/telemetry/degraded-state", payload);
  } catch {
    return;
  }
}
