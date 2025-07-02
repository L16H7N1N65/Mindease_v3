import React from "react";

interface DashboardHeaderProps {
  heading: string;
  text: string;
}

export const DashboardHeader: React.FC<DashboardHeaderProps> = ({ heading, text }) => {
  return (
    <header className="p-4 bg-gray-100 border-b">
      <h1 className="text-2xl font-bold">{heading}</h1>
      <p className="text-gray-600">{text}</p>
    </header>
  );
};
