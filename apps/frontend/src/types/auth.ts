import type { BloodType, UserRole } from "@/types/domain";

export type { UserRole } from "@/types/domain";

export interface AuthUser {
  id: string;
  email: string;
  role: UserRole;
  donor_id: string | null;
  hospital_id: string | null;
  is_active: boolean;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_at: string;
  refresh_token: string;
  refresh_expires_at: string;
  user: AuthUser;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface DonorRegisterPayload {
  email: string;
  password: string;
  full_name: string;
  phone: string;
  date_of_birth: string;
  blood_type: BloodType;
  medical_history?: string;
}

export interface HospitalRegisterPayload {
  email: string;
  password: string;
  name: string;
  address: string;
  city: string;
  latitude?: number;
  longitude?: number;
  contact_phone: string;
}
