"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import React from "react";

// Format advisor output into nice sections
function formatAdvisorOutput(text: string) {
  const lines = text.split("\n").filter((line) => line.trim() !== "");

  return (
    <div className="space-y-3">
      {lines.map((line, idx) => {
        // ### Headings
        if (line.startsWith("###")) {
          return (
            <h3 key={idx} className="text-lg font-semibold text-gray-900">
              {line.replace(/^###\s*/, "").replace(/\*\*/g, "")}
            </h3>
          );
        }

        // Bullet points (- or *)
        if (line.trim().startsWith("- ") || line.trim().startsWith("* ")) {
          return (
            <li key={idx} className="ml-6 list-disc text-gray-800">
              {line.replace(/^[-*]\s*/, "").replace(/\*\*/g, "")}
            </li>
          );
        }

        // Bold-only lines
        if (line.startsWith("**") && line.endsWith("**")) {
          return (
            <p key={idx} className="font-bold text-gray-900">
              {line.replace(/\*\*/g, "")}
            </p>
          );
        }

        // Normal paragraph with inline bold
        return (
          <p key={idx} className="text-gray-700">
            {line.replace(/\*\*(.*?)\*\*/g, "$1")}
          </p>
        );
      })}
    </div>
  );
}

export default function ResumeAdvisorPage() {
  const [resumeText, setResumeText] = useState<string>("");
  const [jobDescription, setJobDescription] = useState<string>("");
  const [advisorOutput, setAdvisorOutput] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    const setupData = JSON.parse(localStorage.getItem("ats_setup_data") || "{}");
    const resume = localStorage.getItem("ats_resume_text") || "";
    setResumeText(resume);
    setJobDescription(setupData.jd || "");
  }, []);

  const truncateText = (text: string, maxLines = 6) => {
    const lines = text.split("\n").filter((line) => line.trim() !== "");
    return lines.slice(0, maxLines).join("\n") + (lines.length > maxLines ? "\n..." : "");
  };

  const handleAdvisor = async () => {
    if (!resumeText || !jobDescription) {
      console.error("Please provide both resume text and job description.");
      return;
    }

    setLoading(true);
    try {
      const setupData = JSON.parse(localStorage.getItem("ats_setup_data") || "{}");
      const model = setupData.selectedModel || "Mistral Small";

      // Determine which key to send
      const keys = {
        openai_api_key: model === "OpenAI" ? setupData.openAIKey || null : null,
        mistral_api_key: model === "Mistral Small" ? setupData.mistralKey || null : null,
        gemini_api_key: model === "Gemini" ? setupData.geminiKey || null : null,
        groq_api_key: model === "Groq" ? setupData.groqKey || null : null,
      };

      const res = await fetch("http://localhost:8000/api/resume-advisor", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          resume: resumeText,
          jd: jobDescription,
          model: model.toLowerCase().includes("mistral") ? "mistral" : model.toLowerCase(),
          ...keys,
        }),
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(`Failed to generate resume advice: ${errorData.detail || res.statusText}`);
      }

      const data = await res.json();
      setAdvisorOutput(data.advisor_output);
    } catch (error) {
      console.error("An error occurred while generating advice:", error);
      setAdvisorOutput(`Error: ${(error as Error).message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-6 pt-8">
      <h1 className="text-3xl font-bold text-black mb-6">Resume Advisor</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <Card className="bg-white border border-gray-200 shadow-md rounded-lg">
          <CardHeader>
            <CardTitle className="text-black">Resume Preview</CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="text-gray-800 text-sm whitespace-pre-wrap p-2">
              {resumeText ? truncateText(resumeText, 6) : "No resume text found."}
            </pre>
          </CardContent>
        </Card>

        <Card className="bg-white border border-gray-200 shadow-md rounded-lg">
          <CardHeader>
            <CardTitle className="text-black">Job Description Preview</CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="text-gray-800 text-sm whitespace-pre-wrap p-2">
              {jobDescription ? truncateText(jobDescription, 6) : "No job description found."}
            </pre>
          </CardContent>
        </Card>
      </div>

      <div className="text-right mb-6">
        <Button
          className="bg-black hover:bg-gray-700 text-white px-6 py-2 rounded-md shadow-md transition-colors duration-200"
          onClick={handleAdvisor}
          disabled={loading}
        >
          {loading ? "Analyzing..." : "Get Advice"}
        </Button>
      </div>

      {advisorOutput && (
        <Card className="shadow-md bg-gray-50">
          <CardHeader>
            <CardTitle className="text-xl font-bold text-green-800">
              Resume Advice
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="prose max-w-none whitespace-pre-wrap text-gray-800 leading-relaxed space-y-3">
              {formatAdvisorOutput(advisorOutput)}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
