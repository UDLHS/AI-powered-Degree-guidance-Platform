import { apiRequest } from "@/lib/api";

export type Stream = {
  stream_id: number;
  stream_name: string;
  description?: string;
};

export type Subject = {
  subject_id: number;
  stream_id: number;
  subject_name: string;
};

export type District = {
  district_id: number;
  district_name: string;
  province: string;
};

export type FieldOfInterest = {
  field_id: number;
  field_name: string;
  category?: string;
};

export type AcademicProfilePayload = {
  stream_id: number;
  district_id: number;
  z_score: number;
  subject_ids: number[];
  field_ids: number[];
};

export const profileService = {
  getStreams() {
    return apiRequest<Stream[]>("/api/profiles/streams");
  },

  getSubjectsByStream(streamId: number) {
    return apiRequest<Subject[]>(`/api/profiles/streams/${streamId}/subjects`);
  },

  getDistricts() {
    return apiRequest<District[]>("/api/profiles/districts");
  },

  getFieldsOfInterest() {
    return apiRequest<FieldOfInterest[]>("/api/profiles/fields-of-interest");
  },

  createProfile(payload: AcademicProfilePayload) {
    return apiRequest<{ profile_id: string; message: string }>("/api/profiles/", {
      method: "POST",
      authType: "student",
      body: JSON.stringify(payload),
    });
  },
};