import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { DashboardHeader } from "@/components/dashboard-header"
import { DashboardShell } from "@/components/dashboard-shell"

import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

export default function AnalyticsPage() {
  return (
    <DashboardShell>
      <DashboardHeader
        heading="Analytics Dashboard"
        text="Track team mental health metrics and usage patterns."
      />
      
      <div className="flex items-center justify-between space-y-2">
        <h2 className="text-3xl font-bold tracking-tight">Overview</h2>
        <div className="flex items-center space-x-2">
          <Select defaultValue="week">
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Select timeframe" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="day">Last 24 hours</SelectItem>
              <SelectItem value="week">Last 7 days</SelectItem>
              <SelectItem value="month">Last 30 days</SelectItem>
              <SelectItem value="quarter">Last 90 days</SelectItem>
            </SelectContent>
          </Select>
          <Button variant="outline">Export</Button>
        </div>
      </div>
      
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Users</CardTitle>
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">42</div>
            <p className="text-xs text-muted-foreground">+12% from last week</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Therapy Sessions</CardTitle>
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
            </svg>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">187</div>
            <p className="text-xs text-muted-foreground">+24% from last week</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Average Stress Level</CardTitle>
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 8v8m-4-5v5m-4-2v2m-2 4h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">3.2/10</div>
            <p className="text-xs text-muted-foreground">-8% from last week</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Mood Improvement</CardTitle>
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">+18%</div>
            <p className="text-xs text-muted-foreground">+5% from last week</p>
          </CardContent>
        </Card>
      </div>
      
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        <Card className="col-span-4">
          <CardHeader>
            <CardTitle>Mood Trends</CardTitle>
            <CardDescription>
              Average mood scores across your organization
            </CardDescription>
          </CardHeader>
          <CardContent className="pl-2">
            <div className="h-[300px]">
              {/* This would be a real chart component in production */}
              <div className="flex items-center justify-center h-full border-2 border-dashed border-muted-foreground rounded-md">
                <p className="text-sm text-muted-foreground">Line chart showing mood trends over time would appear here</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card className="col-span-3">
          <CardHeader>
            <CardTitle>Usage by Department</CardTitle>
            <CardDescription>
              App usage broken down by department
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[300px]">
              {/* This would be a real chart component in production */}
              <div className="flex items-center justify-center h-full border-2 border-dashed border-muted-foreground rounded-md">
                <p className="text-sm text-muted-foreground">Bar chart showing usage by department would appear here</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
      
      <div className="mt-4">
        <Tabs defaultValue="sessions">
          <TabsList>
            <TabsTrigger value="sessions">Session Analytics</TabsTrigger>
            <TabsTrigger value="users">User Analytics</TabsTrigger>
            <TabsTrigger value="features">Feature Usage</TabsTrigger>
          </TabsList>
          <TabsContent value="sessions" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Session Analytics</CardTitle>
                <CardDescription>
                  Detailed breakdown of therapy sessions
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <h3 className="text-lg font-medium">Session Duration</h3>
                      <div className="mt-2 space-y-2">
                        <div className="flex justify-between">
                          <span className="text-sm">Average Duration</span>
                          <span className="text-sm font-medium">12 minutes</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm">Longest Session</span>
                          <span className="text-sm font-medium">45 minutes</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm">Shortest Session</span>
                          <span className="text-sm font-medium">3 minutes</span>
                        </div>
                      </div>
                    </div>
                    <div>
                      <h3 className="text-lg font-medium">Session Types</h3>
                      <div className="mt-2 space-y-2">
                        <div className="flex justify-between">
                          <span className="text-sm">Rule-based CBT</span>
                          <span className="text-sm font-medium">78%</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm">Mistral 7B Fallback</span>
                          <span className="text-sm font-medium">22%</span>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div>
                    <h3 className="text-lg font-medium">Popular Session Topics</h3>
                    <div className="mt-2 space-y-2">
                      <div className="flex justify-between items-center">
                        <span className="text-sm">Work Stress</span>
                        <div className="w-2/3 bg-muted rounded-full h-2">
                          <div className="bg-primary h-2 rounded-full" style={{ width: '65%' }}></div>
                        </div>
                        <span className="text-sm font-medium">65%</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm">Anxiety</span>
                        <div className="w-2/3 bg-muted rounded-full h-2">
                          <div className="bg-primary h-2 rounded-full" style={{ width: '48%' }}></div>
                        </div>
                        <span className="text-sm font-medium">48%</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm">Relationships</span>
                        <div className="w-2/3 bg-muted rounded-full h-2">
                          <div className="bg-primary h-2 rounded-full" style={{ width: '32%' }}></div>
                        </div>
                        <span className="text-sm font-medium">32%</span>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
          <TabsContent value="users" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>User Analytics</CardTitle>
                <CardDescription>
                  User engagement and demographics
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <h3 className="text-lg font-medium">User Engagement</h3>
                      <div className="mt-2 space-y-2">
                        <div className="flex justify-between">
                          <span className="text-sm">Daily Active Users</span>
                          <span className="text-sm font-medium">28</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm">Weekly Active Users</span>
                          <span className="text-sm font-medium">42</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm">Monthly Active Users</span>
                          <span className="text-sm font-medium">56</span>
                        </div>
                      </div>
                    </div>
                    <div>
                      <h3 className="text-lg font-medium">Language Preference</h3>
                      <div className="mt-2 space-y-2">
                        <div className="flex justify-between">
                          <span className="text-sm">English</span>
                          <span className="text-sm font-medium">82%</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm">French</span>
                          <span className="text-sm font-medium">18%</span>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div>
                    <h3 className="text-lg font-medium">User Retention</h3>
                    <div className="mt-2 space-y-2">
                      <div className="flex justify-between items-center">
                        <span className="text-sm">Week 1</span>
                        <div className="w-2/3 bg-muted rounded-full h-2">
                          <div className="bg-primary h-2 rounded-full" style={{ width: '95%' }}></div>
                        </div>
                        <span className="text-sm font-medium">95%</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm">Week 2</span>
                        <div className="w-2/3 bg-muted rounded-full h-2">
                          <div className="bg-primary h-2 rounded-full" style={{ width: '82%' }}></div>
                        </div>
                        <span className="text-sm font-medium">82%</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm">Week 4</span>
                        <div className="w-2/3 bg-muted rounded-full h-2">
                          <div className="bg-primary h-2 rounded-full" style={{ width: '75%' }}></div>
                        </div>
                        <span className="text-sm font-medium">75%</span>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
          <TabsContent value="features" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Feature Usage</CardTitle>
                <CardDescription>
                  Usage statistics for app features
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <h3 className="text-lg font-medium">Feature Popularity</h3>
                    <div className="mt-2 space-y-2">
                      <div className="flex justify-between items-center">
                        <span className="text-sm">Therapy Chat</span>
                        <div className="w-2/3 bg-muted rounded-full h-2">
                          <div className="bg-primary h-2 rounded-full" style={{ width: '92%' }}></div>
                        </div>
                        <span className="text-sm font-medium">92%</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm">Facial Mood Detection</span>
                        <div className="w-2/3 bg-muted rounded-full h-2">
                          <div className="bg-primary h-2 rounded-full" style={{ width: '68%' }}></div>
                        </div>
                        <span className="text-sm font-medium">68%</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm">Voice Mood Analysis</span>
                        <div className="w-2/3 bg-muted rounded-full h-2">
                          <div className="bg-primary h-2 rounded-full" style={{ width: '45%' }}></div>
                        </div>
                        <span className="text-sm font-medium">45%</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm">Therapy Buddy</span>
                        <div className="w-2/3 bg-muted rounded-full h-2">
                          <div className="bg-primary h-2 rounded-full" style={{ width: '32%' }}></div>
                        </div>
                        <span className="text-sm font-medium">32%</span>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
              <CardFooter>
                <Button variant="outline" className="w-full">Download Detailed Report</Button>
              </CardFooter>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </DashboardShell>
  )
}
