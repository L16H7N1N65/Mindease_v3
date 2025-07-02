"use client";

import React from "react";
import { usePathname } from "next/navigation";
import Link from "next/link";
import { DashboardGuard } from "@/components/dashboard/dashboard-shells";
import {
  SidebarProvider,
  Sidebar,
  SidebarTrigger,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
  SidebarSeparator,
} from "@/components/ui/sidebar";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  Home,
  BarChart3,
  FileText,
  User,
  Settings,
  HelpCircle,
  Menu,
} from "lucide-react";

const useAuth = () => ({
  user: {
    name: "Test User",
    email: "user@example.com",
    avatarUrl: "/avatars/user.png",
    role: "user" as "user" | "admin",
  },
  isAuthenticated: true,
  isLoading: false,
});

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { user, isAuthenticated, isLoading } = useAuth();
  const pathname = usePathname();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-background text-foreground">
        <p className="text-muted-foreground">Loading...</p>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-background text-foreground">
        <p className="text-muted-foreground">
          Please log in to access this page
        </p>
      </div>
    );
  }

  const isAdminRoute = pathname.startsWith("/dashboard/admin");
  const isAdmin = user.role === "admin";

  return (
    <DashboardGuard
      userRole={user.role}
      requiredRole={isAdminRoute ? "admin" : "user"}
      fallback={
        <div className="flex items-center justify-center min-h-screen bg-background text-foreground">
          <div className="text-center">
            <h2 className="text-2xl font-bold">Access Denied</h2>
            <p className="mt-2 text-muted-foreground">
              You don't have permission to access this page
            </p>
          </div>
        </div>
      }
    >
      <SidebarProvider>
        <div className="flex h-screen bg-background text-foreground">
          {/* Mobile menu button */}
          <button className="md:hidden p-2 m-2 rounded-lg hover:bg-muted" aria-label="Open sidebar">
            <Menu className="h-6 w-6" />
          </button>

          <Sidebar side="left" collapsible="icon" variant="sidebar">
            <SidebarHeader>
              <div className="px-4 py-3 text-lg font-bold">MindEase</div>
            </SidebarHeader>

            <SidebarSeparator />

            <SidebarContent>
              <SidebarMenu>
                <SidebarMenuItem>
                  <SidebarMenuButton
                    asChild
                    isActive={pathname === "/dashboard"}
                    className="flex items-center px-3 py-2 rounded-lg hover:bg-muted"
                  >
                    <Link href="/dashboard">
                      <Home className="mr-2 h-5 w-5" />
                      Overview
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>

                {isAdmin && (
                  <SidebarMenuItem>
                    <SidebarMenuButton
                      asChild
                      isActive={pathname.startsWith("/dashboard/analytics")}
                      className="flex items-center px-3 py-2 rounded-lg hover:bg-muted"
                    >
                      <Link href="/dashboard/analytics">
                        <BarChart3 className="mr-2 h-5 w-5" />
                        Analytics
                      </Link>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                )}

                <SidebarMenuItem>
                  <SidebarMenuButton
                    asChild
                    isActive={pathname.startsWith("/dashboard/reports")}
                    className="flex items-center px-3 py-2 rounded-lg hover:bg-muted"
                  >
                    <Link href="/dashboard/reports">
                      <FileText className="mr-2 h-5 w-5" />
                      Reports
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>

                <SidebarMenuItem>
                  <SidebarMenuButton
                    asChild
                    isActive={pathname.startsWith("/dashboard/profile")}
                    className="flex items-center px-3 py-2 rounded-lg hover:bg-muted"
                  >
                    <Link href="/dashboard/profile">
                      <User className="mr-2 h-5 w-5" />
                      Profile
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>

                <SidebarMenuItem>
                  <SidebarMenuButton
                    asChild
                    isActive={pathname.startsWith("/dashboard/settings")}
                    className="flex items-center px-3 py-2 rounded-lg hover:bg-muted"
                  >
                    <Link href="/dashboard/settings">
                      <Settings className="mr-2 h-5 w-5" />
                      Settings
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>

                <SidebarMenuItem>
                  <SidebarMenuButton
                    asChild
                    isActive={pathname.startsWith("/dashboard/faq")}
                    className="flex items-center px-3 py-2 rounded-lg hover:bg-muted"
                  >
                    <Link href="/dashboard/faq">
                      <HelpCircle className="mr-2 h-5 w-5" />
                      FAQ
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              </SidebarMenu>
            </SidebarContent>

            <SidebarFooter>
              <div className="flex items-center px-4 py-3 space-x-3 hover:bg-muted rounded-lg">
                <Avatar>
                  <AvatarImage src={user.avatarUrl} alt={user.name} />
                  <AvatarFallback>
                    {user.name.charAt(0).toUpperCase()}
                  </AvatarFallback>
                </Avatar>
                <div className="flex flex-col">
                  <span className="text-sm font-medium">{user.name}</span>
                  <span className="text-xs text-muted-foreground">
                    {user.email}
                  </span>
                </div>
              </div>
            </SidebarFooter>
          </Sidebar>

          <main className="flex-1 overflow-auto px-4 py-6 sm:px-6 lg:px-8">{children}</main>
        </div>
      </SidebarProvider>
    </DashboardGuard>
  );
}
