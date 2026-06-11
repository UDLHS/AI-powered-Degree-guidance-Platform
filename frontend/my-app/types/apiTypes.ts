export type AuthResponse = {
  access_token: string;
  token_type: string;
  user_id?: string;
  admin_id?: string;
  name?: string;
  email?: string;
};

export type RegisterPayload = {
  name: string;
  email: string;
  password: string;
};

export type LoginPayload = {
  email: string;
  password: string;
};

export type AcademicProfilePayload = {
  stream_id: number;
  district_id: number;
  z_score: number;
  subject_ids: number[];
  field_ids: number[];
};

export type RecommendationPayload = {
  stream_id: number;
  subject_ids: number[];
  district_id: number;
  z_score: number;
  field_ids?: number[];
  min_job_demand_score?: number;
  max_pending_margin?: number;
  result_type?: "BEST" | "PENDING" | "ALL";
};

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
  category: string;
};