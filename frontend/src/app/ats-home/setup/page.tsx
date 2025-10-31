"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export default function SetupPage() {
  const [selectedModel, setSelectedModel] = useState("Mistral Small");
  const [openAIKey, setOpenAIKey] = useState("");
  const [geminiKey, setGeminiKey] = useState("");
  const [mistralKey, setMistralKey] = useState("");
  const [groqKey, setGroqKey] = useState("");
  const [resumeFileName, setResumeFileName] = useState("");
  const [jdFileName, setJDFileName] = useState("");
  const [jd, setJD] = useState("");
  const [uploading, setUploading] = useState(false);
  const [saveMessage, setSaveMessage] = useState("");

  const handleResumeUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.type.includes("pdf") && !file.type.includes("msword") && !file.name.endsWith(".docx")) {
      alert("Please upload a PDF or DOC/DOCX file");
      return;
    }

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);

      const res = await fetch("http://localhost:8000/api/upload-resume", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) throw new Error("Failed to upload resume");

      const data = await res.json();
      localStorage.setItem("ats_resume_text", data.extracted_text);
      setResumeFileName(file.name);
    } catch (error) {
      console.error("Resume upload failed:", error);
      alert("Resume upload failed");
    } finally {
      setUploading(false);
    }
  };

  const handleJDUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.type.includes("pdf") && !file.type.includes("msword") && !file.name.endsWith(".docx")) {
      alert("Please upload a PDF or DOC/DOCX file");
      return;
    }

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);

      const res = await fetch("http://localhost:8000/api/upload-jd", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) throw new Error("Failed to upload Job Description");

      const data = await res.json();
      setJD(data.extracted_text);
      setJDFileName(file.name);
    } catch (error) {
      console.error("JD upload failed:", error);
      alert("Job Description upload failed");
    } finally {
      setUploading(false);
    }
  };

  const handleSave = () => {
    const data = {
      selectedModel,
      openAIKey,
      geminiKey,
      mistralKey,
      groqKey,
      resumeFileName,
      jdFileName,
      jd,
    };
    localStorage.setItem("ats_setup_data", JSON.stringify(data));
    setSaveMessage("✅ Setup data saved successfully!");
    setTimeout(() => setSaveMessage(""), 4000);
  };

  return (
    <div className="container mx-auto px-6 pt-8">
      <h1 className="text-3xl font-bold text-black mb-6">ATS Smart Advisor Setup</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* AI Model Selection */}
        <Card className="bg-white border border-gray-200">
          <CardHeader>
            <CardTitle className="text-black">Select AI Model</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <select
              className="w-full p-2 border border-gray-300 rounded-md text-black bg-white"
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
            >
              <option value="Mistral Small">Mistral Small</option>
              <option value="Groq">Groq (Llama)</option>
              <option value="Gemini">Gemini</option>
              <option value="OpenAI">OpenAI (Requires API Key)</option>
            </select>

            {selectedModel === "OpenAI" && (
              <input
                type="text"
                placeholder="Enter your OpenAI API Key"
                className="w-full p-2 border border-gray-300 rounded-md text-black bg-white"
                value={openAIKey}
                onChange={(e) => setOpenAIKey(e.target.value)}
              />
            )}

            {selectedModel === "Gemini" && (
              <input
                type="text"
                placeholder="Enter your Gemini API Key"
                className="w-full p-2 border border-gray-300 rounded-md text-black bg-white"
                value={geminiKey}
                onChange={(e) => setGeminiKey(e.target.value)}
              />
            )}

            {selectedModel === "Mistral Small" && (
              <input
                type="text"
                placeholder="Enter your Mistral API Key"
                className="w-full p-2 border border-gray-300 rounded-md text-black bg-white"
                value={mistralKey}
                onChange={(e) => setMistralKey(e.target.value)}
              />
            )}

            {selectedModel === "Groq" && (
              <input
                type="text"
                placeholder="Enter your Groq API Key"
                className="w-full p-2 border border-gray-300 rounded-md text-black bg-white"
                value={groqKey}
                onChange={(e) => setGroqKey(e.target.value)}
              />
            )}
          </CardContent>
        </Card>

        {/* Resume & Job Description Upload */}
        <Card className="bg-white border border-gray-200">
          <CardHeader>
            <CardTitle className="text-black">Resume & Job Description</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <label className="text-black font-medium">Upload your Resume (PDF or DOC):</label>
              <input
                type="file"
                accept=".pdf,.doc,.docx"
                className="block w-full text-sm text-gray-700 border border-gray-300 rounded-md p-2 cursor-pointer bg-white"
                onChange={handleResumeUpload}
              />
              {uploading && <p className="text-sm text-gray-500">Uploading and extracting...</p>}
              {resumeFileName && <p className="text-sm text-gray-600 mt-1">Selected File: {resumeFileName}</p>}
            </div>

            <div className="space-y-2">
              <label className="text-black font-medium">Upload Job Description (PDF or DOC):</label>
              <input
                type="file"
                accept=".pdf,.doc,.docx"
                className="block w-full text-sm text-gray-700 border border-gray-300 rounded-md p-2 cursor-pointer bg-white"
                onChange={handleJDUpload}
              />
              {jdFileName && <p className="text-sm text-gray-600 mt-1">Selected File: {jdFileName}</p>}
            </div>

            <textarea
              placeholder="Paste Job Description here..."
              className="w-full p-2 border border-gray-300 rounded-md text-black bg-white h-32"
              value={jd}
              onChange={(e) => setJD(e.target.value)}
            />
          </CardContent>
        </Card>
      </div>

      <div className="mt-6 text-right">
        <Button className="bg-black hover:bg-gray-900 text-white px-6" onClick={handleSave}>
          Save & Continue
        </Button>
        {saveMessage && <p className="mt-3 text-green-600 font-medium text-sm">{saveMessage}</p>}
      </div>
    </div>
  );
}
