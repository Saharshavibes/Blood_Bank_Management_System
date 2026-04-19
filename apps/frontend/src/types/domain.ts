export const USER_ROLES = ["donor", "admin", "hospital"] as const;
export type UserRole = (typeof USER_ROLES)[number];

export const BLOOD_TYPES = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"] as const;
export type BloodType = (typeof BLOOD_TYPES)[number];

export const BLOOD_COMPONENTS = [
  "whole_blood",
  "packed_red_cells",
  "plasma",
  "platelets",
  "cryoprecipitate",
] as const;
export type BloodComponent = (typeof BLOOD_COMPONENTS)[number];

export const BLOOD_BAG_STATUSES = [
  "collected",
  "tested",
  "available",
  "reserved",
  "issued",
  "transfused",
  "discarded",
  "expired",
] as const;
export type BloodBagStatus = (typeof BLOOD_BAG_STATUSES)[number];

export const REQUEST_URGENCIES = ["routine", "urgent", "critical"] as const;
export type RequestUrgency = (typeof REQUEST_URGENCIES)[number];

export const REQUEST_STATUSES = ["pending", "partially_fulfilled", "fulfilled", "cancelled"] as const;
export type RequestStatus = (typeof REQUEST_STATUSES)[number];