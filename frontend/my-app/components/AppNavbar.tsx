"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { authService } from "@/services/authService";

export default function AppNavbar() {
  const router = useRouter();

  function logout() {
    authService.logout();
    router.push("/login");
  }

  return (
    <nav className="border-b border-slate-800 bg-slate-950/80 backdrop-blur sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-xl bg-blue-600 flex items-center justify-center text-white font-bold">
            AI
          </div>
          <div>
            <h1 className="text-white font-bold leading-tight">
              Degree Guidance
            </h1>
            <p className="text-xs text-slate-400">Sri Lankan A/L Students</p>
          </div>
        </Link>

        <div className="flex items-center gap-3">
          
          <Link
            href="/dashboard"
            className="text-slate-300 hover:text-white text-sm"
          >
            Dashboard
          </Link>

          <Link
            href="/profile/create"
            className="text-slate-300 hover:text-white text-sm"
          >
            Create Profile
          </Link>
          <Link
            href="/universities"
            className="text-slate-300 hover:text-white text-sm"
          >
            Universities
          </Link>

          <button
            onClick={logout}
            className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg text-sm font-medium"
          >
            Logout
          </button>
        </div>
      </div>
    </nav>
  );
}