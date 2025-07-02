// app/components/breathing-exercise/BreathingExercise.tsx
"use client";

import React, { useState, useEffect, useRef } from "react";
import { ExerciseInterlude } from "./ExerciseInterlude";
import { BreathingAnimation } from "./BreathingAnimation";
import { StepDescription } from "./StepDescription";
import { AnimatedDots } from "./AnimatedDots";
import { Timer } from "./Timer";
import { ExerciseComplete } from "./ExerciseComplete";

const VOICES = {
  laura: {
    inhale: new Audio("/audio/lauraInhale.mp3"),
    afterInhale: new Audio("/audio/lauraHold.mp3"),
    exhale: new Audio("/audio/lauraExhale.mp3"),
    afterExhale: new Audio("/audio/lauraHold.mp3"),
  },
  paul: {
    inhale: new Audio("/audio/paulInhale.mp3"),
    afterInhale: new Audio("/audio/paulHold.mp3"),
    exhale: new Audio("/audio/paulExhale.mp3"),
    afterExhale: new Audio("/audio/paulHold.mp3"),
  },
};
const endingBell = new Audio("/audio/endingBell.mp3");

type ExerciseStatus = "choose" | "interlude" | "running" | "completed";
type StepId = "inhale" | "afterInhale" | "exhale" | "afterExhale";

interface Step { id: StepId; label: string; duration: number; }

const PATTERN = [
  { id: "inhale", duration: 4000 },
  { id: "afterInhale", duration: 2000 },
  { id: "exhale", duration: 6000 },
  { id: "afterExhale", duration: 2000 },
] as const;

const LABELS: Record<StepId, string> = {
  inhale: "Breathe In",
  afterInhale: "Hold",
  exhale: "Breathe Out",
  afterExhale: "Hold",
};

export default function BreathingExercise() {
  const [status, setStatus] = useState<ExerciseStatus>("choose");
  const [voice, setVoice] = useState<keyof typeof VOICES>("laura");
  const [stepIndex, setStepIndex] = useState(0);
  const [animValue, setAnimValue] = useState(0);

  // useRef for requestAnimationFrame handle
  const rafRef = useRef<number>(0);

  const steps: Step[] = PATTERN.map(s => ({ id: s.id, duration: s.duration, label: LABELS[s.id] }));
  const currentStep = steps[stepIndex];
  const timeLimit = 300; // seconds

  const playVoice = (stepId: StepId) => {
    const audio = VOICES[voice][stepId];
    audio.currentTime = 0;
    audio.play().catch(() => {});
  };

  // Play voice when entering running
  useEffect(() => {
    if (status === "running") playVoice(currentStep.id);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [status]);

  // Play voice on each step change
  useEffect(() => {
    if (status === "running") playVoice(currentStep.id);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [stepIndex]);

  // Main loop: animate & step progression
  useEffect(() => {
    if (status !== "running") return;

    let startTime: number;
    let stepStart: number;

    const loop = (ts: number) => {
      if (!startTime) {
        startTime = ts;
        stepStart = ts;
      }

      const sinceStart = (ts - startTime) / 1000;
      if (sinceStart >= timeLimit) {
        setStatus("completed");
        endingBell.play().catch(() => {});
        return;
      }

      const sinceStep = ts - stepStart;
      const { duration, id } = currentStep;
      const progress = Math.min(sinceStep / duration, 1);

      if (id === "inhale") setAnimValue(progress);
      else if (id === "exhale") setAnimValue(1 - progress);

      if (progress >= 1) {
        setStepIndex(i => (i + 1) % steps.length);
        stepStart = ts;
      }

      rafRef.current = requestAnimationFrame(loop);
    };

    rafRef.current = requestAnimationFrame(loop);
    return () => cancelAnimationFrame(rafRef.current);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [status, stepIndex]);

  // UI
  if (status === "choose") {
    return (
      <div className="space-y-4 text-center p-6">
        <h2 className="text-2xl font-bold">Choose your voice</h2>
        <select
          className="border rounded p-2"
          value={voice}
          onChange={e => setVoice(e.currentTarget.value as keyof typeof VOICES)}
        >
          <option value="laura">Laura</option>
          <option value="paul">Paul</option>
        </select>
        <button
          className="mt-4 px-6 py-2 rounded-full bg-primary text-white"
          onClick={() => setStatus("interlude")}
        >
          Start Session
        </button>
      </div>
    );
  }

  return (
    <div className="relative min-h-[500px] flex flex-col items-center justify-center">
      {status === "interlude" && (
        <ExerciseInterlude onComplete={() => setStatus("running")} />
      )}

      {status === "running" && (
        <>
          <Timer
            limit={timeLimit}
            onLimitReached={() => {
              setStatus("completed");
              endingBell.play().catch(() => {});
            }}
          />

          <div className="my-8 flex flex-col items-center">
            <BreathingAnimation animationValue={animValue} />
            <StepDescription label={currentStep.label} />
            {(currentStep.id === "afterInhale" || currentStep.id === "afterExhale") && (
              <AnimatedDots numberOfDots={3} totalDuration={currentStep.duration} />
            )}
          </div>

          <button
            onClick={() => {
              setStatus("completed");
              endingBell.play().catch(() => {});
            }}
            className="mt-8 rounded-full bg-muted px-6 py-2 hover:bg-muted/80"
          >
            End Exercise
          </button>
        </>
      )}

      {status === "completed" && (
        <ExerciseComplete onRestart={() => {
          setStatus("choose");
          setStepIndex(0);
          setAnimValue(0);
        }} />
      )}
    </div>
  );
}
