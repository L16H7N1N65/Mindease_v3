"use client";

import React, { useState, useEffect } from "react";

import { BigTypography, GradientText } from "@/components/BigTypography";
import { GentleMessage } from "@/components/GentleMessage";
import { BentoGrid, BentoCard } from "@/components/BentoGrid";
import { CallToAction } from "@/components/CallToAction";
import { LandingNavbar } from "@/components/ui/LandingNavbar";
import { Card } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";

import { Vortex } from "@/components/ui/vortex";

export default function LandingPage() {
  const [dark, setDark] = useState(false);
  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
  }, [dark]);

  return (
    <div className="min-h-screen flex flex-col transition-colors bg-white dark:bg-black text-black dark:text-white">
      <LandingNavbar dark={dark} onToggleDark={() => setDark((d) => !d)} />

      <main className="flex-1">
        {/* Hero Section */}
        <section
          className="flex flex-col justify-start items-center text-center w-full pt-16
             bg-[var(--hero-bg)] bg-cover bg-center min-h-[calc(100vh-64px)]"
          // style={{
          //   minHeight: "calc(100vh - 64px)",
          //   backgroundImage: `url(${dark ? "/dark.jpg" : "/light.jpg"})`,
          //   backgroundSize: "cover",
          //   backgroundPosition: "center",
          // }}
        >
          <BigTypography 
            as="h1" 
            size="8xl" 
            align="center" 
            animate={true}
            className="t-12 mb-4 px-4 sm:px-6 lg:px-0"
          >
            Take a <GradientText>deep breath.</GradientText>
          </BigTypography>
          
          <GentleMessage 
            animate={true} 
            delay={300}
            className="max-w-3xl mx-auto mb-8"
          >
            AI‑powered support, privately yours—whenever you need it.
          </GentleMessage>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center mt-10">
            <CallToAction href="/auth/register" size="lg" className="px-6 py-4">
              Begin your journey
            </CallToAction>
            <CallToAction href="#how-it-works" size="lg" variant="outline" className="px-6 py-4">
              Learn More
            </CallToAction>
          </div>
        </section>

        {/* Features Section */}
        <section id="features" className="py-20 px-4 md:px-6 lg:px-8 max-w-7xl mx-auto">
          <BigTypography 
            as="h2" 
            size="4xl" 
            align="center"
            className="mb-16"
          >
            Explore your <GradientText>inner space</GradientText>
          </BigTypography>
          
          <BentoGrid className="mb-16">
            {/** apply black border to all cards and zoom on hover **/}
            {[
              {
                title: "AI-Powered Therapy",
                desc: "Personalized support through advanced AI that adapts to your unique needs and communication style.",
                icon: (
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" />
                  </svg>
                ),
              },
              {
                title: "Mood Tracking",
                desc: "Monitor your emotional patterns with intuitive visualization tools that help identify triggers and progress.",
                icon: (
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M7.5 14.25v2.25m3-4.5v4.5m3-6.75v6.75m3-9v9" />
                    <rect x="6" y="3.75" width="12" height="18.75" rx="2.25" />
                  </svg>
                ),
              },
              {
                title: "Therapy Buddy System",
                desc: "Connect with peers on similar journeys for mutual support and accountability.",
                icon: (
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M15 19.128a9.38 9.38 0 002.625.372 9.337 9.337 0 004.121-.952 4.125 4.125 0 00-7.533-2.493" />
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.375a3.375 3.375 0 11-6.75 0 3.375 3.375 0 016.75 0z" />
                  </svg>
                ),
              },
              {
                title: "Personalized Insights",
                desc: "Receive tailored recommendations and insights based on your unique patterns and progress.",
                icon: (
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 18L9 11.25l4.306 4.307a11.95 11.95 0 015.814-5.519" />
                  </svg>
                ),
                colSpan: 2,
              },
              {
                title: "Private & Secure",
                desc: "Your data is encrypted and protected, ensuring your mental health journey remains confidential.",
                icon: (
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75" />
                    <rect x="3.75" y="9.75" width="16.5" height="10.5" rx="2.25" />
                  </svg>
                ),
              },
            ].map((card, idx) => (
              <BentoCard
                key={idx}
                title={card.title}
                description={card.desc}
                icon={card.icon}
                colSpan={card.colSpan}
                className="border border-black transform hover:scale-105 transition-transform duration-300"
                highlight={idx === 0}
              />
            ))}
          </BentoGrid>
        </section>

        {/* How It Works Section */}
        <section id="how-it-works" className="py-20 px-4 md:px-6 lg:px-8 max-w-7xl mx-auto bg-muted/30 rounded-3xl">
          <BigTypography 
            as="h2" 
            size="4xl" 
            align="center"
            className="mb-16"
          >
            How <GradientText>MindEase</GradientText> works
          </BigTypography>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-12 max-w-5xl mx-auto">
            <div className="flex flex-col items-center text-center">
              <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mb-6">
                <span className="text-2xl font-bold text-primary">1</span>
              </div>
              <h3 className="text-xl font-semibold mb-3">Start your check-in</h3>
              <p className="text-muted-foreground">Begin with a simple check-in about how you're feeling today.</p>
            </div>
            
            <div className="flex flex-col items-center text-center">
              <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mb-6">
                <span className="text-2xl font-bold text-primary">2</span>
              </div>
              <h3 className="text-xl font-semibold mb-3">Connect with AI</h3>
              <p className="text-muted-foreground">Our AI adapts to your needs, providing personalized support and insights.</p>
            </div>
            
            <div className="flex flex-col items-center text-center">
              <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mb-6">
                <span className="text-2xl font-bold text-primary">3</span>
              </div>
              <h3 className="text-xl font-semibold mb-3">Track your progress</h3>
              <p className="text-muted-foreground">Watch your mental wellness improve over time with visual tracking tools.</p>
            </div>
          </div>
          
          <div className="mt-16 text-center">
            <CallToAction href="/auth/register">
              Start your check-in
            </CallToAction>
          </div>
        </section>

        {/* Testimonials Section */}
        <section id="testimonials" className="py-20 px-4 md:px-6 lg:px-8 max-w-7xl mx-auto">
          <BigTypography 
            as="h2" 
            size="4xl" 
            align="center"
            className="mb-16"
          >
            Stories from our <GradientText>community</GradientText>
          </BigTypography>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <div className="bg-card p-6 rounded-xl border border-border">
              <div className="flex items-center mb-4">
                <div className="w-12 h-12 rounded-full bg-primary/20 flex items-center justify-center mr-4">
                  <span className="font-semibold">JD</span>
                </div>
                <div>
                  <h4 className="font-semibold">Jamie D.</h4>
                  <p className="text-sm text-muted-foreground">Marketing Director</p>
                </div>
              </div>
              <p className="text-muted-foreground">"MindEase helped me manage work stress in ways traditional therapy couldn't. The AI always responds when I need it most."</p>
            </div>
            
            <div className="bg-card p-6 rounded-xl border border-border">
              <div className="flex items-center mb-4">
                <div className="w-12 h-12 rounded-full bg-primary/20 flex items-center justify-center mr-4">
                  <span className="font-semibold">SL</span>
                </div>
                <div>
                  <h4 className="font-semibold">Sarah L.</h4>
                  <p className="text-sm text-muted-foreground">Software Engineer</p>
                </div>
              </div>
              <p className="text-muted-foreground">"The mood tracking feature helped me identify patterns I never noticed before. I'm more self-aware and better equipped to handle challenges."</p>
            </div>
            
            <div className="bg-card p-6 rounded-xl border border-border">
              <div className="flex items-center mb-4">
                <div className="w-12 h-12 rounded-full bg-primary/20 flex items-center justify-center mr-4">
                  <span className="font-semibold">MT</span>
                </div>
                <div>
                  <h4 className="font-semibold">Michael T.</h4>
                  <p className="text-sm text-muted-foreground">Healthcare Professional</p>
                </div>
              </div>
              <p className="text-muted-foreground">"As someone who helps others all day, I needed support too. MindEase gives me a private space to process my own emotions."</p>
            </div>
          </div>
        </section>

        {/* CTA Section with Vortex */}
        <section className="py-20 px-4 md:px-6 lg:px-8 max-w-5xl mx-auto">
          <div className="rounded-3xl overflow-hidden shadow-lg">
            <Vortex
              particleCount={300}
              rangeY={800}
              baseHue={300}
              containerClassName="w-full h-[360px] relative"
              className="absolute inset-0 flex flex-col items-center justify-center text-white text-center px-4"
              backgroundColor="#000000"
            >
              <h2 className="text-3xl sm:text-4xl font-bold mb-4 mt-12 text-white">
                Ready to explore your inner space?
              </h2>
              <p className="text-white max-w-2xl mb-6 text-base sm:text-lg">
                Join thousands who have transformed their mental wellness journey with MindEase.
              </p>
              <CallToAction
                href="/auth/register"
                size="lg"
                className="px-8 py-4 bg-white text-black hover:bg-gray-200"
              >
                Begin your journey
              </CallToAction>
            </Vortex>
          </div>
        </section>


        {/* Pricing Section */}
        <section
          id="pricing"
          className="py-20 px-4 md:px-6 lg:px-8 max-w-7xl mx-auto"
        >
          <BigTypography as="h2" size="4xl" align="center" className="mb-16">
            Choose Your <GradientText>Plan</GradientText>
          </BigTypography>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Free */}
            <Card className="flex flex-col p-6 shadow-md">
              <h3 className="text-xl font-bold">Free</h3>
              <p className="text-3xl font-bold mt-2">€0</p>
              <p className="text-sm text-muted-foreground">Forever</p>
              <Separator className="my-4" />
              <ul className="space-y-2 flex-1">
                <li className="text-sm">Basic mood tracking</li>
                <li className="text-sm">5 AI therapy sessions/month</li>
                <li className="text-sm">Community forum access</li>
              </ul>
              <CallToAction href="/auth/register" className="mt-6 w-full">
                Get Started
              </CallToAction>
            </Card>

            {/* Premium */}
            <Card className="flex flex-col p-6 shadow-md border-2 border-primary">
              <div>
                <h3 className="text-xl font-bold">Premium</h3>
                <p className="text-3xl font-bold mt-2">€9.90</p>
                <p className="text-sm text-muted-foreground">per month</p>
              </div>
              <Separator className="my-4" />
              <ul className="space-y-2 flex-1">
                <li className="text-sm">Advanced mood analytics</li>
                <li className="text-sm">Unlimited AI therapy sessions</li>
                <li className="text-sm">Buddy system matching</li>
                <li className="text-sm">Personalized wellness plan</li>
              </ul>
              <CallToAction href="/auth/register" className="mt-6 w-full">
                Subscribe Now
              </CallToAction>
            </Card>

            {/* Enterprise */}
            <Card className="flex flex-col p-6 shadow-md">
              <h3 className="text-xl font-bold">Enterprise</h3>
              <p className="text-3xl font-bold mt-2">Custom</p>
              <p className="text-sm text-muted-foreground">Contact us for pricing</p>
              <Separator className="my-4" />
              <ul className="space-y-2 flex-1">
                <li className="text-sm">All Premium features</li>
                <li className="text-sm">Team wellness analytics</li>
                <li className="text-sm">Company-wide referral system</li>
                <li className="text-sm">Dedicated support</li>
                <li className="text-sm">Custom integration options</li>
              </ul>
              <CallToAction href="/contact" className="mt-6 w-full">
                Contact Sales
              </CallToAction>
            </Card>
          </div>
        </section>

      </main>

      <footer className="bg-muted/30 py-12 px-4 md:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <div className="flex items-center gap-2 mb-4">
              <svg viewBox="0 0 24 24" fill="none" className="h-6 w-6 text-primary">
                <path
                  d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
                <path
                  d="M9 15h6M9 9h6"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
              <span className="font-bold">MindEase</span>
            </div>
            <p className="text-sm text-muted-foreground">Supporting your mental wellness journey with AI-powered therapy and tools.</p>
          </div>
          
          <div>
            <h4 className="font-semibold mb-4">Features</h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li>AI Therapy</li>
              <li>Mood Tracking</li>
              <li>Buddy System</li>
              <li>Personalized Insights</li>
            </ul>
          </div>
          
          <div>
            <h4 className="font-semibold mb-4">Company</h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li>About Us</li>
              <li>Careers</li>
              <li>Blog</li>
              <li>Contact</li>
            </ul>
          </div>
          
          <div>
            <h4 className="font-semibold mb-4">Legal</h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li>Privacy Policy</li>
              <li>Terms of Service</li>
              <li>Cookie Policy</li>
            </ul>
          </div>
        </div>
        
        <div className="max-w-7xl mx-auto mt-12 pt-6 border-t border-border text-center text-sm text-muted-foreground">
          <p>© {new Date().getFullYear()} MindEase. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}
