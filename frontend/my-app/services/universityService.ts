import { apiRequest } from "@/lib/api";

export type University = {
  university_id: number;
  university_name: string;
  location?: string;
  website?: string;
};

export type DegreeProgram = {
  program_id: number;
  university_id: number;
  program_name: string;
  degree_name?: string;
  stream_id?: number;
  duration_years?: number;
  description?: string;
};

export const universityService = {
  getUniversities() {
    return apiRequest<University[]>("/api/universities/");
  },

  getUniversityPrograms(universityId: number) {
    return apiRequest<DegreeProgram[]>(
      `/api/universities/${universityId}/programs`
    );
  },
};