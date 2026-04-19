import apiClient from "@/lib/api";
import type { RoutingRecommendationResponse } from "@/types/routing";

export async function fetchNearestBanksForRequest(
  requestId: string,
  maxResults = 5,
): Promise<RoutingRecommendationResponse> {
  const { data } = await apiClient.get<RoutingRecommendationResponse>(`/requests/${requestId}/nearest-banks`, {
    params: {
      max_results: maxResults,
    },
  });
  return data;
}
