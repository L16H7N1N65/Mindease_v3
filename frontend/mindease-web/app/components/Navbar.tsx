"use client";


import React from "react";
import { cn } from "@/lib/utils";

type NavbarProps = {
  className?: string;
  logo?: React.ReactNode;
  children?: React.ReactNode;
  transparent?: boolean;
  sticky?: boolean;
};

export const Navbar = ({
  className,
  logo,
  children,
  transparent = false,
  sticky = true,
}: NavbarProps) => {
  return (
    <header
      className={cn(
        "w-full py-4 px-4 md:px-6 flex items-center justify-between",
        sticky && "sticky top-0 z-50",
        transparent ? "bg-transparent" : "bg-background/80 backdrop-blur-sm border-b border-border",
        className
      )}
    >
      <div className="flex items-center gap-2">
        {logo}
      </div>
      <nav className="hidden md:flex items-center gap-6">
        {children}
      </nav>
      <div className="md:hidden">
        {/* Mobile menu button would go here */}
        <button className="p-2">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth={1.5}
            stroke="currentColor"
            className="w-6 h-6"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5"
            />
          </svg>
        </button>
      </div>
    </header>
  );
};
