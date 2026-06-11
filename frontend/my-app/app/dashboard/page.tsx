"use client";

import Link from "next/link";
import AppNavbar from "@/components/AppNavbar";

export default function DashboardPage() {
  return (
    <main className="min-h-screen bg-slate-950 text-white">
      <AppNavbar />

      <section className="max-w-6xl mx-auto px-6 py-10">
        <div className="bg-gradient-to-r from-blue-900 to-violet-900 border border-slate-700 rounded-3xl p-8 shadow-2xl mb-8">
          <h1 className="text-4xl font-extrabold mb-3">
            Welcome to your Student Dashboard
          </h1>

          <p className="text-blue-100 max-w-2xl">
            Create your academic profile, generate degree recommendations, and
            explore suitable university pathways based on your A/L results.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-6">
          <Link
            href="/profile/create"
            className="group bg-slate-900 border border-slate-700 rounded-3xl p-6 hover:border-blue-500 hover:-translate-y-1 transition"
          >
            <div className="h-14 w-14 rounded-2xl bg-blue-600 flex items-center justify-center text-2xl mb-5">
              🎓
            </div>

            <h2 className="text-2xl font-bold mb-2 group-hover:text-blue-400">
              Create Academic Profile
            </h2>

            <p className="text-slate-300">
              Add your stream, district, subjects, Z-score and interests.
            </p>
          </Link>

          <div className="bg-slate-900 border border-slate-700 rounded-3xl p-6">
            <div className="h-14 w-14 rounded-2xl bg-violet-600 flex items-center justify-center text-2xl mb-5">
              🤖
            </div>

            <h2 className="text-2xl font-bold mb-2">
              AI Recommendations
            </h2>

            <p className="text-slate-300">
              Generate suitable degree programs after creating your profile.
            </p>
          </div>

          <Link
            href="/universities"
            className="bg-slate-900 border border-slate-700 rounded-3xl p-6 hover:border-emerald-500 hover:-translate-y-1 transition"
          >
            <div className="h-14 w-14 rounded-2xl bg-emerald-600 flex items-center justify-center text-2xl mb-5">
              🏛️
            </div>

            <h2 className="text-2xl font-bold mb-2">
              University Pathways
            </h2>

            <p className="text-slate-300">
              Explore degree programs, specializations and career opportunities.
            </p>
          </Link>
        </div>

        <div className="grid md:grid-cols-4 gap-5 mt-8">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl p-5">
            <p className="text-slate-400 text-sm">Profile Status</p>
            <h3 className="text-2xl font-bold mt-2">Ready</h3>
          </div>

          <div className="bg-slate-900 border border-slate-700 rounded-2xl p-5">
            <p className="text-slate-400 text-sm">Recommendation Type</p>
            <h3 className="text-2xl font-bold mt-2">AI Based</h3>
          </div>

          <div className="bg-slate-900 border border-slate-700 rounded-2xl p-5">
            <p className="text-slate-400 text-sm">Data Source</p>
            <h3 className="text-2xl font-bold mt-2">UGC Z-score</h3>
          </div>

          <div className="bg-slate-900 border border-slate-700 rounded-2xl p-5">
            <p className="text-slate-400 text-sm">User Type</p>
            <h3 className="text-2xl font-bold mt-2">Student</h3>
          </div>
        </div>
      </section>
    </main>
  );
}