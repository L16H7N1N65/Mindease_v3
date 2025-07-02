// app/components/dashboard-shell.tsx
import React, { ReactNode } from 'react';

interface DashboardShellProps {
  children: ReactNode;
}

export const DashboardShell = ({ children }: DashboardShellProps) => {
  return (
    <div className="min-h-screen flex flex-col">
      <header>
        {/* You can include DashboardHeader here if needed */}
      </header>
      <main className="flex-1 p-4">
        {children}
      </main>
      <footer className="p-4 bg-gray-100 text-center">
        Dashboard Footer
      </footer>
    </div>
  );
};
