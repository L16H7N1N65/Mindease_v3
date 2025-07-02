"use client"

import React, { useEffect, useState } from 'react'
import { motion } from 'framer-motion'

interface Props {
  limit: number
  onLimitReached: () => void
}

export function Timer({ limit, onLimitReached }: Props) {
  const [timeElapsed, setTimeElapsed] = useState(0)
  const [isActive, setIsActive] = useState(true)
  
  useEffect(() => {
    if (!isActive) return
    
    const interval = setInterval(() => {
      setTimeElapsed(prev => {
        const newTime = prev + 1
        if (newTime >= limit) {
          clearInterval(interval)
          setIsActive(false)
          onLimitReached()
          return limit
        }
        return newTime
      })
    }, 1000)
    
    return () => clearInterval(interval)
  }, [isActive, limit, onLimitReached])
  
  // Format time as MM:SS
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }
  
  // Calculate progress percentage
  const progress = (timeElapsed / limit) * 100
  
  return (
    <div className="w-full max-w-xs mx-auto mb-6">
      <div className="flex justify-between text-sm text-muted-foreground mb-2">
        <span>Time Elapsed</span>
        <span>{formatTime(timeElapsed)} / {formatTime(limit)}</span>
      </div>
      
      <div className="h-2 bg-muted rounded-full overflow-hidden">
        <motion.div 
          className="h-full bg-primary"
          initial={{ width: '0%' }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.5 }}
        />
      </div>
    </div>
  )
}
