import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { DashboardHeader } from "@/components/dashboard-header"
import { DashboardShell } from "@/components/dashboard-shell"

export default function FacialMoodDetectionPage() {
  return (
    <DashboardShell>
      <DashboardHeader
        heading="Facial Mood Detection"
        text="Detect your mood using facial expression analysis with privacy-first technology."
      />
      <div className="grid gap-4">
        <Card className="col-span-3">
          <CardHeader>
            <CardTitle>Facial Mood Scanner</CardTitle>
            <CardDescription>
              Your privacy is protected. Images are processed on-device and never stored.
            </CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col items-center justify-center">
            <div className="relative w-full max-w-md aspect-video bg-muted rounded-lg flex items-center justify-center mb-4">
              <div className="text-center p-4">
                <p className="text-sm text-muted-foreground mb-4">Camera feed will appear here</p>
                <Button>Enable Camera</Button>
              </div>
              <div className="absolute inset-0 border-2 border-dashed border-muted-foreground rounded-lg pointer-events-none" />
            </div>
            
            <div className="grid grid-cols-2 gap-4 w-full max-w-md">
              <Card>
                <CardHeader className="p-4">
                  <CardTitle className="text-base">Detected Mood</CardTitle>
                </CardHeader>
                <CardContent className="p-4 pt-0">
                  <div className="text-2xl font-bold">Neutral</div>
                  <div className="text-sm text-muted-foreground">Confidence: 85%</div>
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader className="p-4">
                  <CardTitle className="text-base">Secondary Mood</CardTitle>
                </CardHeader>
                <CardContent className="p-4 pt-0">
                  <div className="text-2xl font-bold">Calm</div>
                  <div className="text-sm text-muted-foreground">Confidence: 10%</div>
                </CardContent>
              </Card>
            </div>
            
            <div className="w-full max-w-md mt-4">
              <Button className="w-full">Save Mood Detection</Button>
            </div>
          </CardContent>
        </Card>
        
        <Tabs defaultValue="about" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="about">About</TabsTrigger>
            <TabsTrigger value="privacy">Privacy</TabsTrigger>
            <TabsTrigger value="history">History</TabsTrigger>
          </TabsList>
          <TabsContent value="about" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>About Facial Mood Detection</CardTitle>
                <CardDescription>
                  How our privacy-first mood detection works
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <p>MindEase uses TensorFlow Lite to detect your mood from facial expressions directly on your device. The system can identify seven basic emotions:</p>
                <ul className="list-disc pl-5 space-y-1">
                  <li>Happy</li>
                  <li>Sad</li>
                  <li>Angry</li>
                  <li>Surprised</li>
                  <li>Fearful</li>
                  <li>Disgusted</li>
                  <li>Neutral</li>
                </ul>
                <p>This feature helps you track your emotional patterns over time, providing valuable insights for your therapy journey.</p>
              </CardContent>
            </Card>
          </TabsContent>
          <TabsContent value="privacy" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Privacy Protection</CardTitle>
                <CardDescription>
                  How we protect your privacy
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <p>Your privacy is our top priority. Here's how we protect your data:</p>
                <ul className="list-disc pl-5 space-y-1">
                  <li><strong>On-device processing:</strong> All facial analysis happens directly on your device.</li>
                  <li><strong>No image storage:</strong> Raw images are never stored or transmitted.</li>
                  <li><strong>Minimal data:</strong> Only mood labels and confidence scores are saved.</li>
                  <li><strong>Optional server fallback:</strong> DeepFace server processing is optional and opt-in only.</li>
                  <li><strong>GDPR compliant:</strong> All data can be deleted at any time.</li>
                </ul>
              </CardContent>
            </Card>
          </TabsContent>
          <TabsContent value="history" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Mood Detection History</CardTitle>
                <CardDescription>
                  Your recent mood detections
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between border-b pb-2">
                    <div>
                      <div className="font-medium">Happy (92%)</div>
                      <div className="text-sm text-muted-foreground">April 5, 2025 - 2:30 PM</div>
                    </div>
                    <Button variant="ghost" size="sm">View</Button>
                  </div>
                  <div className="flex items-center justify-between border-b pb-2">
                    <div>
                      <div className="font-medium">Neutral (87%)</div>
                      <div className="text-sm text-muted-foreground">April 4, 2025 - 10:15 AM</div>
                    </div>
                    <Button variant="ghost" size="sm">View</Button>
                  </div>
                  <div className="flex items-center justify-between border-b pb-2">
                    <div>
                      <div className="font-medium">Sad (76%)</div>
                      <div className="text-sm text-muted-foreground">April 2, 2025 - 7:45 PM</div>
                    </div>
                    <Button variant="ghost" size="sm">View</Button>
                  </div>
                </div>
              </CardContent>
              <CardFooter>
                <Button variant="outline" className="w-full">View Complete History</Button>
              </CardFooter>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </DashboardShell>
  )
}
