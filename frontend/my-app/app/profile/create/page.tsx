"use client";
import AppNavbar from "@/components/AppNavbar";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { profileService, Stream, Subject, District, FieldOfInterest } from "@/services/profileService";

export default function CreateProfilePage() {
  const [streams, setStreams] = useState<Stream[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [districts, setDistricts] = useState<District[]>([]);
  const [fields, setFields] = useState<FieldOfInterest[]>([]);

  const [streamId, setStreamId] = useState("");
  const [districtId, setDistrictId] = useState("");
  const [zScore, setZScore] = useState("");
  const [subject1, setSubject1] = useState("");
  const [subject2, setSubject2] = useState("");
  const [subject3, setSubject3] = useState("");
  const [fieldIds, setFieldIds] = useState<number[]>([]);

  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const router = useRouter();

  useEffect(() => {
    async function loadInitialData() {
      try {
        const [streamsData, districtsData, fieldsData] = await Promise.all([
          profileService.getStreams(),
          profileService.getDistricts(),
          profileService.getFieldsOfInterest(),
        ]);

        setStreams(streamsData);
        setDistricts(districtsData);
        setFields(fieldsData);
      } catch (err: any) {
        setError(err.message);
      }
    }

    loadInitialData();
  }, []);

  async function handleStreamChange(value: string) {
    setStreamId(value);
    setSubject1("");
    setSubject2("");
    setSubject3("");
    setSubjects([]);

    if (!value) return;

    try {
      const data = await profileService.getSubjectsByStream(Number(value));
      setSubjects(data);
    } catch (err: any) {
      setError(err.message);
    }
  }

  function toggleField(fieldId: number) {
    setFieldIds((prev) =>
      prev.includes(fieldId)
        ? prev.filter((id) => id !== fieldId)
        : [...prev, fieldId]
    );
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setMessage("");

    const selectedSubjects = [subject1, subject2, subject3]
      .filter(Boolean)
      .map(Number);

    if (!streamId || !districtId || !zScore) {
      setError("Please fill stream, district and Z-score.");
      return;
    }

    if (selectedSubjects.length !== 3) {
      setError("Please select exactly 3 subjects.");
      return;
    }

    const uniqueSubjects = new Set(selectedSubjects);

    if (uniqueSubjects.size !== 3) {
      setError("Please select 3 different subjects.");
      return;
    }

    try {
      setLoading(true);

      const result = await profileService.createProfile({
        stream_id: Number(streamId),
        district_id: Number(districtId),
        z_score: Number(zScore),
        subject_ids: selectedSubjects,
        field_ids: fieldIds,
      });

      setMessage(`Profile created successfully. Profile ID: ${result.profile_id}`);
      router.push(`/recommendations/${result.profile_id}`);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-slate-950 text-white">
    <AppNavbar />

    <section className="max-w-4xl mx-auto px-6 py-10">
      <div className="bg-slate-900 border border-slate-700 rounded-3xl shadow-2xl p-8">
        <h1 className="text-3xl font-bold text-white mb-2">
          Create Academic Profile
        </h1>

        <p className="text-slate-300 mb-6">
          Enter your A/L details to receive suitable degree recommendations.
        </p>

        {error && (
          <div className="bg-red-950 border border-red-700 text-red-300 p-3 rounded-lg mb-4">
            {error}
          </div>
        )}

        {message && (
          <div className="bg-green-950 border border-green-700 text-green-300 p-3 rounded-lg mb-4">
            {message}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-slate-300 mb-2">A/L Stream</label>
            <select
              className="bg-slate-800 border border-slate-600 text-white p-3 w-full rounded-lg"
              value={streamId}
              onChange={(e) => handleStreamChange(e.target.value)}
            >
              <option value="">Select stream</option>
              {streams.map((stream) => (
                <option key={stream.stream_id} value={stream.stream_id}>
                  {stream.stream_name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-slate-300 mb-2">District</label>
            <select
              className="bg-slate-800 border border-slate-600 text-white p-3 w-full rounded-lg"
              value={districtId}
              onChange={(e) => setDistrictId(e.target.value)}
            >
              <option value="">Select district</option>
              {districts.map((district) => (
                <option key={district.district_id} value={district.district_id}>
                  {district.district_name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-slate-300 mb-2">Z-score</label>
            <input
              className="bg-slate-800 border border-slate-600 text-white placeholder-slate-400 p-3 w-full rounded-lg"
              placeholder="Example: 1.8456"
              value={zScore}
              onChange={(e) => setZScore(e.target.value)}
            />
          </div>

          <div className="grid md:grid-cols-3 gap-4">
            <div>
              <label className="block text-slate-300 mb-2">Subject 1</label>
              <select
                className="bg-slate-800 border border-slate-600 text-white p-3 w-full rounded-lg"
                value={subject1}
                onChange={(e) => setSubject1(e.target.value)}
              >
                <option value="">Select</option>
                {subjects.map((subject) => (
                  <option key={subject.subject_id} value={subject.subject_id}>
                    {subject.subject_name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-slate-300 mb-2">Subject 2</label>
              <select
                className="bg-slate-800 border border-slate-600 text-white p-3 w-full rounded-lg"
                value={subject2}
                onChange={(e) => setSubject2(e.target.value)}
              >
                <option value="">Select</option>
                {subjects.map((subject) => (
                  <option key={subject.subject_id} value={subject.subject_id}>
                    {subject.subject_name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-slate-300 mb-2">Subject 3</label>
              <select
                className="bg-slate-800 border border-slate-600 text-white p-3 w-full rounded-lg"
                value={subject3}
                onChange={(e) => setSubject3(e.target.value)}
              >
                <option value="">Select</option>
                {subjects.map((subject) => (
                  <option key={subject.subject_id} value={subject.subject_id}>
                    {subject.subject_name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-slate-300 mb-3">
              Fields of Interest
            </label>

            <div className="grid md:grid-cols-2 gap-3">
              {fields.map((field) => (
                <label
                  key={field.field_id}
                  className="flex items-center gap-3 bg-slate-800 border border-slate-700 text-slate-200 p-3 rounded-lg"
                >
                  <input
                    type="checkbox"
                    checked={fieldIds.includes(field.field_id)}
                    onChange={() => toggleField(field.field_id)}
                  />
                  {field.field_name}
                </label>
              ))}
            </div>
          </div>

          <button
            disabled={loading}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 text-white w-full py-3 rounded-lg font-semibold"
          >
            {loading ? "Creating..." : "Create Profile"}
          </button>
        </form>
   </div>
    </section>
  </main>
);
}