// app/components/breathing-exercise/ExerciseInterlude.tsx
"use client"

import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { BigTypography } from '@/components/BigTypography'

const beepAudio = new Audio('/audio/beep.mp3')

interface Props {
  onComplete: () => void
}

export function ExerciseInterlude({ onComplete }: Props) {
  const [countdown, setCountdown] = useState(3)

  useEffect(() => {
    if (countdown <= 0) {
      onComplete()
      return
    }

    // play beep
    beepAudio.currentTime = 0
    beepAudio.play().catch(() => {})

    const timer = setTimeout(() => setCountdown(c => c - 1), 1000)
    return () => clearTimeout(timer)
  }, [countdown, onComplete])

  return (
    <motion.div
      className="flex flex-col items-center justify-center text-center p-8"
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4 }}
    >
      <BigTypography as="h2" size="3xl" className="mb-4">
        Get Ready
      </BigTypography>
      <p className="text-lg text-muted-foreground mb-6 max-w-md">
        Find a comfortable position. Exercise begins in:
      </p>
      <motion.div
        key={countdown}
        className="w-24 h-24 rounded-full bg-primary/20 flex items-center justify-center text-5xl font-bold text-primary"
        initial={{ scale: 0.7, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 1.2, opacity: 0 }}
        transition={{ duration: 0.4 }}
      >
        {countdown > 0 ? countdown : null}
      </motion.div>
    </motion.div>
  )
}
