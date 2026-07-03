"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import AppNavbar from "@/components/AppNavbar";
import { universityService, University } from "@/services/universityService";

export default function UniversitiesPage() {
  const [universities, setUniversities] = useState<University[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadUniversities() {
      try {
        setLoading(true);
        const data = await universityService.getUniversities();
        setUniversities(data);
      } catch (err: any) {
        setError(err.message || "Failed to load universities.");
      } finally {
        setLoading(false);
      }
    }

    loadUniversities();
  }, []);

  return (
    <main className="min-h-screen bg-slate-950 text-white">
      <AppNavbar />

      <section className="max-w-6xl mx-auto px-6 py-10">
        <div className="bg-gradient-to-r from-blue-900 to-violet-900 border border-slate-700 rounded-3xl p-8 shadow-2xl mb-8">
          <h1 className="text-4xl font-extrabold mb-3">
            Universities & Degree Programs
          </h1>

          <p className="text-blue-100 max-w-2xl">
            Explore Sri Lankan universities and their available degree programs
            related to A/L streams.
          </p>
        </div>

        {loading && (
          <div className="bg-slate-900 border border-slate-700 rounded-2xl p-6 text-slate-300">
            Loading universities...
          </div>
        )}

        {error && (
          <div className="bg-red-950 border border-red-700 text-red-300 rounded-2xl p-5">
            {error}
          </div>
        )}

        {!loading && !error && universities.length === 0 && (
          <div className="bg-slate-900 border border-slate-700 rounded-2xl p-6 text-slate-300">
            No universities found. Please run backend seed data.
          </div>
        )}

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {universities.map((university) => (
            <Link
              key={university.university_id}
              href={`/universities/${university.university_id}`}
              className="group bg-slate-900 border border-slate-700 rounded-3xl p-6 hover:border-blue-500 hover:-translate-y-1 transition shadow-lg"
            >
              <div className="h-14 w-14 rounded-2xl bg-blue-600 flex items-center justify-center text-2xl mb-5">
                🏛️
              </div>

              <h2 className="text-2xl font-bold mb-2 group-hover:text-blue-400">
                {university.university_name}
              </h2>

              <p className="text-slate-300 mb-4">
                {university.location || "Location not available"}
              </p>

              <span className="text-blue-400 font-medium">
                View degree programs →
              </span>
            </Link>
          ))}
        </div>
      </section>
    </main>
  );
}