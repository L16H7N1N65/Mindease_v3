"use client"

import React from 'react'
import { useRouter } from 'next/navigation'
import { Card } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import { AdminDashboardShell } from "@/components/dashboard/dashboard-shells"
import { 
  Users, 
  Settings, 
  FileText, 
  BarChart3, 
  Shield, 
  Database 
} from "lucide-react"

export default function AdminDashboardPage() {
  return (
    <div className="flex min-h-screen flex-col">
      <main className="flex-1 p-6">
        <AdminDashboardShell>
          <Tabs defaultValue="overview" className="space-y-4">
            <TabsList className="grid grid-cols-6 h-auto">
              <TabsTrigger value="overview" className="flex items-center gap-2 py-3">
                <BarChart3 className="h-4 w-4" />
                <span>Overview</span>
              </TabsTrigger>
              <TabsTrigger value="users" className="flex items-center gap-2 py-3">
                <Users className="h-4 w-4" />
                <span>Users</span>
              </TabsTrigger>
              <TabsTrigger value="content" className="flex items-center gap-2 py-3">
                <FileText className="h-4 w-4" />
                <span>Content</span>
              </TabsTrigger>
              <TabsTrigger value="roles" className="flex items-center gap-2 py-3">
                <Shield className="h-4 w-4" />
                <span>Roles</span>
              </TabsTrigger>
              <TabsTrigger value="data" className="flex items-center gap-2 py-3">
                <Database className="h-4 w-4" />
                <span>Data</span>
              </TabsTrigger>
              <TabsTrigger value="settings" className="flex items-center gap-2 py-3">
                <Settings className="h-4 w-4" />
                <span>Settings</span>
              </TabsTrigger>
            </TabsList>
            
            <TabsContent value="overview" className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <Card className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Total Users</p>
                      <h3 className="text-2xl font-bold">2,543</h3>
                    </div>
                    <div className="rounded-full bg-primary/10 p-2">
                      <Users className="h-5 w-5 text-primary" />
                    </div>
                  </div>
                  <div className="mt-4 text-xs text-muted-foreground">
                    <span className="text-green-500">+12%</span> from last month
                  </div>
                </Card>
                
                <Card className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Active Sessions</p>
                      <h3 className="text-2xl font-bold">187</h3>
                    </div>
                    <div className="rounded-full bg-primary/10 p-2">
                      <FileText className="h-5 w-5 text-primary" />
                    </div>
                  </div>
                  <div className="mt-4 text-xs text-muted-foreground">
                    <span className="text-green-500">+5%</span> from yesterday
                  </div>
                </Card>
                
                <Card className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Database Size</p>
                      <h3 className="text-2xl font-bold">4.2 GB</h3>
                    </div>
                    <div className="rounded-full bg-primary/10 p-2">
                      <Database className="h-5 w-5 text-primary" />
                    </div>
                  </div>
                  <div className="mt-4 text-xs text-muted-foreground">
                    <span className="text-yellow-500">+28%</span> from last week
                  </div>
                </Card>
                
                <Card className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">System Status</p>
                      <h3 className="text-2xl font-bold">Healthy</h3>
                    </div>
                    <div className="rounded-full bg-green-100 p-2 dark:bg-green-900">
                      <Shield className="h-5 w-5 text-green-600 dark:text-green-400" />
                    </div>
                  </div>
                  <div className="mt-4 text-xs text-muted-foreground">
                    All services operational
                  </div>
                </Card>
              </div>
              
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
                <Card className="col-span-4 p-6">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-medium">User Activity</h3>
                    <div className="flex items-center gap-2">
                      <Button variant="outline" size="sm">Daily</Button>
                      <Button variant="outline" size="sm">Weekly</Button>
                      <Button variant="outline" size="sm">Monthly</Button>
                    </div>
                  </div>
                  <div className="mt-4 h-[300px] flex items-center justify-center border rounded-md">
                    <p className="text-muted-foreground">Activity chart placeholder</p>
                  </div>
                </Card>
                
                <Card className="col-span-3 p-6">
                  <h3 className="text-lg font-medium">Recent Signups</h3>
                  <div className="mt-4 space-y-4">
                    {[1, 2, 3, 4, 5].map((i) => (
                      <div key={i} className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div className="h-9 w-9 rounded-full bg-primary/10 flex items-center justify-center">
                            <span className="text-xs font-medium text-primary">
                              {String.fromCharCode(64 + i)}
                            </span>
                          </div>
                          <div>
                            <p className="text-sm font-medium">User{i}@example.com</p>
                            <p className="text-xs text-muted-foreground">Joined today</p>
                          </div>
                        </div>
                        <Button variant="ghost" size="sm">View</Button>
                      </div>
                    ))}
                  </div>
                </Card>
              </div>
            </TabsContent>
            
            <TabsContent value="users" className="space-y-4">
              <Card className="p-6">
                <h3 className="text-lg font-medium mb-4">User Management</h3>
                <div className="border rounded-md p-4">
                  <p className="text-muted-foreground text-center">User management interface placeholder</p>
                </div>
              </Card>
            </TabsContent>
            
            <TabsContent value="content" className="space-y-4">
              <Card className="p-6">
                <h3 className="text-lg font-medium mb-4">Content Management</h3>
                <div className="border rounded-md p-4">
                  <p className="text-muted-foreground text-center">Content management interface placeholder</p>
                </div>
              </Card>
            </TabsContent>
            
            <TabsContent value="roles" className="space-y-4">
              <Card className="p-6">
                <h3 className="text-lg font-medium mb-4">Role Management</h3>
                <div className="border rounded-md p-4">
                  <p className="text-muted-foreground text-center">Role management interface placeholder</p>
                </div>
              </Card>
            </TabsContent>
            
            <TabsContent value="data" className="space-y-4">
              <Card className="p-6">
                <h3 className="text-lg font-medium mb-4">Data Management</h3>
                <div className="border rounded-md p-4">
                  <p className="text-muted-foreground text-center">Data management interface placeholder</p>
                </div>
              </Card>
            </TabsContent>
            
            <TabsContent value="settings" className="space-y-4">
              <Card className="p-6">
                <h3 className="text-lg font-medium mb-4">System Settings</h3>
                <div className="border rounded-md p-4">
                  <p className="text-muted-foreground text-center">Settings interface placeholder</p>
                </div>
              </Card>
            </TabsContent>
          </Tabs>
        </AdminDashboardShell>
      </main>
    </div>
  )
}
