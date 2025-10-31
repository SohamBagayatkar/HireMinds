"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Image from "next/image";

const templates = [
  {
    id: 1,
    name: "Microsoft Create",
    description: "Professional free ATS-friendly resume templates directly from Microsoft.",
    preview: "/template/microsoft.png",
    link: "https://create.microsoft.com/en-us/templates/ats-resumes",
  },
  {
    id: 2,
    name: "My Resume Templates",
    description: "Free, customizable ATS-ready resume templates for job seekers.",
    preview: "/template/myresumetemplates.png",
    link: "https://www.my-resume-templates.com/free-ats-friendly-resume-templates/",
  },
  {
    id: 3,
    name: "TechGuruPlus",
    description: "Modern collection of ATS-compliant resume templates with clean design.",
    preview: "/template/techguruplus.png",
    link: "https://techguruplus.com/ats-friendly-resume-templates/",
  },
];

export default function ResumeTemplatesPage() {
  return (
    <div className="p-6">
      {/* Page Title */}
      <h1 className="text-2xl font-bold mb-6">ATS-Friendly Resume Templates</h1>

      {/* Grid of Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {templates.map((template) => (
          <Card key={template.id} className="rounded-2xl shadow-md bg-white border border-gray-200">
            <CardHeader>
              <CardTitle className="text-lg font-semibold">{template.name}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="w-full h-48 relative mb-4">
                <Image
                  src={template.preview}
                  alt={template.name}
                  fill
                  className="object-contain rounded-md border"
                />
              </div>
              <p className="text-sm text-gray-700 mb-4">{template.description}</p>
              <Button asChild className="w-full">
                <a href={template.link} target="_blank" rel="noopener noreferrer">
                  Visit Website
                </a>
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
