"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { FileText,  User, Briefcase } from "lucide-react";

export default function ATSHomePage() {
  const router = useRouter();

  // Redirect to setup page if setup data is not found
  useEffect(() => {
    const setupData = localStorage.getItem("ats_setup_data");
    if (!setupData) {
      router.push("/setup");
    }
  }, [router]);

  const features = [
    {
      title: "Gap Analyzer",
      description:
        "Analyze your resume against a job description to find missing keywords and skills.",
      icon: FileText,
    },
    {
      title: "Resume Advisor",
      description: "Get 10 AI-powered suggestions to improve your resume instantly.",
      icon: User,
    },
    {
      title: "Resume Screening",
      description: "Rank upto 10 resumes against a job description to find the best candidate .",
      icon: Briefcase,
    },
  ];

  const steps = [
    {
      step: "Step 1",
      title: "Setup",
      description:
        "Go to setup page, select LLM & upload your resume and job description.",
    },
    {
      step: "Step 2",
      title: "Gap Analyzer",
      description:
        "Run Analysis to check the gap between your resume and job description and generate ATS score.",
    },
    {
      step: "Step 3",
      title: "Resume Advisor",
      description:
        "Click on Get Advice to receive improvement suggestions on your resume.",
    },
    {
      step: "Step 4",
      title: "Resume Screening",
      description:
        "Generate interview tips & YouTube course links related to the job description.",
    },
    {
      step: "Step 5",
      title: "Search Jobs",
      description:
        "Select 3 skills from your resume, enter a location, choose a site (LinkedIn, Indeed, Glassdoor) to find jobs.",
    },
  ];

  return (
    <div className="container mx-auto px-6 pt-8">
      {/* Header Section */}
      <div className="mb-10 text-center">
        <h1 className="text-4xl font-bold text-black mb-2">
          Welcome to ATS Smart Advisor
        </h1>
        <p className="text-gray-700 max-w-2xl mx-auto">
          Upload your resume and job description once, then explore AI-powered
          tools to enhance your job search.
        </p>
      </div>

      {/* Feature Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {features.map((feature, index) => {
          const Icon = feature.icon;
          return (
            <Card
              key={index}
              className="bg-white border border-gray-200 hover:shadow-lg transition-shadow"
            >
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-black text-lg">
                  <Icon className="w-5 h-5 text-black" />
                  {feature.title}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-700 text-sm">{feature.description}</p>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Steps Section */}
      <div className="mt-16">
        <h2 className="text-2xl font-bold text-center mb-8 text-black">
          Steps For User
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-6">
          {steps.map((item, index) => (
            <Card
              key={index}
              className="bg-white border border-gray-200 hover:shadow-lg transition-shadow text-center"
            >
              <CardHeader>
                <CardTitle className="flex flex-col items-center text-black text-lg">
                  <div className="w-10 h-10 flex items-center justify-center rounded-full bg-black text-white font-bold mb-2">
                    {index + 1}
                  </div>
                  {item.title}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-700 text-sm">{item.description}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}
