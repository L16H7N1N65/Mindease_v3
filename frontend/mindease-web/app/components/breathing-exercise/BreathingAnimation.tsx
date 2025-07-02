"use client"

import React from 'react'
import { motion } from 'framer-motion'

interface Props {
  animationValue: number
  color?: string
}

export function BreathingAnimation({ animationValue, color = "#FF9F66" }: Props) {
  // Calculate dimensions based on viewport
  const circleWidth = Math.min(window.innerWidth, window.innerHeight) / 3
  
  // Animation values
  const innerOpacity = 1 - animationValue * 0.9
  const innerScale = 0.9 + animationValue * 0.1
  const outerScale = 1 + animationValue * 0.5
  
  return (
    <div className="relative flex items-center justify-center" style={{ minHeight: circleWidth * 2, minWidth: circleWidth * 2 }}>
      {/* Inner circle */}
      <motion.div
        className="absolute rounded-full bg-primary/20 dark:bg-primary/30"
        style={{
          width: circleWidth,
          height: circleWidth,
          opacity: innerOpacity,
          scale: innerScale,
        }}
        animate={{
          scale: innerScale,
          opacity: innerOpacity,
        }}
        transition={{
          duration: 0.2,
        }}
      />
      
      {/* Outer circles */}
      {Array.from({ length: 8 }).map((_, index) => (
        <RotatingCircle
          key={`circle-${index}`}
          color={color}
          opacity={0.2}
          animationValue={animationValue}
          index={index}
          circleWidth={circleWidth}
          outerScale={outerScale}
        />
      ))}
    </div>
  )
}

interface RotatingCircleProps {
  animationValue: number
  outerScale: number
  opacity: number
  index: number
  color: string
  circleWidth: number
}

function RotatingCircle({ animationValue, outerScale, opacity, index, color, circleWidth }: RotatingCircleProps) {
  const rotation = index * 45 + animationValue * 180
  const translate = 1 + animationValue * (circleWidth / 6)
  
  return (
    <motion.div
      className="absolute rounded-full"
      style={{
        width: circleWidth,
        height: circleWidth,
        backgroundColor: color,
        opacity,
        rotate: `${rotation}deg`,
        translateX: translate,
        translateY: translate,
        scale: outerScale,
      }}
      animate={{
        rotate: `${rotation}deg`,
        translateX: translate,
        translateY: translate,
        scale: outerScale,
      }}
      transition={{
        duration: 0.2,
      }}
    />
  )
}
