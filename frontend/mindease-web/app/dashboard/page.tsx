"use client";

import React from "react";
import { Card } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { UserDashboardShell } from "@/components/dashboard/dashboard-shells";
import { LineChart } from "@/components/ui/line-chart";
import Link from "next/link";

const useAuth = () => ({
  user: {
    name: "Test User",
    email: "user@example.com",
    avatarUrl: "/avatars/user.png",
    role: "user" as const,
  },
  isAuthenticated: true,
  isLoading: false,
});

export default function UserDashboardPage() {
  const { user } = useAuth();

  const metrics = [
    { label: "Mood Score", value: "7.5/10", meta: "+2% from last week" },
    { label: "Therapy Sessions", value: "12", meta: "2 sessions this week" },
    { label: "Mindfulness Minutes", value: "156", meta: "+23% from last month" },
    { label: "Streak", value: "7 days", meta: "Keep it going!" },
  ];

  const activities = [
    { title: "Completed CBT Session", time: "Yesterday at 2:30 PM" },
    { title: "Breathing Exercise", time: "Today at 9:15 AM" },
    { title: "Buddy Chat", time: "Today at 11:30 AM" },
  ];

  return (
    <div className="flex flex-col min-h-screen bg-background text-foreground">
      <main className="flex-1 px-4 py-6 sm:px-6 lg:px-8 max-w-7xl mx-auto">
        <UserDashboardShell>
          {/* Header */}
          <div className="mb-6">
            <h1 className="text-3xl font-bold">Welcome back, {user.name}!</h1>
            <p className="mt-1 text-sm text-muted-foreground">
              Here's an overview of your wellness journey
            </p>
          </div>

          {/* Tabs */}
          <Tabs defaultValue="overview" className="space-y-6">
            {/* <TabsList className="grid grid-cols-2 sm:grid-cols-4 gap-1 bg-muted p-1 rounded-lg">
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="analytics" disabled>
                Analytics
              </TabsTrigger>
              <TabsTrigger value="reports" disabled>
                Reports
              </TabsTrigger>
              <TabsTrigger value="notifications" disabled>
                Notifications
              </TabsTrigger>
            </TabsList> */}

            <TabsContent value="overview" className="space-y-6">
              {/* Metrics */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {metrics.map((m) => (
                  <Card
                    key={m.label}
                    className="p-4 border border-border shadow-xs rounded-lg"
                  >
                    <h3 className="text-sm font-medium">{m.label}</h3>
                    <div className="mt-2 text-2xl font-bold">{m.value}</div>
                    <p className="mt-1 text-xs text-muted-foreground">
                      {m.meta}
                    </p>
                  </Card>
                ))}
              </div>

              {/* Charts & Activities */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-[repeat(4,_minmax(0,4fr))_repeat(3,_minmax(0,3fr))] gap-4">
                {/* Mood Trends */}
                <Card className="p-6 border border-border shadow-xs rounded-lg">
                  <h3 className="text-lg font-semibold">Mood Trends</h3>
                  <p className="mt-1 text-sm text-muted-foreground">
                    Your mood patterns over the past 30 days
                  </p>
                  <div className="mt-4 h-52">
                    <LineChart
                      data={[
                        { x: "2025-03-10", y: 65 },
                        { x: "2025-03-15", y: 45 },
                        { x: "2025-03-20", y: 70 },
                        { x: "2025-03-25", y: 75 },
                        { x: "2025-03-30", y: 60 },
                        { x: "2025-04-05", y: 80 },
                      ]}
                    />
                  </div>
                </Card>

                {/* Recent Activities */}
                <Card className="p-6 border border-border shadow-xs rounded-lg col-span-1 md:col-span-2 lg:col-span-3">
                  <h3 className="text-lg font-semibold">Recent Activities</h3>
                  <p className="mt-1 text-sm text-muted-foreground">
                    Your latest interactions and progress
                  </p>
                  <div className="mt-4 space-y-4">
                    {activities.map((act) => (
                      <div
                        key={act.title}
                        className="flex items-center space-x-3"
                      >
                        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10">
                          {/* replace with appropriate icon */}
                          <span className="text-primary font-medium">
                            {act.title.charAt(0)}
                          </span>
                        </div>
                        <div>
                          <p className="text-sm font-medium">{act.title}</p>
                          <p className="text-xs text-muted-foreground">
                            {act.time}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </Card>
              </div>

              {/* Wellness Plan */}
              <Card className="p-6 border border-border shadow-xs rounded-lg">
                <h3 className="text-lg font-medium">Your Wellness Plan</h3>
                <p className="mt-1 text-sm text-muted-foreground">
                  Personalized recommendations for your mental health journey
                </p>
                <div className="mt-4 space-y-4">
                  <div className="flex items-start space-x-4">
                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10">
                      {/* icon */}
                      <span className="text-primary">🧘</span>
                    </div>
                    <div className="flex-1">
                      <h4 className="font-medium">Daily Mindfulness Practice</h4>
                      <p className="mt-1 text-sm text-muted-foreground">
                        5–10 minutes of guided meditation each morning
                      </p>
                      <Button
                        asChild
                        size="sm"
                        variant="outline"
                        className="mt-2"
                      >
                        <Link href="/dashboard/therapy/breathing-exercise">
                          Start Practice
                        </Link>
                      </Button>
                    </div>
                  </div>

                  <div className="flex items-start space-x-4">
                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10">
                      {/* icon */}
                      <span className="text-primary">💡</span>
                    </div>
                    <div className="flex-1">
                      <h4 className="font-medium">Weekly CBT Session</h4>
                      <p className="mt-1 text-sm text-muted-foreground">
                        Schedule your next therapy session for this week
                      </p>
                      <Button
                        asChild
                        size="sm"
                        variant="outline"
                        className="mt-2"
                      >
                        <Link href="/dashboard/therapy">
                          Schedule Session
                        </Link>
                      </Button>
                    </div>
                  </div>

                  <div className="flex items-start space-x-4">
                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10">
                      {/* icon */}
                      <span className="text-primary">🤝</span>
                    </div>
                    <div className="flex-1">
                      <h4 className="font-medium">Buddy Check-in</h4>
                      <p className="mt-1 text-sm text-muted-foreground">
                        Connect with your therapy buddy for mutual support
                      </p>
                      <Button size="sm" variant="outline" className="mt-2">
                        Message Buddy
                      </Button>
                    </div>
                  </div>
                </div>
              </Card>
            </TabsContent>
          </Tabs>
        </UserDashboardShell>
      </main>
    </div>
  );
}
