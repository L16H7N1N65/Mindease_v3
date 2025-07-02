"use client"

import React from 'react'
import { useRouter } from 'next/navigation'
import { cn } from "@/lib/utils"

interface DashboardShellProps {
  children: React.ReactNode
  className?: string
}

export function UserDashboardShell({
  children,
  className,
}: DashboardShellProps) {
  return (
    <div className={cn("grid items-start gap-8", className)}>
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">
            Welcome back to your wellness journey
          </p>
        </div>
      </div>
      {children}
    </div>
  )
}

export function AdminDashboardShell({
  children,
  className,
}: DashboardShellProps) {
  return (
    <div className={cn("grid items-start gap-8", className)}>
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Admin Dashboard</h1>
          <p className="text-muted-foreground">
            Manage users, content, and system settings
          </p>
        </div>
      </div>
      {children}
    </div>
  )
}

export function DashboardGuard({
  children,
  userRole,
  requiredRole,
  fallback,
}: {
  children: React.ReactNode
  userRole: string
  requiredRole: string
  fallback?: React.ReactNode
}) {
  const router = useRouter()
  
  // Check if user has the required role
  const hasAccess = userRole === requiredRole || 
                    (userRole === 'admin' && requiredRole === 'user')
  
  // If no access and no fallback, redirect to dashboard
  if (!hasAccess && !fallback) {
    router.push('/dashboard')
    return null
  }
  
  // Return children if has access, otherwise fallback
  return hasAccess ? <>{children}</> : <>{fallback}</>
}
