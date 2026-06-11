"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { adminService } from "@/services/adminService";

export default function AdminDashboardPage() {
  const router = useRouter();

  const [metrics, setMetrics] = useState<any>(null);
  const [pdfs, setPdfs] = useState<any[]>([]);
  const [jobs, setJobs] = useState<any[]>([]);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const [liveStats, setLiveStats] = useState<any>(null);
  const [activities, setActivities] = useState<any[]>([]);

  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  async function loadDashboard() {
    try {
      setLoading(true);
      setError("");

      const [metricsData, pdfData, jobData] = await Promise.all([
        adminService.getMetrics(),
        adminService.getUploadedPDFs(),
        adminService.getOCRJobs(),
      ]);

      setMetrics(metricsData);
      setPdfs(Array.isArray(pdfData) ? pdfData : []);
      setJobs(Array.isArray(jobData) ? jobData : []);
    } catch (err: any) {
      setError(err.message || "Failed to load admin dashboard.");
    } finally {
      setLoading(false);
    }
  }

  async function loadLiveData() {
    try {
      const data = await adminService.getLiveStats();

      setLiveStats(data);
      setActivities(
        Array.isArray(data.recent_activities)
          ? data.recent_activities
          : []
      );
    } catch (err) {
      console.log("Live update failed", err);
    }
  }

  useEffect(() => {
    async function checkAdminAndLoad() {
      const token = localStorage.getItem("admin_access_token");

      if (!token) {
        router.push("/admin/login");
        return;
      }

      try {
        await adminService.getMe();
        await loadDashboard();
        await loadLiveData();
      } catch {
        localStorage.removeItem("admin_access_token");
        router.push("/admin/login");
      }
    }

    checkAdminAndLoad();
  }, [router]);

  useEffect(() => {
    const interval = setInterval(() => {
      const token = localStorage.getItem("admin_access_token");

      if (token) {
        loadLiveData();
      }
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  async function handleUpload(e: React.FormEvent) {
    e.preventDefault();

    if (!selectedFile) {
      setError("Please select a PDF file.");
      return;
    }

    try {
      setUploading(true);
      setError("");
      setMessage("");

      await adminService.uploadHandbook(selectedFile);

      setMessage("PDF uploaded successfully.");
      setSelectedFile(null);

      await loadDashboard();
      await loadLiveData();
    } catch (err: any) {
      setError(err.message || "PDF upload failed.");
    } finally {
      setUploading(false);
    }
  }

  function logout() {
    adminService.logout();
    router.push("/admin/login");
  }

  function formatAction(action: string) {
    return action
      .replaceAll("_", " ")
      .toLowerCase()
      .replace(/\b\w/g, (char) => char.toUpperCase());
  }

  function getActionBadge(action: string) {
    if (action.includes("REGISTERED")) {
      return "bg-green-950 border-green-700 text-green-300";
    }

    if (action.includes("LOGGED_IN")) {
      return "bg-blue-950 border-blue-700 text-blue-300";
    }

    if (action.includes("PROFILE")) {
      return "bg-violet-950 border-violet-700 text-violet-300";
    }

    if (action.includes("RECOMMENDATION")) {
      return "bg-yellow-950 border-yellow-700 text-yellow-300";
    }

    return "bg-slate-800 border-slate-600 text-slate-300";
  }
  async function processOCRJob(jobId: string | number) {
  try {
    setError("");
    setMessage("Processing OCR job. Please wait...");

    await adminService.processOCRJob(jobId);

    setMessage("OCR processing completed successfully.");
    await loadDashboard();
    await loadLiveData();
  } catch (err: any) {
    setError(err.message || "OCR processing failed.");
  }
}

  return (
    <main className="min-h-screen bg-slate-950 text-white">
      <nav className="border-b border-slate-800 bg-slate-950/80 backdrop-blur">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold">Admin Dashboard</h1>
            <p className="text-xs text-slate-400">
              AI Degree Guidance Platform
            </p>
          </div>

          <button
            onClick={logout}
            className="bg-red-600 hover:bg-red-700 px-4 py-2 rounded-lg text-sm font-medium"
          >
            Logout
          </button>
        </div>
      </nav>

      <section className="max-w-6xl mx-auto px-6 py-10">
        <div className="bg-gradient-to-r from-violet-900 to-blue-900 border border-slate-700 rounded-3xl p-8 shadow-2xl mb-8">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-5">
            <div>
              <h1 className="text-4xl font-extrabold mb-3">
                Admin Control Center
              </h1>

              <p className="text-blue-100 max-w-2xl">
                Monitor student activity in near real-time, upload UGC handbook
                PDFs, manage OCR jobs and track recommendation activity.
              </p>
            </div>

            <div className="flex items-center gap-2 bg-green-950 border border-green-700 text-green-300 px-4 py-2 rounded-full text-sm">
              <span className="h-2 w-2 bg-green-400 rounded-full animate-pulse"></span>
              Live Updating
            </div>
          </div>
        </div>

        {error && (
          <div className="bg-red-950 border border-red-700 text-red-300 rounded-2xl p-4 mb-6">
            {error}
          </div>
        )}

        {message && (
          <div className="bg-green-950 border border-green-700 text-green-300 rounded-2xl p-4 mb-6">
            {message}
          </div>
        )}

        {loading ? (
          <div className="bg-slate-900 border border-slate-700 rounded-2xl p-6 text-slate-300">
            Loading dashboard...
          </div>
        ) : (
          <>
            <div className="grid md:grid-cols-4 gap-5 mb-8">
              <div className="bg-slate-900 border border-slate-700 rounded-2xl p-5">
                <p className="text-slate-400 text-sm">Students</p>
                <h2 className="text-3xl font-bold mt-2">
                  {liveStats?.total_students ?? metrics?.total_users ?? 0}
                </h2>
              </div>

              <div className="bg-slate-900 border border-slate-700 rounded-2xl p-5">
                <p className="text-slate-400 text-sm">Profiles Created</p>
                <h2 className="text-3xl font-bold mt-2">
                  {liveStats?.total_profiles ?? metrics?.total_profiles ?? 0}
                </h2>
              </div>

              <div className="bg-slate-900 border border-slate-700 rounded-2xl p-5">
                <p className="text-slate-400 text-sm">Recommendations</p>
                <h2 className="text-3xl font-bold mt-2">
                  {liveStats?.total_recommendations ??
                    metrics?.total_recommendations ??
                    0}
                </h2>
              </div>

              <div className="bg-slate-900 border border-slate-700 rounded-2xl p-5">
                <p className="text-slate-400 text-sm">Logins Last 24h</p>
                <h2 className="text-3xl font-bold mt-2">
                  {liveStats?.logins_last_24h ?? 0}
                </h2>
              </div>
            </div>

            <div className="bg-slate-900 border border-slate-700 rounded-3xl p-6 shadow-lg mb-8">
              <div className="flex items-center justify-between mb-5">
                <div>
                  <h2 className="text-2xl font-bold">
                    Live Student Activity
                  </h2>
                  <p className="text-slate-400 text-sm">
                    Student registrations, logins, profile creation and
                    recommendation generation update every 5 seconds.
                  </p>
                </div>

                <button
                  onClick={loadLiveData}
                  className="bg-slate-800 hover:bg-slate-700 border border-slate-600 px-4 py-2 rounded-lg text-sm"
                >
                  Refresh
                </button>
              </div>

              {activities.length === 0 ? (
                <p className="text-slate-400">No student activity yet.</p>
              ) : (
                <div className="space-y-3">
                  {activities.map((activity) => (
                    <div
                      key={activity.log_id}
                      className="bg-slate-800 border border-slate-700 rounded-2xl p-4"
                    >
                      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
                        <div>
                          <div
                            className={`inline-flex border rounded-full px-3 py-1 text-xs font-medium mb-2 ${getActionBadge(
                              activity.action
                            )}`}
                          >
                            {formatAction(activity.action)}
                          </div>

                          <p className="text-white font-semibold">
                            {activity.details?.name ||
                              activity.details?.email ||
                              "Student Activity"}
                          </p>

                          <p className="text-slate-400 text-sm">
                            {activity.details?.email || activity.user_id}
                          </p>
                        </div>
                        <p className="text-slate-500 text-sm">
                          {activity.created_at
                            ? new Date(activity.created_at).toLocaleString()
                            : "N/A"}
                        </p>
                      </div>

                      {activity.details && (
                        <div className="grid md:grid-cols-3 gap-3 mt-4">
                          {activity.details.profile_id && (
                            <div className="bg-slate-950 border border-slate-700 rounded-xl p-3">
                              <p className="text-slate-500 text-xs">
                                Profile ID
                              </p>
                              <p className="text-slate-300 text-sm break-all">
                                {activity.details.profile_id}
                              </p>
                            </div>
                          )}

                          {activity.details.z_score && (
                            <div className="bg-slate-950 border border-slate-700 rounded-xl p-3">
                              <p className="text-slate-500 text-xs">Z-score</p>
                              <p className="text-slate-300 text-sm">
                                {activity.details.z_score}
                              </p>
                            </div>
                          )}

                          {activity.details.total_results !== undefined && (
                            <div className="bg-slate-950 border border-slate-700 rounded-xl p-3">
                              <p className="text-slate-500 text-xs">
                                Total Results
                              </p>
                              <p className="text-slate-300 text-sm">
                                {activity.details.total_results}
                              </p>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="grid lg:grid-cols-2 gap-6">
              <form
                onSubmit={handleUpload}
                className="bg-slate-900 border border-slate-700 rounded-3xl p-6 shadow-lg"
              >
                <h2 className="text-2xl font-bold mb-3">
                  Upload UGC Handbook PDF
                </h2>

                <p className="text-slate-300 mb-5">
                  Upload official handbook PDFs for OCR extraction and cutoff
                  mark processing.
                </p>

                <input
                  type="file"
                  accept="application/pdf"
                  onChange={(e) =>
                    setSelectedFile(e.target.files ? e.target.files[0] : null)
                  }
                  className="block w-full text-slate-300 bg-slate-800 border border-slate-600 rounded-lg p-3 mb-5"
                />

                <button
                  disabled={uploading}
                  className="bg-violet-600 hover:bg-violet-700 disabled:bg-slate-600 text-white px-5 py-3 rounded-lg font-semibold"
                >
                  {uploading ? "Uploading..." : "Upload PDF"}
                </button>
              </form>

              <div className="bg-slate-900 border border-slate-700 rounded-3xl p-6 shadow-lg">
                <h2 className="text-2xl font-bold mb-4">OCR Jobs</h2>

                {jobs.length === 0 ? (
                  <p className="text-slate-400">No OCR jobs found.</p>
                ) : (
                  <div className="space-y-3">

                {jobs.slice(0, 5).map((job: any) => (
                  <div
                    key={job.job_id}
                    className="bg-slate-800 border border-slate-700 rounded-xl p-4"
                  >
                    <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                      <div>
                        <p className="text-white font-semibold">
                          Job ID: {job.job_id}
                        </p>

                        <p className="text-slate-400 text-sm">
                          Status: {job.status || "Pending"}
                        </p>

                        {job.created_at && (
                          <p className="text-slate-500 text-xs mt-1">
                            Created: {new Date(job.created_at).toLocaleString()}
                          </p>
                        )}
                      </div>

                      <div className="flex flex-wrap gap-2">
                        <button
                          onClick={() => processOCRJob(job.job_id)}
                          className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded-lg text-sm font-medium"
                        >
                          Process OCR
                        </button>

                        <button
                          onClick={() => router.push(`/admin/ocr-jobs/${job.job_id}`)}
                          className="bg-slate-700 hover:bg-slate-600 text-white px-3 py-2 rounded-lg text-sm font-medium"
                        >
                          Review Rows
                        </button>
                      </div>
                    </div>
                  </div>
                ))}

                  </div>
                )}
              </div>
            </div>

            <div className="bg-slate-900 border border-slate-700 rounded-3xl p-6 shadow-lg mt-6">
              <h2 className="text-2xl font-bold mb-4">Uploaded PDFs</h2>

              {pdfs.length === 0 ? (
                <p className="text-slate-400">No PDFs uploaded yet.</p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-left">
                    <thead>
                      <tr className="border-b border-slate-700 text-slate-400">
                        <th className="py-3">PDF ID</th>
                        <th className="py-3">File Name</th>
                        <th className="py-3">Status</th>
                        <th className="py-3">Uploaded At</th>
                      </tr>
                    </thead>

                    <tbody>
                      {pdfs.map((pdf: any) => (
                        <tr
                          key={pdf.pdf_id}
                          className="border-b border-slate-800 text-slate-300"
                        >
                          <td className="py-3">{pdf.pdf_id}</td>
                          <td className="py-3">
                            {pdf.original_filename || pdf.filename || "PDF"}
                          </td>
                          <td className="py-3">
                            {pdf.status || "Uploaded"}
                          </td>
                          <td className="py-3">
                            {pdf.uploaded_at
                              ? new Date(pdf.uploaded_at).toLocaleString()
                              : "N/A"}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </>
        )}
      </section>
    </main>
  );
}

