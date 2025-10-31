import { ReactNode } from "react";
import Sidebar from "@/components/Sidebar";
import Navbar from "@/components/Navbar";

interface ATSLayoutProps {
  children: ReactNode;
}

export default function ATSLayout({ children }: ATSLayoutProps) {
  return (
    <div className="flex flex-col min-h-screen bg-white text-black">
      {/* Full-width Navbar at the top */}
      <Navbar />

      {/* Content Area with Sidebar + Page */}
      <div className="flex flex-1">
        {/* ATS Sidebar */}
        <Sidebar />

        {/* Page Content */}
        <main className="flex-1 p-6">{children}</main>
      </div>
    </div>
  );
}
