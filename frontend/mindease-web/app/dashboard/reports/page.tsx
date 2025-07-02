import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { DashboardHeader } from "@/components/dashboard-header";
import { DashboardShell } from "@/components/dashboard-shell";
import { ScrollArea } from "@/components/ui/scroll-area";

export default function ReportsPage() {
  return (
    <DashboardShell>
      <DashboardHeader
        heading="Session Reports"
        text="View your therapy session history and progress."
      />
      <div className="grid gap-4">
        <Card className="col-span-3">
          <CardHeader>
            <CardTitle>Session History</CardTitle>
            <CardDescription>
              Your past therapy sessions and outcomes
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-[500px] pr-4">
              <div className="space-y-4">
                {/* Session 1 */}
                <div className="border rounded-lg p-4">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <h3 className="font-medium">Session #TH-2025-04-06-001</h3>
                      <p className="text-sm text-muted-foreground">April 6, 2025 at 2:30 PM</p>
                    </div>
                    <Button variant="outline" size="sm">View Details</Button>
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="font-medium">Duration:</span>
                      <span className="text-muted-foreground">45 minutes</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="font-medium">Focus Area:</span>
                      <span className="text-muted-foreground">Anxiety Management</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="font-medium">Techniques:</span>
                      <span className="text-muted-foreground">CBT, Breathing Exercises</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="font-medium">Mood Before:</span>
                      <span className="text-muted-foreground">5/10</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="font-medium">Mood After:</span>
                      <span className="text-muted-foreground">7/10</span>
                    </div>
                  </div>
                </div>

                {/* Session 2 */}
                <div className="border rounded-lg p-4">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <h3 className="font-medium">Session #TH-2025-03-28-002</h3>
                      <p className="text-sm text-muted-foreground">March 28, 2025 at 10:15 AM</p>
                    </div>
                    <Button variant="outline" size="sm">View Details</Button>
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="font-medium">Duration:</span>
                      <span className="text-muted-foreground">30 minutes</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="font-medium">Focus Area:</span>
                      <span className="text-muted-foreground">Stress Reduction</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="font-medium">Techniques:</span>
                      <span className="text-muted-foreground">Mindfulness, Guided Imagery</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="font-medium">Mood Before:</span>
                      <span className="text-muted-foreground">4/10</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="font-medium">Mood After:</span>
                      <span className="text-muted-foreground">6/10</span>
                    </div>
                  </div>
                </div>

                {/* Session 3 */}
                <div className="border rounded-lg p-4">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <h3 className="font-medium">Session #TH-2025-03-21-003</h3>
                      <p className="text-sm text-muted-foreground">March 21, 2025 at 3:45 PM</p>
                    </div>
                    <Button variant="outline" size="sm">View Details</Button>
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="font-medium">Duration:</span>
                      <span className="text-muted-foreground">50 minutes</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="font-medium">Focus Area:</span>
                      <span className="text-muted-foreground">Depression Management</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="font-medium">Techniques:</span>
                      <span className="text-muted-foreground">Behavioral Activation, Thought Records</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="font-medium">Mood Before:</span>
                      <span className="text-muted-foreground">3/10</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="font-medium">Mood After:</span>
                      <span className="text-muted-foreground">5/10</span>
                    </div>
                  </div>
                </div>
              </div>
            </ScrollArea>
          </CardContent>
        </Card>
        
        <div className="grid gap-4 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>Session Log</CardTitle>
              <CardDescription>
                Track your therapy journey over time
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm font-medium">Total Sessions:</span>
                  <span className="text-sm text-muted-foreground">12</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm font-medium">This Month:</span>
                  <span className="text-sm text-muted-foreground">3 sessions</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm font-medium">Average Duration:</span>
                  <span className="text-sm text-muted-foreground">42 minutes</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm font-medium">Most Common Focus:</span>
                  <span className="text-sm text-muted-foreground">Anxiety Management</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm font-medium">Average Mood Improvement:</span>
                  <span className="text-sm text-muted-foreground">+2.1 points</span>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle>Progress Insights</CardTitle>
              <CardDescription>
                Key metrics from your therapy journey
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm font-medium">Consistency Score:</span>
                  <span className="text-sm text-muted-foreground">8.5/10</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm font-medium">Engagement Level:</span>
                  <span className="text-sm text-muted-foreground">High</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm font-medium">Technique Mastery:</span>
                  <span className="text-sm text-muted-foreground">7/10</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm font-medium">Goal Achievement:</span>
                  <span className="text-sm text-muted-foreground">65%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm font-medium">Overall Trend:</span>
                  <span className="text-sm text-muted-foreground">Positive</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </DashboardShell>
  );
}
