import { apiRequest } from "@/lib/api";

export const dashboardService = {
  getPublicSummary() {
    return apiRequest("/api/dashboard/public-summary");
  },

  getTopPrograms() {
    return apiRequest("/api/dashboard/top-programs");
  },
};