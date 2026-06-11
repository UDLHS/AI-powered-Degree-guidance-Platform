import { apiRequest } from "@/lib/api";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

type AdminLoginResponse = {
  access_token: string;
  token_type: string;
};

export const adminService = {
  async login(email: string, password: string) {
    const formData = new URLSearchParams();
    formData.append("username", email);
    formData.append("password", password);

    const response = await fetch(`${API_BASE_URL}/admin/token`, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: formData,
    });

    if (!response.ok) {
      throw new Error("Invalid admin email or password");
    }

    const data: AdminLoginResponse = await response.json();
    localStorage.setItem("admin_access_token", data.access_token);

    return data;
  },

  logout() {
    localStorage.removeItem("admin_access_token");
  },

  getMe() {
    return apiRequest<any>("/admin/me", {
      authType: "admin",
    });
  },

  getMetrics() {
    return apiRequest<any>("/admin/metrics", {
      authType: "admin",
    });
  },

  uploadHandbook(file: File) {
    const formData = new FormData();
    formData.append("file", file);

    return apiRequest<any>("/admin/upload-handbook", {
      method: "POST",
      authType: "admin",
      body: formData,
    });
  },

  getUploadedPDFs() {
    return apiRequest<any[]>("/admin/uploaded-pdfs", {
      authType: "admin",
    });
  },

  getOCRJobs() {
    return apiRequest<any[]>("/admin/ocr-jobs", {
      authType: "admin",
    });
  },
  getLiveStats() {
  return apiRequest<any>("/admin/live-stats", {
    authType: "admin",
  });
},

getStudentActivities() {
  return apiRequest<any[]>("/admin/student-activities", {
    authType: "admin",
  });
},
processOCRJob(jobId: string | number) {
  return apiRequest<any>(`/admin/ocr-jobs/${jobId}/process`, {
    method: "POST",
    authType: "admin",
  });
},


getExtractedRows(jobId: string | number) {
  return apiRequest<any[]>(`/admin/ocr-jobs/${jobId}/extracted-rows`, {
    authType: "admin",
  });
},

verifyExtractedRow(rowId: number) {
  return apiRequest<any>(`/admin/ocr-extracted-rows/${rowId}/verify`, {
    method: "PATCH",
    authType: "admin",
  });
},

updateExtractedRow(rowId: number, payload: any) {
  return apiRequest<any>(`/admin/ocr-extracted-rows/${rowId}`, {
    method: "PATCH",
    authType: "admin",
    body: JSON.stringify(payload),
  });
},

approveOCRJob(jobId: string | number) {
  return apiRequest<any>(`/admin/ocr-jobs/${jobId}/approve-to-cutoffs`, {
    method: "POST",
    authType: "admin",
  });
},
};