export interface DonorTrendPoint {
  month: string;
  volume_ml: number;
  donations: number;
}

export interface DonorMilestone {
  title: string;
  target_volume_ml: number;
  achieved: boolean;
  achieved_at: string | null;
}

export interface DonorImpact {
  donor_id: string;
  total_volume_ml: number;
  total_donations: number;
  lives_impacted_estimate: number;
  current_badge: string;
  next_badge: string | null;
  next_milestone_volume_ml: number | null;
  trends: DonorTrendPoint[];
  milestones: DonorMilestone[];
}
