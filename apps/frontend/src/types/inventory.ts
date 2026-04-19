import type { BloodBagStatus, BloodComponent, BloodType } from "@/types/domain";

export type { BloodBagStatus } from "@/types/domain";

export interface BloodBag {
  id: string;
  bag_number: string;
  donor_id: string;
  storage_hospital_id: string | null;
  blood_request_id: string | null;
  blood_type: BloodType;
  component: BloodComponent;
  volume_ml: number;
  collection_date: string;
  expiration_date: string;
  status: BloodBagStatus;
  created_at: string;
  updated_at: string;
}
