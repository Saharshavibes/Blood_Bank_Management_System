import type { RequestUrgency } from "@/types/domain";

export type { RequestUrgency } from "@/types/domain";

export interface RoutingHospitalPoint {
  hospital_id: string;
  hospital_name: string;
  city: string;
  latitude: number;
  longitude: number;
}

export interface RoutingCandidate {
  source_hospital_id: string;
  source_hospital_name: string;
  source_city: string;
  latitude: number;
  longitude: number;
  distance_km: number;
  available_units: number;
  available_volume_ml: number;
}

export interface RoutingRecommendationResponse {
  request_id: string;
  request_number: string;
  urgency: RequestUrgency;
  units_requested: number;
  requesting_hospital: RoutingHospitalPoint;
  candidates: RoutingCandidate[];
}
