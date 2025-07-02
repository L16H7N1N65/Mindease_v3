"use client"

import React from 'react'
import { motion } from 'framer-motion'

interface Props {
  label: string
}

export function StepDescription({ label }: Props) {
  return (
    <motion.div
      className="mt-6 text-center"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      transition={{ duration: 0.5 }}
    >
      <h3 className="text-2xl font-medium text-primary dark:text-primary-foreground">
        {label}
      </h3>
    </motion.div>
  )
}
