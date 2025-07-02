import React from "react";
import { BigTypography } from "@/components/BigTypography";
import { GentleMessage } from "@/components/GentleMessage";
import { BentoGrid, BentoCard } from "@/components/BentoGrid";
import { CallToAction } from "@/components/CallToAction";

export default function ResponsiveTest() {
  return (
    <div className="p-4 space-y-8">
      <div className="border border-dashed border-primary p-4 rounded-lg">
        <h2 className="text-lg font-semibold mb-2">Mobile View (Small Screens)</h2>
        <div className="w-full max-w-[375px] mx-auto border border-border rounded-lg overflow-hidden">
          <div className="p-4">
            <BigTypography size="4xl">
              Take a deep breath.
            </BigTypography>
            
            <GentleMessage className="mt-4">
              You're in a space designed just for you.
            </GentleMessage>
            
            <div className="mt-6">
              <CallToAction fullWidth={true}>
                Begin your journey
              </CallToAction>
            </div>
            
            <div className="mt-8">
              <BentoGrid className="grid-cols-1">
                <BentoCard
                  title="AI-Powered Therapy"
                  description="Personalized support through advanced AI."
                  icon={
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" />
                    </svg>
                  }
                />
              </BentoGrid>
            </div>
          </div>
        </div>
      </div>
      
      <div className="border border-dashed border-primary p-4 rounded-lg">
        <h2 className="text-lg font-semibold mb-2">Tablet View (Medium Screens)</h2>
        <div className="w-full max-w-[768px] mx-auto border border-border rounded-lg overflow-hidden">
          <div className="p-6">
            <BigTypography size="5xl" align="center">
              Take a deep breath.
            </BigTypography>
            
            <GentleMessage className="mt-4 text-center">
              You're in a space designed just for you.
            </GentleMessage>
            
            <div className="mt-6 flex justify-center">
              <CallToAction>
                Begin your journey
              </CallToAction>
            </div>
            
            <div className="mt-8">
              <BentoGrid className="grid-cols-2">
                <BentoCard
                  title="AI-Powered Therapy"
                  description="Personalized support through advanced AI."
                  icon={
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" />
                    </svg>
                  }
                />
                <BentoCard
                  title="Mood Tracking"
                  description="Monitor your emotional patterns with intuitive visualization tools."
                  icon={
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M7.5 14.25v2.25m3-4.5v4.5m3-6.75v6.75m3-9v9M6 20.25h12A2.25 2.25 0 0020.25 18V6A2.25 2.25 0 0018 3.75H6A2.25 2.25 0 003.75 6v12A2.25 2.25 0 006 20.25z" />
                    </svg>
                  }
                />
              </BentoGrid>
            </div>
          </div>
        </div>
      </div>
      
      <div className="border border-dashed border-primary p-4 rounded-lg">
        <h2 className="text-lg font-semibold mb-2">Desktop View (Large Screens)</h2>
        <div className="w-full max-w-[1200px] mx-auto border border-border rounded-lg overflow-hidden">
          <div className="p-8">
            <BigTypography size="6xl" align="center">
              Take a deep breath.
            </BigTypography>
            
            <GentleMessage className="mt-4 text-center max-w-3xl mx-auto">
              You're in a space designed just for you. Our AI supports your journey—quietly, privately, safely.
            </GentleMessage>
            
            <div className="mt-6 flex justify-center gap-4">
              <CallToAction>
                Begin your journey
              </CallToAction>
              <CallToAction variant="outline">
                Learn more
              </CallToAction>
            </div>
            
            <div className="mt-12">
              <BentoGrid className="grid-cols-3">
                <BentoCard
                  title="AI-Powered Therapy"
                  description="Personalized support through advanced AI that adapts to your unique needs and communication style."
                  icon={
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" />
                    </svg>
                  }
                  highlight={true}
                />
                <BentoCard
                  title="Mood Tracking"
                  description="Monitor your emotional patterns with intuitive visualization tools that help identify triggers and progress."
                  icon={
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M7.5 14.25v2.25m3-4.5v4.5m3-6.75v6.75m3-9v9M6 20.25h12A2.25 2.25 0 0020.25 18V6A2.25 2.25 0 0018 3.75H6A2.25 2.25 0 003.75 6v12A2.25 2.25 0 006 20.25z" />
                    </svg>
                  }
                />
                <BentoCard
                  title="Therapy Buddy System"
                  description="Connect with peers on similar journeys for mutual support and accountability."
                  icon={
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M15 19.128a9.38 9.38 0 002.625.372 9.337 9.337 0 004.121-.952 4.125 4.125 0 00-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 018.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0111.964-3.07M12 6.375a3.375 3.375 0 11-6.75 0 3.375 3.375 0 016.75 0zm8.25 2.25a2.625 2.625 0 11-5.25 0 2.625 2.625 0 015.25 0z" />
                    </svg>
                  }
                />
              </BentoGrid>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
