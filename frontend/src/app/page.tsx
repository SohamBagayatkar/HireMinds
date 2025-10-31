"use client";

import { useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Briefcase } from "lucide-react";

export default function LandingPage() {
  const router = useRouter();

  const atsModuleData = {
    title: "ATS Smart Advisor",
    description:
      "AI-powered tools to analyze your resume, optimize it for ATS, and boost your job search.",
    icon: Briefcase,
    path: "/ats-home",
  };

  const Icon = atsModuleData.icon;

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-white px-6">
      <h1 className="text-4xl font-bold mb-8 text-black text-center">
        HireMinds
      </h1>
      <p className="text-gray-700 mb-12 max-w-2xl text-center">
        Access AI-powered tools to analyze your resume and boost your job search.
      </p>

      <div className="max-w-sm w-full">
        <Card
          onClick={() => router.push(atsModuleData.path)}
          className="cursor-pointer bg-white border border-gray-200 hover:shadow-lg transition-shadow"
        >
          <CardHeader>
            <CardTitle className="flex items-center gap-3 text-xl text-black">
              <Icon className="w-6 h-6 text-black" />
              {atsModuleData.title}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-700">{atsModuleData.description}</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
