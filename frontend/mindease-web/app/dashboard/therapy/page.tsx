import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Textarea } from "@/components/ui/textarea"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { ScrollArea } from "@/components/ui/scroll-area"
import { DashboardHeader } from "@/components/dashboard-header"
import { DashboardShell } from "@/components/dashboard-shell"
import Link from 'next/link'
export default function TherapyPage() {
  return (
    <DashboardShell>
      <DashboardHeader
        heading="Therapy Session"
        text="Chat with your AI therapist using CBT techniques."
      />
      <div className="grid gap-4">
        <Card className="col-span-3">
          <CardHeader>
            <CardTitle>Therapy Chat</CardTitle>
            <CardDescription>
              Your conversation is private and encrypted. This session uses rule-based CBT with Mistral 7B as a fallback.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-[500px] pr-4">
              <div className="space-y-4">
                <div className="flex items-start gap-4">
                  <Avatar>
                    <AvatarImage src="/avatars/therapist.png" alt="MindEase" />
                    <AvatarFallback>ME</AvatarFallback>
                  </Avatar>
                  <div className="grid gap-1">
                    <div className="font-semibold">MindEase Therapist</div>
                    <div className="rounded-lg bg-muted p-3">
                      <p>Hello! I'm your MindEase therapist. How are you feeling today?</p>
                    </div>
                    <div className="text-xs text-muted-foreground">
                      Just now
                    </div>
                  </div>
                </div>
                
                <div className="flex items-start gap-4 justify-end">
                  <div className="grid gap-1">
                    <div className="font-semibold text-right">You</div>
                    <div className="rounded-lg bg-primary p-3 text-primary-foreground">
                      <p>I've been feeling anxious about my upcoming presentation at work.</p>
                    </div>
                    <div className="text-xs text-muted-foreground text-right">
                      Just now
                    </div>
                  </div>
                  <Avatar>
                    <AvatarImage src="/avatars/user.png" alt="User" />
                    <AvatarFallback>U</AvatarFallback>
                  </Avatar>
                </div>
                
                <div className="flex items-start gap-4">
                  <Avatar>
                    <AvatarImage src="/avatars/therapist.png" alt="MindEase" />
                    <AvatarFallback>ME</AvatarFallback>
                  </Avatar>
                  <div className="grid gap-1">
                    <div className="font-semibold">MindEase Therapist</div>
                    <div className="rounded-lg bg-muted p-3">
                      <p>I understand presentations can be stressful. Let's explore what specific thoughts are contributing to your anxiety. Can you identify any particular thoughts or concerns about the presentation?</p>
                    </div>
                    <div className="text-xs text-muted-foreground">
                      Just now
                    </div>
                  </div>
                </div>
              </div>
            </ScrollArea>
          </CardContent>
          <CardFooter className="flex items-center gap-2">
            <Textarea
              placeholder="Type your message here..."
              className="min-h-[80px]"
            />
            <Button className="ml-auto">Send</Button>
          </CardFooter>
        </Card>
        
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          <Card>
            <CardHeader>
              <CardTitle>Session Information</CardTitle>
              <CardDescription>
                Details about your current therapy session
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm font-medium">Session ID:</span>
                  <span className="text-sm text-muted-foreground">TH-2025-04-06-001</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm font-medium">Duration:</span>
                  <span className="text-sm text-muted-foreground">5 minutes</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm font-medium">Mode:</span>
                  <span className="text-sm text-muted-foreground">Rule-based CBT</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm font-medium">Language:</span>
                  <span className="text-sm text-muted-foreground">English</span>
                </div>
              </div>
            </CardContent>
            <CardFooter>
              <Button variant="outline" className="w-full">End Session</Button>
            </CardFooter>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle>Therapy Tools</CardTitle>
              <CardDescription>
                Additional resources for your session
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <Button variant="outline" className="w-full justify-start">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                  Thought Record
                </Button>
                <Button variant="outline" className="w-full justify-start">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  Breathing Exercise
                </Button>
                <Button variant="outline" className="w-full justify-start">
                  <Link href="/dashboard/therapy/breathing-exercise">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </Link>
                  Cognitive Distortions
                </Button>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle>Session History</CardTitle>
              <CardDescription>
                Your recent therapy sessions
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">April 3, 2025</span>
                  <Button variant="ghost" size="sm">View</Button>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">March 28, 2025</span>
                  <Button variant="ghost" size="sm">View</Button>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">March 21, 2025</span>
                  <Button variant="ghost" size="sm">View</Button>
                </div>
              </div>
            </CardContent>
            <CardFooter>
              <Button variant="outline" className="w-full">View All Sessions</Button>
            </CardFooter>
          </Card>
        </div>
      </div>
    </DashboardShell>
  )
}
