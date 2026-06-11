import { apiRequest } from "@/lib/api";

export type RecommendationItem = {
  result_id?: string | number;
  program_id?: number;
  university_id?: number;
  program_name?: string;
  university_name?: string;
  degree_name?: string;
  match_score?: number;
  cutoff_mark?: number;
  z_score?: number;
  eligibility_status?: string;
  result_type?: string;
  pending_margin?: number;
  explanation?: string;
};

export const recommendationService = {
  generateFromProfile(profileId: string) {
    return apiRequest<any>(`/api/recommendations/from-profile/${profileId}`, {
      method: "POST",
      authType: "student",
    });
  },

  getMyResults(profileId: string) {
    return apiRequest<any>(`/api/recommendations/my-results/${profileId}`, {
      authType: "student",
    });
  },
};