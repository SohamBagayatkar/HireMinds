"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Home, FileText, User, Menu, Settings, Files } from "lucide-react";
import { useState } from "react";

export default function Sidebar() {
  const pathname = usePathname();
  const [isOpen, setIsOpen] = useState(true);

  const navItems = [
    { name: "Home", href: "/ats-home", icon: Home },
    { name: "Setup", href: "/ats-home/setup", icon: Settings },
    { name: "Resume Templates", href: "/ats-home/resume-templates", icon: Files },
    { name: "Gap Analyzer", href: "/ats-home/gap-analyzer", icon: FileText },
    { name: "Resume Advisor", href: "/ats-home/resume-advisor", icon: User },
    { name: "Resume Screening", href: "/ats-home/resume-screening", icon: Menu },
  ];

  return (
    <aside
      className={`bg-black text-white min-h-screen flex flex-col ${
        isOpen ? "w-64" : "w-16"
      } transition-all duration-300`}
    >
      {/* Sidebar Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-700">
        <span className={`${isOpen ? "text-xl font-bold" : "hidden"}`}>
          ATS Advisor
        </span>
        <button
          className="text-gray-300 hover:text-white"
          onClick={() => setIsOpen(!isOpen)}
        >
          <Menu className="w-6 h-6" />
        </button>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 p-2">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;

          return (
            <Link
              key={item.name}
              href={item.href}
              className={`flex items-center gap-3 p-3 rounded-md mb-1 transition-colors ${
                isActive
                  ? "bg-white text-black font-medium"
                  : "text-gray-300 hover:bg-gray-800"
              }`}
            >
              <Icon className="w-5 h-5" />
              {isOpen && <span>{item.name}</span>}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
