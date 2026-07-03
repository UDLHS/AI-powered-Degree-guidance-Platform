"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { adminService } from "@/services/adminService";

export default function AdminLoginPage() {
  const router = useRouter();

  const [email, setEmail] = useState("admin@aidg.lk");
  const [password, setPassword] = useState("Admin12345");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setError("");

    try {
      setLoading(true);
      await adminService.login(email, password);
      router.push("/admin/dashboard");
    } catch (err: any) {
      setError(err.message || "Admin login failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-slate-950 flex items-center justify-center px-4">
      <form
        onSubmit={handleLogin}
        className="bg-slate-900 border border-slate-700 rounded-3xl shadow-2xl p-8 w-full max-w-md"
      >
        <div className="h-16 w-16 rounded-2xl bg-violet-600 flex items-center justify-center text-3xl mb-6">
          🛡️
        </div>

        <h1 className="text-3xl font-extrabold text-white mb-2">
          Admin Login
        </h1>

        <p className="text-slate-300 mb-6">
          Login to manage handbook uploads, OCR data and system records.
        </p>

        {error && (
          <div className="bg-red-950 border border-red-700 text-red-300 p-3 rounded-lg mb-4">
            {error}
          </div>
        )}

        <label className="block text-slate-300 mb-2">Admin Email</label>
        <input
          className="bg-slate-800 border border-slate-600 text-white p-3 w-full rounded-lg mb-4"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />

        <label className="block text-slate-300 mb-2">Password</label>
        <input
          className="bg-slate-800 border border-slate-600 text-white p-3 w-full rounded-lg mb-6"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <button
          disabled={loading}
          className="bg-violet-600 hover:bg-violet-700 disabled:bg-slate-600 text-white w-full py-3 rounded-lg font-semibold"
        >
          {loading ? "Logging in..." : "Login as Admin"}
        </button>
      </form>
    </main>
  );
}