"use client"

import React from 'react'
import { motion } from 'framer-motion'

interface Props {
  numberOfDots: number
  totalDuration: number
}

export function AnimatedDots({ numberOfDots, totalDuration }: Props) {
  return (
    <div className="flex items-center justify-center mt-4 space-x-2">
      {Array.from({ length: numberOfDots }).map((_, index) => (
        <motion.div
          key={`dot-${index}`}
          className="w-2 h-2 rounded-full bg-primary/60"
          animate={{
            scale: [1, 1.5, 1],
            opacity: [0.5, 1, 0.5]
          }}
          transition={{
            duration: totalDuration / 1000 / numberOfDots,
            repeat: Infinity,
            delay: (index * totalDuration) / 1000 / numberOfDots / 2,
            ease: "easeInOut"
          }}
        />
      ))}
    </div>
  )
}
