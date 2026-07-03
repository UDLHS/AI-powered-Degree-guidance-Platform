import { apiRequest } from "@/lib/api";

export type RecommendationItem = {
  result_id?: string | number;

  program_id?: number;
  university_id?: number;

  program_name?: string;
  university_name?: string;
  degree_name?: string;
  location?: string;

  duration_years?: number;
  syllabus_summary?: string;
  job_demand_score?: number;
  ugc_link?: string;

  match_score?: number;
  match_type?: string;
  eligibility_status?: string;
  result_type?: string;

  cutoff_mark?: number | null;
  raw_cutoff_mark?: string | null;
  cutoff_status?: "QUALIFIED" | "NQC" | "MISSING" | string | null;
  is_nqc?: boolean;

  z_score?: number;
  margin?: number;
  pending_margin?: number;
  rank?: number;

  explanation?: string;
  created_at?: string;

  latest_cutoff?: {
    year?: number | null;
    cutoff_mark?: number | null;
    raw_cutoff_mark?: string | null;
    cutoff_status?: string | null;
    is_nqc?: boolean;
  };
};

export type RecommendationSummaryProfile = {
  profile_id: string;
  stream_name: string;
  district_name: string;
  z_score: number;
  total_results: number;
  best_count: number;
  pending_count: number;
  created_at: string;
};

export type RecommendationSummaryResponse = {
  user: {
    user_id: string;
    name: string;
    email: string;
  };
  total_profiles: number;
  profiles: RecommendationSummaryProfile[];
};

export type RecommendationResultByProfileResponse = {
  profile: {
    profile_id: string;
    stream_id: number;
    district_id: number;
    z_score: number;
    created_at: string;
  };
  total_results: number;
  best_matching: RecommendationItem[];
  pending_borderline: RecommendationItem[];
};

export type DirectRecommendationPayload = {
  stream_id: number;
  district_id: number;
  z_score: number;
  field_ids?: number[];
  min_job_demand_score?: number;
  max_pending_margin?: number;
  result_type?: string;
};

export const recommendationService = {
  generateFromProfile(profileId: string) {
    return apiRequest<any>(`/api/recommendations/from-profile/${profileId}`, {
      method: "POST",
      authType: "student",
    });
  },

  getMyResultsSummary() {
    return apiRequest<RecommendationSummaryResponse>("/api/recommendations/my-results", {
      authType: "student",
    });
  },

  getMyResults(profileId: string) {
    return apiRequest<RecommendationResultByProfileResponse>(
      `/api/recommendations/my-results/${profileId}`,
      {
        authType: "student",
      }
    );
  },

  getHistory(profileId: string) {
    return apiRequest<RecommendationItem[]>(
      `/api/recommendations/history/${profileId}`,
      {
        authType: "student",
      }
    );
  },

  deleteMyResults(profileId: string) {
    return apiRequest<{
      message: string;
      profile_id: string;
      deleted_count: number;
    }>(`/api/recommendations/my-results/${profileId}`, {
      method: "DELETE",
      authType: "student",
    });
  },

  generateDirect(payload: DirectRecommendationPayload) {
    return apiRequest<any>("/api/recommendations/", {
      method: "POST",
      body: JSON.stringify({
        stream_id: payload.stream_id,
        district_id: payload.district_id,
        z_score: payload.z_score,
        field_ids: payload.field_ids ?? [],
        min_job_demand_score: payload.min_job_demand_score,
        max_pending_margin: payload.max_pending_margin,
        result_type: payload.result_type,
      }),
    });
  },
};

