"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import AppNavbar from "@/components/AppNavbar";
import {
  universityService,
  DegreeProgram,
} from "@/services/universityService";

export default function UniversityProgramsPage() {
  const params = useParams();
  const router = useRouter();

  const universityId = Number(params.universityId);

  const [programs, setPrograms] = useState<DegreeProgram[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadPrograms() {
      try {
        setLoading(true);
        const data = await universityService.getUniversityPrograms(universityId);
        setPrograms(data);
      } catch (err: any) {
        setError(err.message || "Failed to load degree programs.");
      } finally {
        setLoading(false);
      }
    }

    if (universityId) {
      loadPrograms();
    }
  }, [universityId]);

  return (
    <main className="min-h-screen bg-slate-950 text-white">
      <AppNavbar />

      <section className="max-w-6xl mx-auto px-6 py-10">
        <button
          onClick={() => router.push("/universities")}
          className="text-slate-300 hover:text-white mb-6"
        >
          ← Back to Universities
        </button>

        <div className="bg-slate-900 border border-slate-700 rounded-3xl p-8 shadow-2xl mb-8">
          <h1 className="text-4xl font-extrabold mb-3">
            Degree Programs
          </h1>

          <p className="text-slate-300">
            Available degree programs for selected university.
          </p>
        </div>

        {loading && (
          <div className="bg-slate-900 border border-slate-700 rounded-2xl p-6 text-slate-300">
            Loading degree programs...
          </div>
        )}

        {error && (
          <div className="bg-red-950 border border-red-700 text-red-300 rounded-2xl p-5">
            {error}
          </div>
        )}

        {!loading && !error && programs.length === 0 && (
          <div className="bg-slate-900 border border-slate-700 rounded-2xl p-6 text-slate-300">
            No degree programs found for this university.
          </div>
        )}

        <div className="grid gap-6">
          {programs.map((program) => (
            <div
              key={program.program_id}
              className="bg-slate-900 border border-slate-700 rounded-3xl p-6 shadow-lg hover:border-blue-500 transition"
            >
              <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
                <div>
                  <h2 className="text-2xl font-bold text-white mb-2">
                    {program.program_name}
                  </h2>

                  <p className="text-slate-300">
                    {program.degree_name || "Degree details not available"}
                  </p>
                </div>

                <div className="bg-blue-950 border border-blue-700 text-blue-300 px-4 py-2 rounded-xl text-sm font-medium">
                  {program.duration_years
                    ? `${program.duration_years} Years`
                    : "Duration N/A"}
                </div>
              </div>

              {program.description && (
                <p className="text-slate-300 mt-5 leading-relaxed">
                  {program.description}
                </p>
              )}

              <div className="grid md:grid-cols-3 gap-4 mt-6">
                <div className="bg-slate-800 rounded-2xl p-4">
                  <p className="text-slate-400 text-sm">Program ID</p>
                  <p className="text-white text-xl font-semibold">
                    {program.program_id}
                  </p>
                </div>

                <div className="bg-slate-800 rounded-2xl p-4">
                  <p className="text-slate-400 text-sm">University ID</p>
                  <p className="text-white text-xl font-semibold">
                    {program.university_id}
                  </p>
                </div>

                <div className="bg-slate-800 rounded-2xl p-4">
                  <p className="text-slate-400 text-sm">Stream ID</p>
                  <p className="text-white text-xl font-semibold">
                    {program.stream_id || "N/A"}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}