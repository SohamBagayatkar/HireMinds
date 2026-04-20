"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

export default function VideoGapAnalyzerPage() {
  const [jobDescription, setJobDescription] = useState<string>("");
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [atsScore, setAtsScore] = useState<number | null>(null);
  const [matchedSkills, setMatchedSkills] = useState<string[]>([]);
  const [missingSkills, setMissingSkills] = useState<string[]>([]);
  const [videoFeedback, setVideoFeedback] = useState<string>(""); // ✅ now string
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

    if (!parsed.jd) {
      alert("Please upload Job Description in Setup page first.");
      router.push("/setup");
      return;
    }

    setJobDescription(parsed.jd || "");
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

  const cleanFeedback = (text: string) => {
    return text.replace(/```json|```/g, "").trim();
  };

  const handleRunAnalysis = async () => {
    if (!videoFile) {
      alert("Please upload a video resume.");
      return;
    }

    const setupData = JSON.parse(localStorage.getItem("ats_setup_data") || "{}");

    setLoading(true);

    try {
      const formData = new FormData();
      formData.append("video", videoFile);
      formData.append("jd_text", setupData.jd || "");
      formData.append("model", mapModelName(setupData.selectedModel || "mistral"));
      formData.append("openai_api_key", setupData.openAIKey || "");
      formData.append("gemini_api_key", setupData.geminiKey || "");
      formData.append("mistral_api_key", setupData.mistralKey || "");
      formData.append("groq_api_key", setupData.groqKey || "");

      const res = await fetch("http://localhost:8000/api/video-gap-analyzer", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) throw new Error("Failed to analyze video resume");

      const data = await res.json();

      setAtsScore(data.score);
      setMatchedSkills(data.matched_skills || []);
      setMissingSkills(data.missing_skills || []);
      setVideoFeedback(cleanFeedback(data.video_feedback || ""));
    } catch (error) {
      console.error("Video gap analysis error:", error);
      alert("Failed to analyze video resume.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-6 pt-8">
      <h1 className="text-3xl font-bold text-black mb-6">
        Video Resume Gap Analyzer
      </h1>

      {/* JD Preview */}
      <Card className="bg-white border border-gray-200 shadow-md mb-6">
        <CardHeader>
          <CardTitle>Job Description</CardTitle>
        </CardHeader>
        <CardContent>
          <pre className="text-sm whitespace-pre-wrap">
            {truncateText(jobDescription)}
          </pre>
        </CardContent>
      </Card>

      {/* Upload */}
      <Card className="bg-white border shadow-md">
        <CardHeader>
          <CardTitle>Upload Video Resume</CardTitle>
        </CardHeader>
        <CardContent>
          <input
            type="file"
            accept="video/mp4,video/mov,video/webm"
            onChange={(e) => setVideoFile(e.target.files?.[0] || null)}
          />
        </CardContent>
      </Card>

      {/* Button */}
      <div className="mt-6 text-right">
        <Button onClick={handleRunAnalysis} disabled={loading}>
          {loading ? "Analyzing..." : "Run Analysis"}
        </Button>
      </div>

      {/* Results */}
      {atsScore !== null && (
        <div className="mt-8">

          {/* ATS */}
          <p className="mb-2 font-medium">ATS Score: {atsScore}%</p>
          <div className="w-full bg-gray-200 h-4 rounded-full">
            <div
              className="bg-black h-4 rounded-full"
              style={{ width: `${atsScore}%` }}
            />
          </div>

          {/* Matched */}
          <Card className="mt-6">
            <CardHeader>
              <CardTitle>Matched Skills</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-wrap gap-2">
              {matchedSkills.map((s, i) => (
                <Badge key={i} variant="secondary" className="bg-gray-100 text-black border">
                  {s}
                </Badge>
              ))}
            </CardContent>
          </Card>

          {/* Missing */}
          <Card className="mt-6">
            <CardHeader>
              <CardTitle>Missing Skills</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-wrap gap-2">
              {missingSkills.map((s, i) => (
                <Badge key={i} variant="secondary" className="bg-gray-100 text-black border">
                  {s}
                </Badge>
              ))}
            </CardContent>
          </Card>

          {/* ✅ SINGLE FEEDBACK BOX */}
          {videoFeedback && (
            <Card className="mt-6">
              <CardHeader>
                <CardTitle>AI Video Feedback</CardTitle>
              </CardHeader>
              <CardContent className="text-sm whitespace-pre-wrap text-black">
                {videoFeedback}
              </CardContent>
            </Card>
          )}

        </div>
      )}
    </div>
  );
}