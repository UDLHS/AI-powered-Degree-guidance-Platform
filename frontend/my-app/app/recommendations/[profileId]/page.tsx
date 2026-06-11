"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import {
  recommendationService,
  RecommendationItem,
} from "@/services/recommendationService";

export default function RecommendationPage() {
  const params = useParams();
  const router = useRouter();

  const profileId = params.profileId as string;

  const [recommendations, setRecommendations] = useState<RecommendationItem[]>([]);
  const [rawResponse, setRawResponse] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadRecommendations() {
      try {
        setLoading(true);
        setError("");

        const data = await recommendationService.generateFromProfile(profileId);
        setRawResponse(data);

        let resultList: RecommendationItem[] = [];

        if (Array.isArray(data)) {
          resultList = data;
        } else if (Array.isArray(data.recommendations)) {
          resultList = data.recommendations;
        } else if (Array.isArray(data.results)) {
          resultList = data.results;
        } else if (Array.isArray(data.data)) {
          resultList = data.data;
        }

        setRecommendations(resultList);
      } catch (err: any) {
        setError(err.message || "Failed to load recommendations.");
      } finally {
        setLoading(false);
      }
    }

    if (profileId) {
      loadRecommendations();
    }
  }, [profileId]);

  function getStatusColor(status?: string) {
    const value = status?.toLowerCase() || "";

    if (value.includes("eligible") || value.includes("matched")) {
      return "bg-green-950 border-green-700 text-green-300";
    }

    if (value.includes("pending") || value.includes("near")) {
      return "bg-yellow-950 border-yellow-700 text-yellow-300";
    }

    return "bg-blue-950 border-blue-700 text-blue-300";
  }

  return (
    <main className="min-h-screen bg-slate-950 p-6">
      <div className="max-w-5xl mx-auto">
        <div className="bg-slate-900 border border-slate-700 rounded-2xl shadow-xl p-8 mb-6">
          <button
            onClick={() => router.push("/dashboard")}
            className="text-slate-300 hover:text-white mb-4"
          >
            ← Back to Dashboard
          </button>

          <h1 className="text-3xl font-bold text-white mb-2">
            Degree Recommendations
          </h1>

          <p className="text-slate-300">
            These are the suggested degree programs based on your academic
            profile.
          </p>

          <p className="text-slate-500 text-sm mt-2">
            Profile ID: {profileId}
          </p>
        </div>

        {loading && (
          <div className="bg-slate-900 border border-slate-700 text-slate-300 rounded-2xl p-8">
            Loading recommendations...
          </div>
        )}

        {error && (
          <div className="bg-red-950 border border-red-700 text-red-300 rounded-2xl p-5">
            {error}
          </div>
        )}

        {!loading && !error && recommendations.length === 0 && (
          <div className="bg-slate-900 border border-slate-700 text-slate-300 rounded-2xl p-8">
            <h2 className="text-xl font-semibold text-white mb-3">
              No recommendations found
            </h2>

            <p className="mb-4">
              The backend responded successfully, but no recommendation list was
              found.
            </p>

            <pre className="bg-slate-950 border border-slate-700 rounded-lg p-4 overflow-auto text-xs text-slate-300">
              {JSON.stringify(rawResponse, null, 2)}
            </pre>
          </div>
        )}

        <div className="grid gap-5">
          {recommendations.map((item, index) => (
            <div
              key={item.result_id || item.program_id || index}
              className="bg-slate-900 border border-slate-700 rounded-2xl p-6 shadow-lg"
            >
              <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
                <div>
                  <h2 className="text-2xl font-bold text-white mb-2">
                    {item.program_name ||
                      item.degree_name ||
                      `Degree Program ${index + 1}`}
                  </h2>

                  <p className="text-slate-300">
                    {item.university_name || "University not available"}
                  </p>
                </div>

                <div
                  className={`border rounded-lg px-4 py-2 text-sm font-medium ${getStatusColor(
                    item.eligibility_status || item.result_type
                  )}`}
                >
                  {item.eligibility_status || item.result_type || "Recommended"}
                </div>
              </div>

              <div className="grid md:grid-cols-4 gap-4 mt-6">
                <div className="bg-slate-800 rounded-xl p-4">
                  <p className="text-slate-400 text-sm">Match Score</p>
                  <p className="text-white text-xl font-semibold">
                    {item.match_score !== undefined
                      ? `${item.match_score}%`
                      : "N/A"}
                  </p>
                </div>

                <div className="bg-slate-800 rounded-xl p-4">
                  <p className="text-slate-400 text-sm">Cutoff Mark</p>
                  <p className="text-white text-xl font-semibold">
                    {item.cutoff_mark ?? "N/A"}
                  </p>
                </div>

                <div className="bg-slate-800 rounded-xl p-4">
                  <p className="text-slate-400 text-sm">Your Z-score</p>
                  <p className="text-white text-xl font-semibold">
                    {item.z_score ?? "N/A"}
                  </p>
                </div>

                <div className="bg-slate-800 rounded-xl p-4">
                  <p className="text-slate-400 text-sm">Margin</p>
                  <p className="text-white text-xl font-semibold">
                    {item.pending_margin ?? "N/A"}
                  </p>
                </div>
              </div>

              {item.explanation && (
                <p className="text-slate-300 mt-5 leading-relaxed">
                  {item.explanation}
                </p>
              )}
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}