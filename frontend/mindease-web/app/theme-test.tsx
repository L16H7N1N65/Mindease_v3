import React from "react";
import { BigTypography, GradientText } from "@/components/BigTypography";
import { GentleMessage } from "@/components/GentleMessage";
import { BentoGrid, BentoCard } from "@/components/BentoGrid";
import { CallToAction } from "@/components/CallToAction";

export default function ThemeTest() {
  return (
    <div className="p-4 space-y-8">
      <div className="border border-dashed border-primary p-4 rounded-lg">
        <h2 className="text-lg font-semibold mb-2">Light Theme</h2>
        <div className="w-full max-w-[768px] mx-auto border border-border rounded-lg overflow-hidden bg-background p-6">
          <BigTypography size="4xl">
            Take a <GradientText>deep breath.</GradientText>
          </BigTypography>
          
          <GentleMessage className="mt-4">
            You're in a space designed just for you.
          </GentleMessage>
          
          <div className="mt-6">
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
                highlight={true}
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
      
      <div className="border border-dashed border-primary p-4 rounded-lg">
        <h2 className="text-lg font-semibold mb-2">Dark Theme</h2>
        <div className="w-full max-w-[768px] mx-auto border border-border rounded-lg overflow-hidden bg-[#121212] p-6 dark">
          <BigTypography size="4xl">
            Take a <GradientText>deep breath.</GradientText>
          </BigTypography>
          
          <GentleMessage className="mt-4">
            You're in a space designed just for you.
          </GentleMessage>
          
          <div className="mt-6">
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
                highlight={true}
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
  );
}
