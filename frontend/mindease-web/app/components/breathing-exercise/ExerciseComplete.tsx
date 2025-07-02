"use client"

import React from 'react'
import { motion } from 'framer-motion'
import { BigTypography } from '@/components/BigTypography'

interface Props {
  onRestart: () => void
}

export function ExerciseComplete({ onRestart }: Props) {
  return (
    <motion.div 
      className="flex flex-col items-center justify-center text-center p-8"
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
    >
      <div className="w-24 h-24 rounded-full bg-primary/20 flex items-center justify-center mb-6">
        <svg 
          xmlns="http://www.w3.org/2000/svg" 
          className="h-12 w-12 text-primary" 
          fill="none" 
          viewBox="0 0 24 24" 
          stroke="currentColor"
        >
          <path 
            strokeLinecap="round" 
            strokeLinejoin="round" 
            strokeWidth={2} 
            d="M5 13l4 4L19 7" 
          />
        </svg>
      </div>
      
      <BigTypography as="h2" size="3xl" className="mb-4">
        Great Job!
      </BigTypography>
      
      <p className="text-lg text-muted-foreground mb-8 max-w-md">
        You've completed your breathing exercise. Taking time for mindful breathing 
        helps reduce stress and improve your overall wellbeing.
      </p>
      
      <div className="flex flex-col sm:flex-row gap-4">
        <button
          onClick={onRestart}
          className="px-6 py-3 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition-colors"
        >
          Start Again
        </button>
        
        <button
          onClick={() => window.history.back()}
          className="px-6 py-3 rounded-lg bg-muted hover:bg-muted/80 transition-colors"
        >
          Return to Dashboard
        </button>
      </div>
    </motion.div>
  )
}