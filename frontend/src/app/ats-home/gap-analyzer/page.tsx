"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

export default function GapAnalyzerPage() {
  const [resumeText, setResumeText] = useState<string>("");
  const [jobDescription, setJobDescription] = useState<string>("");
  const [atsScore, setAtsScore] = useState<number | null>(null);
  const [readabilityScore, setReadabilityScore] = useState<number | null>(null);
  const [readabilityFeedback, setReadabilityFeedback] = useState<string>("");
  const [matchedSkills, setMatchedSkills] = useState<string[]>([]);
  const [missingSkills, setMissingSkills] = useState<string[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const router = useRouter();

  useEffect(() => {
    const setupData = localStorage.getItem("ats_setup_data");

    if (!setupData) {
      alert("Please complete setup first.");
      router.push("/setup");
      return;
    }

    const parsed = JSON.parse(setupData);
    setJobDescription(parsed.jd || "");
    setResumeText(localStorage.getItem("ats_resume_text") || "");

    if (!localStorage.getItem("ats_resume_text")) {
      alert("Please upload a resume on the Setup page first.");
      router.push("/setup");
    }
  }, [router]);

  const mapModelName = (model: string) => {
    switch (model.toLowerCase()) {
      case "openai":
      case "openai (requires api key)":
        return "openai";
      case "mistral small":
        return "mistral";
      case "groq":
        return "groq";
      case "gemini":
        return "gemini";
      default:
        return "mistral";
    }
  };

  const truncateText = (text: string, maxLines = 6) => {
    const lines = text.split("\n").filter((line) => line.trim() !== "");
    return lines.slice(0, maxLines).join("\n") + (lines.length > maxLines ? "\n..." : "");
  };

  const cleanFeedback = (feedback: string) => {
    return feedback.replace(/###/g, "").replace(/\*\*/g, "").trim();
  };

  const handleRunAnalysis = async () => {
    const setupData = JSON.parse(localStorage.getItem("ats_setup_data") || "{}");
    const resumeContent = localStorage.getItem("ats_resume_text") || "";

    if (!resumeContent || !setupData.jd) {
      alert("Please upload a resume and add a job description in the Setup page.");
      return;
    }

    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/api/gap-analyzer", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          resume_text: resumeContent,
          jd_text: setupData.jd || "",
          model: mapModelName(setupData.selectedModel || "mistral"),
          openai_api_key: setupData.openAIKey || null,
          gemini_api_key: setupData.geminiKey || null,
          mistral_api_key: setupData.mistralKey || null,
          groq_api_key: setupData.groqKey || null,
        }),
      });

      if (!res.ok) throw new Error("Failed to fetch gap analysis");

      const data = await res.json();
      setAtsScore(data.score);
      setMatchedSkills(data.matched_skills || []);
      setMissingSkills(data.missing_skills || []);
      setReadabilityScore(data.readability_score || null);
      setReadabilityFeedback(cleanFeedback(data.readability_feedback || ""));
    } catch (error) {
      console.error("Gap analysis error:", error);
      alert("Failed to analyze resume gap.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-6 pt-8">
      <h1 className="text-3xl font-bold text-black mb-6">Resume & JD Gap Analyzer</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Resume Preview */}
        <Card className="bg-white border border-gray-200 shadow-md">
          <CardHeader>
            <CardTitle className="text-black">Resume Preview</CardTitle>
          </CardHeader>
          <CardContent>
            {resumeText ? (
              <pre className="text-gray-700 text-sm whitespace-pre-wrap">
                {truncateText(resumeText, 6)}
              </pre>
            ) : (
              <p className="text-gray-500">No resume found. Please upload via Setup page.</p>
            )}
          </CardContent>
        </Card>

        {/* Job Description Preview */}
        <Card className="bg-white border border-gray-200 shadow-md">
          <CardHeader>
            <CardTitle className="text-black">Job Description Preview</CardTitle>
          </CardHeader>
          <CardContent>
            {jobDescription ? (
              <pre className="text-gray-700 text-sm whitespace-pre-wrap">
                {truncateText(jobDescription, 6)}
              </pre>
            ) : (
              <p className="text-gray-500">No job description found. Please add via Setup page.</p>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Analyze Button */}
      <div className="mt-6 text-right">
        <Button
          className="bg-black hover:bg-gray-900 text-white px-6"
          onClick={handleRunAnalysis}
          disabled={loading}
        >
          {loading ? "Analyzing..." : "Run Analysis"}
        </Button>
      </div>

      {/* Output Section */}
      {atsScore !== null && (
        <div className="mt-8">
          <p className="text-black font-medium mb-2">ATS Score: {atsScore}%</p>
          <div className="w-full bg-gray-200 rounded-full h-4">
            <div
              className="bg-black h-4 rounded-full transition-all"
              style={{ width: `${atsScore}%` }}
            ></div>
          </div>

          {matchedSkills.length > 0 && (
            <Card className="mt-6 bg-white border border-gray-300 shadow-sm">
              <CardHeader>
                <CardTitle className="text-black">Matched Skills</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {matchedSkills.map((s, i) => (
                    <Badge key={i} variant="secondary" className="bg-gray-100 text-black border">
                      {s}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {missingSkills.length > 0 && (
            <Card className="mt-6 bg-white border border-gray-300 shadow-sm">
              <CardHeader>
                <CardTitle className="text-black">Missing Skills</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {missingSkills.map((s, i) => (
                    <Badge key={i} variant="secondary" className="bg-gray-100 text-black border">
                      {s}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {readabilityScore !== null && (
            <div className="mt-6">
              <p className="text-black font-medium mb-2">Readability Score: {readabilityScore}%</p>
              <div className="w-full bg-gray-200 rounded-full h-4">
                <div
                  className="bg-black h-4 rounded-full transition-all"
                  style={{ width: `${readabilityScore}%` }}
                ></div>
              </div>
            </div>
          )}

          {readabilityFeedback && (
            <Card className="mt-4 bg-white border border-gray-300 shadow-sm">
              <CardHeader>
                <CardTitle className="text-black">Readability Feedback</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-black text-sm whitespace-pre-wrap">{readabilityFeedback}</p>
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </div>
  );
}
