"use client";

import { useEffect, useMemo, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { adminService } from "@/services/adminService";

type OCRRow = {
  row_id: number;
  job_id: number | string;
  university_name?: string | null;
  program_name?: string | null;
  district_name?: string | null;
  cutoff_mark?: number | string | null;
  raw_cutoff_mark?: string | null;
  cutoff_status?: string | null;
  display_cutoff?: string | number | null;
  year?: number | string | null;
  confidence_score?: number | null;
  status?: string | null;
  is_verified?: boolean;
  admin_note?: string | null;
  created_at?: string | null;
};

export default function OCRJobReviewPage() {
  const params = useParams();
  const router = useRouter();

const jobId = params.jobId as string;

  const [rows, setRows] = useState<OCRRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [savingRowId, setSavingRowId] = useState<number | null>(null);
  const [approving, setApproving] = useState(false);
  const [filter, setFilter] = useState<"ALL" | "LOW" | "PENDING" | "VERIFIED">("ALL");
  const [searchText, setSearchText] = useState("");

  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  async function loadRows() {
    try {
      setLoading(true);
      setError("");

      const data = await adminService.getExtractedRows(jobId);

      const sortedRows = Array.isArray(data)
        ? [...data].sort(
            (a, b) =>
              Number(a.confidence_score || 0) - Number(b.confidence_score || 0)
          )
        : [];

      setRows(sortedRows);
    } catch (err: any) {
      setError(err.message || "Failed to load OCR rows.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    const token = localStorage.getItem("admin_access_token");

    if (!token) {
      router.push("/admin/login");
      return;
    }

    if (jobId) {
      loadRows();
    }
  }, [jobId, router]);

  const lowConfidenceCount = useMemo(
    () => rows.filter((row) => Number(row.confidence_score || 0) < 80).length,
    [rows]
  );

  const verifiedCount = useMemo(
    () =>
      rows.filter(
        (row) => row.is_verified === true || row.status === "VERIFIED"
      ).length,
    [rows]
  );

  const pendingCount = useMemo(
    () =>
      rows.filter(
        (row) =>
          row.status !== "VERIFIED" &&
          row.status !== "APPROVED" &&
          row.is_verified !== true
      ).length,
    [rows]
  );

  const approvedCount = useMemo(
    () => rows.filter((row) => row.status === "APPROVED").length,
    [rows]
  );

  const filteredRows = useMemo(() => {
    let result = rows;

    if (filter === "LOW") {
      result = result.filter((row) => Number(row.confidence_score || 0) < 80);
    }

    if (filter === "PENDING") {
      result = result.filter(
        (row) =>
          row.status !== "VERIFIED" &&
          row.status !== "APPROVED" &&
          row.is_verified !== true
      );
    }

    if (filter === "VERIFIED") {
      result = result.filter(
        (row) => row.is_verified === true || row.status === "VERIFIED"
      );
    }

    if (searchText.trim()) {
      const keyword = searchText.toLowerCase();

      result = result.filter((row) => {
        return (
          String(row.university_name || "").toLowerCase().includes(keyword) ||
          String(row.program_name || "").toLowerCase().includes(keyword) ||
          String(row.district_name || "").toLowerCase().includes(keyword) ||
          String(row.cutoff_mark || "").toLowerCase().includes(keyword) ||
          String(row.year || "").toLowerCase().includes(keyword)
        );
      });
    }

    return result;
  }, [rows, filter, searchText]);

  function updateLocalRow(rowId: number, field: keyof OCRRow, value: any) {
    setRows((prev) =>
      prev.map((row) =>
        row.row_id === rowId ? { ...row, [field]: value } : row
      )
    );
  }

  function getConfidenceStyle(scoreValue: number) {
    if (scoreValue < 60) {
      return "bg-red-950 border-red-700 text-red-300";
    }

    if (scoreValue < 80) {
      return "bg-yellow-950 border-yellow-700 text-yellow-300";
    }

    return "bg-green-950 border-green-700 text-green-300";
  }

  function getStatusStyle(status?: string | null, isVerified?: boolean) {
    if (status === "APPROVED") {
      return "bg-emerald-950 border-emerald-700 text-emerald-300";
    }

    if (status === "VERIFIED" || isVerified) {
      return "bg-green-950 border-green-700 text-green-300";
    }

    if (status === "MANUALLY_CORRECTED") {
      return "bg-blue-950 border-blue-700 text-blue-300";
    }

    if (status === "REVIEW_REQUIRED") {
      return "bg-red-950 border-red-700 text-red-300";
    }

    return "bg-slate-800 border-slate-600 text-slate-300";
  }
  async function verifyHighConfidenceRows() {
    try {
      setError("");
      setMessage("");

      const response = await adminService.verifyHighConfidenceRows(jobId, 80);

      setMessage(
        `High confidence rows verified successfully. Count: ${
          response.verified_count ?? 0
        }`
      );

      await loadRows();
    } catch (err: any) {
      setError(err.message || "Failed to verify high confidence rows.");
    }
  }

  async function saveRow(row: OCRRow) {
    try {
      setSavingRowId(row.row_id);
      setError("");
      setMessage("");

      await adminService.updateExtractedRow(row.row_id, {
        university_name: row.university_name,
        program_name: row.program_name,
        district_name: row.district_name,
        cutoff_mark:
          row.cutoff_mark === "" || row.cutoff_mark === null
            ? null
            : Number(row.cutoff_mark),
        year: row.year === "" || row.year === null ? null : Number(row.year),
        admin_note: row.admin_note,
      });

      setMessage("Row updated successfully. Confidence score changed to 100%.");
      await loadRows();
    } catch (err: any) {
      setError(err.message || "Failed to update row.");
    } finally {
      setSavingRowId(null);
    }
  }

  async function verifyRow(rowId: number) {
    try {
      setSavingRowId(rowId);
      setError("");
      setMessage("");

      await adminService.verifyExtractedRow(rowId);

      setMessage("Row verified successfully.");
      await loadRows();
    } catch (err: any) {
      setError(err.message || "Failed to verify row.");
    } finally {
      setSavingRowId(null);
    }
  }

  async function approveJob() {
    try {
      setApproving(true);
      setError("");
      setMessage("");

      const response = await adminService.approveOCRJob(jobId);

      setMessage(
        `OCR data approved. Inserted: ${response.inserted_count ?? 0}, Updated: ${
          response.updated_count ?? 0
        }, Skipped: ${response.skipped_count ?? 0}`
      );

      await loadRows();
    } catch (err: any) {
      setError(err.message || "Failed to approve OCR job.");
    } finally {
      setApproving(false);
    }
  }

  return (
    <main className="min-h-screen bg-slate-950 text-white">
      <nav className="border-b border-slate-800 bg-slate-950/80 backdrop-blur">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold">OCR Review</h1>
            <p className="text-xs text-slate-400">Job ID: {jobId}</p>
          </div>

          <button
            onClick={() => router.push("/admin/dashboard")}
            className="bg-slate-700 hover:bg-slate-600 px-4 py-2 rounded-lg text-sm"
          >
            Back to Dashboard
          </button>
        </div>
      </nav>

      <section className="max-w-7xl mx-auto px-6 py-10">
        <div className="bg-gradient-to-r from-violet-900 to-blue-900 border border-slate-700 rounded-3xl p-8 shadow-2xl mb-8">
          <h1 className="text-4xl font-extrabold mb-3">
            Review Extracted PDF Data
          </h1>

          <p className="text-blue-100 max-w-3xl">
            Low-confidence OCR rows are shown first. Correct wrong rows manually,
            save them, verify them, and approve verified rows into the cutoff
            marks table.
          </p>
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

        <div className="grid md:grid-cols-4 gap-5 mb-6">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl p-5">
            <p className="text-slate-400 text-sm">Total Rows</p>
            <h2 className="text-3xl font-bold mt-2">{rows.length}</h2>
          </div>

          <div className="bg-red-950 border border-red-700 rounded-2xl p-5">
            <p className="text-red-300 text-sm">Low Confidence</p>
            <h2 className="text-3xl font-bold mt-2">{lowConfidenceCount}</h2>
          </div>

          <div className="bg-yellow-950 border border-yellow-700 rounded-2xl p-5">
            <p className="text-yellow-300 text-sm">Pending Review</p>
            <h2 className="text-3xl font-bold mt-2">{pendingCount}</h2>
          </div>

          <div className="bg-green-950 border border-green-700 rounded-2xl p-5">
            <p className="text-green-300 text-sm">Verified</p>
            <h2 className="text-3xl font-bold mt-2">
              {verifiedCount}
              {approvedCount > 0 ? ` / ${approvedCount} approved` : ""}
            </h2>
          </div>
        </div>

        {lowConfidenceCount > 0 && (
          <div className="bg-red-950 border border-red-700 text-red-200 rounded-2xl p-4 mb-6">
            {lowConfidenceCount} low-confidence row(s) found. Please check and
            manually correct them before approving.
          </div>
        )}

        <div className="bg-slate-900 border border-slate-700 rounded-3xl p-5 mb-6">
          <div className="grid md:grid-cols-3 gap-4 items-center">
            <input
              className="bg-slate-800 border border-slate-600 text-white placeholder-slate-400 p-3 rounded-lg md:col-span-2"
              placeholder="Search university, program, district, cutoff or year..."
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
            />

            <select
              className="bg-slate-800 border border-slate-600 text-white p-3 rounded-lg"
              value={filter}
              onChange={(e) =>
                setFilter(e.target.value as "ALL" | "LOW" | "PENDING" | "VERIFIED")
              }
            >
              <option value="ALL">All Rows</option>
              <option value="LOW">Low Confidence First</option>
              <option value="PENDING">Pending Review</option>
              <option value="VERIFIED">Verified Rows</option>
            </select>
          </div>
        </div>

        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
          <p className="text-slate-300">
            Showing {filteredRows.length} of {rows.length} extracted rows
          </p>

          <div className="flex flex-wrap gap-3">
            <button
            onClick={verifyHighConfidenceRows}
            className="bg-blue-600 hover:bg-blue-700 text-white px-5 py-3 rounded-lg font-semibold"
            >
            Verify High Confidence Rows
            </button>
            <button
              onClick={loadRows}
              className="bg-slate-700 hover:bg-slate-600 text-white px-5 py-3 rounded-lg font-semibold"
            >
              Refresh Rows
            </button>

            <button
              onClick={approveJob}
              disabled={approving || verifiedCount === 0}
              className="bg-green-600 hover:bg-green-700 disabled:bg-slate-600 text-white px-5 py-3 rounded-lg font-semibold"
            >
              {approving ? "Approving..." : "Approve Verified Rows"}
            </button>
          </div>
        </div>

        {loading ? (
          <div className="bg-slate-900 border border-slate-700 rounded-2xl p-6 text-slate-300">
            Loading extracted rows...
          </div>
        ) : rows.length === 0 ? (
          <div className="bg-slate-900 border border-slate-700 rounded-2xl p-6 text-slate-300">
            No extracted rows found. Go back and click Process OCR first.
          </div>
        ) : filteredRows.length === 0 ? (
          <div className="bg-slate-900 border border-slate-700 rounded-2xl p-6 text-slate-300">
            No rows match your current filter/search.
          </div>
        ) : (
          <div className="bg-slate-900 border border-slate-700 rounded-3xl shadow-lg overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="border-b border-slate-700 text-slate-400 bg-slate-900">
                    <th className="p-3">Row ID</th>
                    <th className="p-3">University</th>
                    <th className="p-3">Program</th>
                    <th className="p-3">District</th>
                    <th className="p-3">Year</th>
                    <th className="p-3">Cutoff</th>
                    <th className="p-3">Confidence</th>
                    <th className="p-3">Status</th>
                    <th className="p-3">Admin Note</th>
                    <th className="p-3">Actions</th>
                  </tr>
                </thead>

                <tbody>
                  {filteredRows.map((row) => {
                    const confidence = Number(row.confidence_score || 0);
                    const isSaving = savingRowId === row.row_id;

                    return (
                      <tr
                        key={row.row_id}
                        className={`border-b border-slate-800 text-slate-300 ${
                          confidence < 80 ? "bg-red-950/20" : ""
                        }`}
                      >
                        <td className="p-3">{row.row_id}</td>

                        <td className="p-3 min-w-[200px]">
                          <input
                            className="bg-slate-800 border border-slate-600 text-white p-2 rounded w-full"
                            value={row.university_name || ""}
                            onChange={(e) =>
                              updateLocalRow(
                                row.row_id,
                                "university_name",
                                e.target.value
                              )
                            }
                          />
                        </td>

                        <td className="p-3 min-w-[240px]">
                          <input
                            className="bg-slate-800 border border-slate-600 text-white p-2 rounded w-full"
                            value={row.program_name || ""}
                            onChange={(e) =>
                              updateLocalRow(
                                row.row_id,
                                "program_name",
                                e.target.value
                              )
                            }
                          />
                        </td>

                        <td className="p-3 min-w-[160px]">
                          <input
                            className="bg-slate-800 border border-slate-600 text-white p-2 rounded w-full"
                            value={row.district_name || ""}
                            onChange={(e) =>
                              updateLocalRow(
                                row.row_id,
                                "district_name",
                                e.target.value
                              )
                            }
                          />
                        </td>

                        <td className="p-3 min-w-[100px]">
                          <input
                            className="bg-slate-800 border border-slate-600 text-white p-2 rounded w-full"
                            value={row.year ?? ""}
                            onChange={(e) =>
                              updateLocalRow(row.row_id, "year", e.target.value)
                            }
                          />
                        </td>

                        <td className="p-3 min-w-[110px]">
                          <input
                            className="bg-slate-800 border border-slate-600 text-white p-2 rounded w-full"
                            value={row.cutoff_status === "NQC" ? "NQC" : row.cutoff_mark ?? ""}
                            onChange={(e) => {
                              const value = e.target.value;

                              updateLocalRow(row.row_id, "cutoff_mark", value);

                              if (value.trim().toUpperCase() === "NQC") {
                                updateLocalRow(row.row_id, "cutoff_status", "NQC");
                              } else {
                                updateLocalRow(row.row_id, "cutoff_status", "QUALIFIED");
                              }
                            }}
                          />
                        </td>

                        <td className="p-3">
                          <span
                            className={`px-3 py-1 rounded-full text-xs border ${getConfidenceStyle(
                              confidence
                            )}`}
                          >
                            {confidence}%
                          </span>
                        </td>

                        <td className="p-3 min-w-[150px]">
                          <span
                            className={`px-3 py-1 rounded-full text-xs border ${getStatusStyle(
                              row.status,
                              row.is_verified
                            )}`}
                          >
                            {row.status ||
                              (row.is_verified ? "VERIFIED" : "PENDING")}
                          </span>
                        </td>

                        <td className="p-3 min-w-[180px]">
                          <input
                            className="bg-slate-800 border border-slate-600 text-white p-2 rounded w-full"
                            placeholder="Optional note"
                            value={row.admin_note || ""}
                            onChange={(e) =>
                              updateLocalRow(
                                row.row_id,
                                "admin_note",
                                e.target.value
                              )
                            }
                          />
                        </td>

                        <td className="p-3 min-w-[150px]">
                          <div className="flex gap-2">
                            <button
                              onClick={() => saveRow(row)}
                              disabled={isSaving}
                              className="bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 text-white px-3 py-2 rounded text-xs"
                            >
                              {isSaving ? "Saving..." : "Save"}
                            </button>

                            <button
                              onClick={() => verifyRow(row.row_id)}
                              disabled={isSaving}
                              className="bg-green-600 hover:bg-green-700 disabled:bg-slate-600 text-white px-3 py-2 rounded text-xs"
                            >
                              Verify
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </section>
    </main>
  );
}
