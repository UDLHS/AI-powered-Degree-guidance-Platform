"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { authService } from "@/services/authService";

export default function RegisterPage() {
  const router = useRouter();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("Password123");
  const [error, setError] = useState("");

  async function handleRegister(e: React.FormEvent) {
    e.preventDefault();
    setError("");

    try {
      await authService.register({
        name,
        email,
        password,
      });

      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message);
    }
  }

  return (
    <main className="min-h-screen flex items-center justify-center bg-slate-950 px-4">
      <form
        onSubmit={handleRegister}
        className="bg-slate-900 border border-slate-700 p-8 rounded-2xl shadow-xl w-full max-w-md"
      >
        <h1 className="text-3xl font-bold mb-6 text-white">
          Student Register
        </h1>

        {error && (
          <div className="bg-red-950 border border-red-700 text-red-300 p-3 rounded-lg mb-4">
            {error}
          </div>
        )}

        <label className="block text-slate-300 mb-2">Name</label>
        <input
          className="bg-slate-800 border border-slate-600 text-white placeholder-slate-400 p-3 w-full mb-4 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Enter your name"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />

        <label className="block text-slate-300 mb-2">Email</label>
        <input
          className="bg-slate-800 border border-slate-600 text-white placeholder-slate-400 p-3 w-full mb-4 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Enter your email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />

        <label className="block text-slate-300 mb-2">Password</label>
        <input
          className="bg-slate-800 border border-slate-600 text-white placeholder-slate-400 p-3 w-full mb-6 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Enter password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <button className="bg-blue-600 hover:bg-blue-700 text-white w-full py-3 rounded-lg font-semibold">
          Register
        </button>
      </form>
    </main>
  );
}