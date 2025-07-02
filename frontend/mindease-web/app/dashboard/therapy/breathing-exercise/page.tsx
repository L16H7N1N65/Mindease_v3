// app/dashboard/therapy/breathing-exercise/page.tsx
"use client"

import React from 'react'
import dynamic from 'next/dynamic'
import { BigTypography } from '@/components/BigTypography'

const BreathingExercise = dynamic(
  () => import('@/components/breathing-exercise/BreathingExercise'),
  {
    ssr: false,
    loading: () => <p>Loading exercise…</p>,
  }
)

export default function BreathingExercisePage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <BigTypography as="h1" size="4xl" className="mb-4">
        Breathing Exercise
      </BigTypography>
      <p className="mb-6 text-muted-foreground">
        Take a moment to relax and focus on your breathing with this guided exercise.
        Deep breathing can help reduce stress, improve focus, and promote a sense of calm.
      </p>

      <div className="bg-card rounded-lg shadow-lg p-6 md:p-8">
        <BreathingExercise />
      </div>

      <div className="mt-8 grid gap-6 md:grid-cols-2">
        <div className="bg-card rounded-lg shadow p-6">
          <h3 className="text-xl font-semibold mb-3">Benefits of Breathing Exercises</h3>
          <ul className="space-y-2">
            <li className="flex items-start">
              <span className="text-primary mr-2">•</span>
              <span>Reduces stress and anxiety</span>
            </li>
            <li className="flex items-start">
              <span className="text-primary mr-2">•</span>
              <span>Lowers blood pressure and heart rate</span>
            </li>
            <li className="flex items-start">
              <span className="text-primary mr-2">•</span>
              <span>Improves focus and concentration</span>
            </li>
            <li className="flex items-start">
              <span className="text-primary mr-2">•</span>
              <span>Promotes better sleep quality</span>
            </li>
          </ul>
        </div>

        <div className="bg-card rounded-lg shadow p-6">
          <h3 className="text-xl font-semibold mb-3">How to Practice</h3>
          <p className="mb-4">
            For best results, practice this breathing exercise daily. Find a quiet place
            where you won't be disturbed, and sit in a comfortable position.
          </p>
          <p>
            Start with 5 minutes and gradually increase to 10–15 minutes per session.
            You can use this exercise whenever you feel stressed or anxious.
          </p>
        </div>
      </div>
    </div>
  )
}
