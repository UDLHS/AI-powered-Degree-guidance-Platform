import Link from "next/link";

export default function HomePage() {
  return (
    <main className="min-h-screen bg-slate-950 text-white overflow-hidden">
      <section className="relative min-h-screen flex items-center justify-center px-6">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,#1d4ed8,transparent_35%),radial-gradient(circle_at_bottom_right,#7c3aed,transparent_30%)] opacity-40" />

        <div className="relative max-w-6xl mx-auto grid lg:grid-cols-2 gap-12 items-center">
          <div>
            <div className="inline-flex items-center gap-2 bg-blue-950 border border-blue-800 text-blue-300 px-4 py-2 rounded-full text-sm mb-6">
              AI-powered university degree recommendation system
            </div>

            <h1 className="text-5xl lg:text-6xl font-extrabold leading-tight mb-6">
              Find the best degree path for your future.
            </h1>

            <p className="text-slate-300 text-lg leading-relaxed mb-8">
              Enter your A/L stream, district, Z-score, subjects and interests.
              Our system recommends suitable university degree programs based on
              your academic profile.
            </p>

            <div className="flex flex-wrap gap-4">
              <Link
                href="/register"
                className="bg-blue-600 hover:bg-blue-700 text-white px-7 py-3 rounded-xl font-semibold shadow-lg"
              >
                Get Started
              </Link>

              <Link
                href="/login"
                className="bg-slate-800 hover:bg-slate-700 border border-slate-700 text-white px-7 py-3 rounded-xl font-semibold"
              >
                Student Login
              </Link>
            </div>
          </div>

          <div className="bg-slate-900/80 border border-slate-700 rounded-3xl p-8 shadow-2xl">
            <div className="grid gap-4">
              <div className="bg-slate-800 rounded-2xl p-5 border border-slate-700">
                <p className="text-slate-400 text-sm">Step 01</p>
                <h3 className="text-xl font-bold mt-1">Create Profile</h3>
                <p className="text-slate-300 mt-2">
                  Add your A/L stream, subjects, district and Z-score.
                </p>
              </div>

              <div className="bg-slate-800 rounded-2xl p-5 border border-slate-700">
                <p className="text-slate-400 text-sm">Step 02</p>
                <h3 className="text-xl font-bold mt-1">AI Recommendation</h3>
                <p className="text-slate-300 mt-2">
                  System checks cutoff marks, eligibility and interest areas.
                </p>
              </div>

              <div className="bg-slate-800 rounded-2xl p-5 border border-slate-700">
                <p className="text-slate-400 text-sm">Step 03</p>
                <h3 className="text-xl font-bold mt-1">Choose Degree Path</h3>
                <p className="text-slate-300 mt-2">
                  View matched programs, universities and possible career paths.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}