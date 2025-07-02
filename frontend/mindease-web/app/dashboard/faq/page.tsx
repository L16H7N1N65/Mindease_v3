import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { DashboardHeader } from "@/components/dashboard-header";
import { DashboardShell } from "@/components/dashboard-shell";

export default function FAQPage() {
  return (
    <DashboardShell>
      <DashboardHeader
        heading="Frequently Asked Questions"
        text="Find answers to common questions about Mindease."
      />
      <div className="grid gap-6">
        <Card>
          <CardHeader>
            <CardTitle>General Questions</CardTitle>
            <CardDescription>
              Basic information about Mindease and our services
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Accordion type="single" collapsible className="w-full">
              <AccordionItem value="item-1">
                <AccordionTrigger>What is Mindease?</AccordionTrigger>
                <AccordionContent>
                  Mindease is an AI-powered therapy platform that provides personalized mental health support through cognitive behavioral therapy (CBT) techniques, mindfulness exercises, and mood tracking tools. Our goal is to make mental healthcare accessible, affordable, and effective for everyone.
                </AccordionContent>
              </AccordionItem>
              
              <AccordionItem value="item-2">
                <AccordionTrigger>How does AI therapy work?</AccordionTrigger>
                <AccordionContent>
                  Our AI therapy system uses natural language processing and machine learning algorithms trained on evidence-based therapeutic approaches. It analyzes your responses, identifies patterns in your thinking, and provides personalized guidance based on cognitive behavioral therapy principles. The AI adapts to your specific needs and progress over time.
                </AccordionContent>
              </AccordionItem>
              
              <AccordionItem value="item-3">
                <AccordionTrigger>Is Mindease a replacement for traditional therapy?</AccordionTrigger>
                <AccordionContent>
                  Mindease is designed to complement traditional therapy, not replace it. While our AI can provide valuable support and techniques based on evidence-based approaches, it's not a substitute for a licensed mental health professional, especially for severe mental health conditions. We recommend using Mindease alongside traditional therapy when possible.
                </AccordionContent>
              </AccordionItem>
            </Accordion>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Privacy & Security</CardTitle>
            <CardDescription>
              Information about how we protect your data
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Accordion type="single" collapsible className="w-full">
              <AccordionItem value="item-1">
                <AccordionTrigger>Is my data confidential?</AccordionTrigger>
                <AccordionContent>
                  Yes, we take your privacy very seriously. All conversations with our AI therapist are encrypted and confidential. We do not share your personal information with third parties without your explicit consent. You can review our complete privacy policy for more details on how we handle your data.
                </AccordionContent>
              </AccordionItem>
              
              <AccordionItem value="item-2">
                <AccordionTrigger>How is my data stored and protected?</AccordionTrigger>
                <AccordionContent>
                  Your data is stored using industry-standard encryption and security measures. We use secure cloud infrastructure with regular security audits and compliance checks. You can delete your data at any time through your account settings, and we provide options to download your personal information.
                </AccordionContent>
              </AccordionItem>
              
              <AccordionItem value="item-3">
                <AccordionTrigger>Do you share my therapy content with AI training systems?</AccordionTrigger>
                <AccordionContent>
                  No, we do not use your therapy conversations to train general AI systems. Any data used to improve our specific therapeutic algorithms is anonymized, aggregated, and stripped of personal identifiers. You can opt out of this anonymized improvement program in your privacy settings.
                </AccordionContent>
              </AccordionItem>
            </Accordion>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Using Mindease</CardTitle>
            <CardDescription>
              Help with using the platform and its features
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Accordion type="single" collapsible className="w-full">
              <AccordionItem value="item-1">
                <AccordionTrigger>How often should I use Mindease?</AccordionTrigger>
                <AccordionContent>
                  For best results, we recommend using Mindease consistently, ideally 3-5 times per week. Regular engagement helps the AI better understand your patterns and provide more personalized support. Even short 5-10 minute sessions can be beneficial, especially when using the breathing exercises and mindfulness tools.
                </AccordionContent>
              </AccordionItem>
              
              <AccordionItem value="item-2">
                <AccordionTrigger>Can I access my previous therapy sessions?</AccordionTrigger>
                <AccordionContent>
                  Yes, you can access all your previous therapy sessions in the Reports section. This allows you to review your progress, revisit insights, and track changes in your mood and thought patterns over time. Session history is an important tool for reinforcing the skills you're developing.
                </AccordionContent>
              </AccordionItem>
              
              <AccordionItem value="item-3">
                <AccordionTrigger>What should I do in a mental health emergency?</AccordionTrigger>
                <AccordionContent>
                  Mindease is not designed for crisis intervention. If you're experiencing a mental health emergency or having thoughts of harming yourself or others, please contact emergency services immediately by calling 911 (US) or your local emergency number. Alternatively, you can text HOME to 741741 to reach the Crisis Text Line, or call the National Suicide Prevention Lifeline at 1-800-273-8255.
                </AccordionContent>
              </AccordionItem>
            </Accordion>
          </CardContent>
        </Card>
      </div>
    </DashboardShell>
  );
}
