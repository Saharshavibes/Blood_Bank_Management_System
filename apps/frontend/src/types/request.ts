import type { BloodComponent, BloodType, RequestStatus, RequestUrgency } from "@/types/domain";

export type { RequestStatus, RequestUrgency } from "@/types/domain";

export interface BloodRequest {
  id: string;
  request_number: string;
  hospital_id: string;
  blood_type: BloodType;
  component: BloodComponent;
  units_requested: number;
  urgency: RequestUrgency;
  status: RequestStatus;
  requested_at: string;
  fulfilled_at: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}
