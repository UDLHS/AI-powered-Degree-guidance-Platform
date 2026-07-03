import { apiRequest } from "@/lib/api";

type RegisterPayload = {
  name: string;
  email: string;
  password: string;
};

type LoginPayload = {
  email: string;
  password: string;
};

type AuthResponse = {
  access_token: string;
  token_type: string;
  user_id: string;
  name: string;
  email: string;
};

export const authService = {
  async register(payload: RegisterPayload) {
    const data = await apiRequest<AuthResponse>("/api/auth/register", {
      method: "POST",
      body: JSON.stringify(payload),
    });

    localStorage.setItem("student_access_token", data.access_token);
    return data;
  },

  async login(payload: LoginPayload) {
    const data = await apiRequest<AuthResponse>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify(payload),
    });

    localStorage.setItem("student_access_token", data.access_token);
    return data;
  },

  logout() {
    localStorage.removeItem("student_access_token");
  },
};