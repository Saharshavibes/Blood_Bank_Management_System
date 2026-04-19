import apiClient from "@/lib/api";
import type { DonorImpact } from "@/types/impact";

export async function fetchMyDonorImpact(): Promise<DonorImpact> {
  const { data } = await apiClient.get<DonorImpact>("/donors/me/impact");
  return data;
}
