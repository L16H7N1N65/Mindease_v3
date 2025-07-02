import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { DashboardHeader } from "@/components/dashboard-header";
import { DashboardShell } from "@/components/dashboard-shell";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";

// Mock auth; replace with your real hook/context
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

export default function ProfilePage() {
  const { user } = useAuth();
  
  return (
    <DashboardShell>
      <DashboardHeader
        heading="Profile"
        text="Manage your personal information and preferences."
      />
      <div className="grid gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Personal Information</CardTitle>
            <CardDescription>
              Update your personal details and profile picture
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col md:flex-row gap-6">
              <div className="flex flex-col items-center gap-4">
                <Avatar className="h-24 w-24">
                  <AvatarImage src={user.avatarUrl} alt={user.name} />
                  <AvatarFallback className="text-2xl">
                    {user.name.charAt(0).toUpperCase()}
                  </AvatarFallback>
                </Avatar>
                <Button variant="outline" size="sm">
                  Change Avatar
                </Button>
              </div>
              
              <div className="flex-1 space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="firstName">First Name</Label>
                    <Input id="firstName" defaultValue="Test" />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="lastName">Last Name</Label>
                    <Input id="lastName" defaultValue="User" />
                  </div>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <Input id="email" type="email" defaultValue={user.email} />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="bio">Bio</Label>
                  <Textarea
                    id="bio"
                    placeholder="Tell us a little about yourself"
                    className="min-h-[100px]"
                  />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Account Security</CardTitle>
            <CardDescription>
              Manage your password and account security settings
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="currentPassword">Current Password</Label>
                <Input id="currentPassword" type="password" />
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="newPassword">New Password</Label>
                  <Input id="newPassword" type="password" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="confirmPassword">Confirm New Password</Label>
                  <Input id="confirmPassword" type="password" />
                </div>
              </div>
              
              <Button>Update Password</Button>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Therapy Preferences</CardTitle>
            <CardDescription>
              Customize your therapy experience
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="therapyGoals">Therapy Goals</Label>
                <Textarea
                  id="therapyGoals"
                  placeholder="What would you like to achieve with therapy?"
                  className="min-h-[100px]"
                />
              </div>
              
              <div className="space-y-2">
                <Label>Primary Focus Areas</Label>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  <div className="flex items-center space-x-2">
                    <input type="checkbox" id="anxiety" className="rounded" />
                    <label htmlFor="anxiety">Anxiety</label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <input type="checkbox" id="depression" className="rounded" />
                    <label htmlFor="depression">Depression</label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <input type="checkbox" id="stress" className="rounded" />
                    <label htmlFor="stress">Stress</label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <input type="checkbox" id="relationships" className="rounded" />
                    <label htmlFor="relationships">Relationships</label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <input type="checkbox" id="selfEsteem" className="rounded" />
                    <label htmlFor="selfEsteem">Self-Esteem</label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <input type="checkbox" id="trauma" className="rounded" />
                    <label htmlFor="trauma">Trauma</label>
                  </div>
                </div>
              </div>
              
              <Button>Save Preferences</Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardShell>
  );
}
