"use client";

import { useEffect, useState, ChangeEvent } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Plus, ChevronDown, ChevronUp } from "lucide-react";
import { Badge } from "@/components/ui/badge";

interface RankedResume {
  resume_name: string;
  score: number;
  matched_skills?: string[];
  missing_skills?: string[];
}

interface SetupData {
  selectedModel: string;
  openAIKey?: string;
  geminiKey?: string;
  mistralKey?: string;
  groqKey?: string;
}

export default function ResumeScreeningPage() {
  const router = useRouter();
  const [setupData, setSetupData] = useState<SetupData | null>(null);
  const [jdFile, setJdFile] = useState<File | null>(null);
  const [resumeFiles, setResumeFiles] = useState<File[]>([]);
  const [loading, setLoading] = useState(false);
  const [rankedResumes, setRankedResumes] = useState<RankedResume[]>([]);
  const [expanded, setExpanded] = useState<number | null>(null);

  // ✅ Load setup data from localStorage
  useEffect(() => {
    const stored = localStorage.getItem("ats_setup_data");
    if (!stored) {
      alert("Please complete setup first.");
      router.push("/ats-home/setup");
      return;
    }

    const parsed = JSON.parse(stored) as SetupData;

    // Convert readable names to internal keys
    const modelMap: Record<string, string> = {
      "OpenAI": "openai",
      "Gemini": "gemini",
      "Mistral Small": "mistral",
      "Groq": "groq",
    };

    const selectedModelKey = modelMap[parsed.selectedModel] || parsed.selectedModel.toLowerCase();

    const keyMap: Record<string, string | undefined> = {
      openai: parsed.openAIKey,
      gemini: parsed.geminiKey,
      mistral: parsed.mistralKey,
      groq: parsed.groqKey,
    };

    if (!keyMap[selectedModelKey]) {
      alert(`Please enter your ${parsed.selectedModel} API key in setup.`);
      router.push("/ats-home/setup");
      return;
    }

    setSetupData({ ...parsed, selectedModel: selectedModelKey });
  }, [router]);

  // ✅ Handlers
  const handleJDChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) setJdFile(e.target.files[0]);
  };

  const handleResumeChange = (index: number, e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) {
      const updatedFiles = [...resumeFiles];
      updatedFiles[index] = e.target.files[0];
      setResumeFiles(updatedFiles);
    }
  };

  const addResumeField = () => {
    if (resumeFiles.length >= 10) return;
    setResumeFiles([...resumeFiles, undefined as unknown as File]);
  };

  // ✅ Submit resumes for screening
  const handleScreenResumes = async () => {
    if (!setupData || !jdFile) return;

    const validResumes = resumeFiles.filter(Boolean);
    if (validResumes.length < 2 || validResumes.length > 10) {
      alert("Please upload between 2 and 10 resumes.");
      return;
    }

    const formData = new FormData();
    formData.append("jd_file", jdFile);
    validResumes.forEach((file) => formData.append("resumes", file));

    const apiKey =
      setupData.selectedModel === "openai"
        ? setupData.openAIKey
        : setupData.selectedModel === "gemini"
        ? setupData.geminiKey
        : setupData.selectedModel === "mistral"
        ? setupData.mistralKey
        : setupData.groqKey;

    formData.append("openai_api_key", apiKey || "");

    setLoading(true);
    setRankedResumes([]);

    try {
      const res = await fetch("http://localhost:8000/api/resume-screening", {
        method: "POST",
        body: formData,
      });
      if (!res.ok) throw new Error("Failed to screen resumes");
      const data = await res.json();
      setRankedResumes(data.ranked_resumes);
    } catch (error) {
      console.error("Resume screening error:", error);
      alert("Failed to screen resumes. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  // ✅ UI
  return (
    <div className="container mx-auto px-6 pt-8">
      <h1 className="text-3xl font-bold text-black mb-8">Resume Screening</h1>

      {/* JD + Resumes */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-5xl mx-auto mb-6">
        {/* Job Description */}
        <Card className="bg-white border border-gray-200 shadow-md">
          <CardHeader>
            <CardTitle className="text-black">Job Description</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <input
              type="file"
              accept=".pdf,.doc,.docx"
              onChange={handleJDChange}
              className="w-full p-2 border border-gray-300 rounded-md cursor-pointer"
            />
            {jdFile && <span className="text-sm text-gray-600">Uploaded: {jdFile.name}</span>}
          </CardContent>
        </Card>

        {/* Resumes */}
        <Card className="bg-white border border-gray-200 shadow-md">
          <CardHeader>
            <CardTitle className="text-black">Resumes (2-10)</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 max-h-96 overflow-y-auto">
            {resumeFiles.map((file, idx) => (
              <div key={idx} className="flex items-center gap-2">
                <input
                  type="file"
                  accept=".pdf,.doc,.docx"
                  onChange={(e) => handleResumeChange(idx, e)}
                  className="flex-1 p-1 border border-gray-300 rounded-md cursor-pointer"
                />
                {file && (
                  <span className="text-sm text-gray-700 px-2 py-1 bg-gray-100 rounded-full">
                    {file.name}
                  </span>
                )}
              </div>
            ))}

            {resumeFiles.length < 10 && (
              <Button
                variant="outline"
                className="flex items-center gap-2 text-black border-gray-300"
                onClick={addResumeField}
              >
                <Plus className="w-4 h-4" /> Add Resume
              </Button>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Run Screening */}
      <div className="text-right max-w-5xl mx-auto mb-6">
        <Button
          className={`px-6 ${
            loading ? "bg-gray-400 cursor-not-allowed" : "bg-black hover:bg-gray-900 text-white"
          }`}
          onClick={handleScreenResumes}
          disabled={loading}
        >
          {loading ? "Screening..." : "Screen Resumes"}
        </Button>
      </div>

      {/* Ranked Resumes */}
      {rankedResumes.length > 0 && (
        <div className="max-w-5xl mx-auto space-y-4">
          <h2 className="text-xl font-semibold text-black mb-2">Screening Results</h2>
          {rankedResumes.map((r, idx) => (
            <Card key={idx} className="bg-white border border-gray-200 shadow-sm">
              <CardHeader
                className="flex flex-row justify-between items-center cursor-pointer"
                onClick={() => setExpanded(expanded === idx ? null : idx)}
              >
                <CardTitle className="text-black">
                  {idx + 1}. {r.resume_name}
                </CardTitle>
                {expanded === idx ? <ChevronUp /> : <ChevronDown />}
              </CardHeader>
              <CardContent>
                <div className="w-full bg-gray-200 rounded-full h-4 mb-2">
                  <div
                    className="bg-black h-4 rounded-full transition-all"
                    style={{ width: `${r.score}%` }}
                  />
                </div>
                <p className="text-black font-medium mb-2">Score: {r.score}%</p>

                {expanded === idx && (
                  <div className="space-y-4">
                    <div>
                      <p className="text-black font-semibold mb-1">
                        Matched Skills ({r.matched_skills?.length || 0})
                      </p>
                      <div className="flex flex-wrap gap-2">
                        {r.matched_skills?.length ? (
                          r.matched_skills.map((skill, i) => (
                            <Badge key={i} className="bg-gray-100 text-black border">
                              {skill}
                            </Badge>
                          ))
                        ) : (
                          <span className="text-gray-500 text-sm">No matched skills found</span>
                        )}
                      </div>
                    </div>
                    <div>
                      <p className="text-black font-semibold mb-1">
                        Missing Skills ({r.missing_skills?.length || 0})
                      </p>
                      <div className="flex flex-wrap gap-2">
                        {r.missing_skills?.length ? (
                          r.missing_skills.map((skill, i) => (
                            <Badge key={i} className="bg-gray-100 text-black border">
                              {skill}
                            </Badge>
                          ))
                        ) : (
                          <span className="text-gray-500 text-sm">No missing skills</span>
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
