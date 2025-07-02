import React from "react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

type CallToActionProps = {
  className?: string;
  children: React.ReactNode;
  onClick?: () => void;
  href?: string;
  size?: "default" | "sm" | "lg";
  variant?: "default" | "outline" | "ghost" | "link" | "secondary" | "destructive";
  animate?: boolean;
  icon?: React.ReactNode;
  fullWidth?: boolean;
};

export const CallToAction = ({
  className,
  children,
  onClick,
  href,
  size = "lg",
  variant = "default",
  animate = true,
  icon,
  fullWidth = false,
}: CallToActionProps) => {
  return (
    <Button
      className={cn(
        "rounded-full font-medium",
        size === "lg" && "text-lg px-8 py-6 h-auto",
        animate && "animate-in fade-in slide-in-from-bottom-4 duration-1000 delay-500",
        fullWidth && "w-full",
        icon && "inline-flex items-center gap-2",
        className
      )}
      size={size !== "lg" ? size : "default"}
      variant={variant}
      onClick={onClick}
      asChild={!!href}
    >
      {href ? (
        <a href={href}>
          {children}
          {icon && <span className="ml-2">{icon}</span>}
        </a>
      ) : (
        <>
          {children}
          {icon && <span className="ml-2">{icon}</span>}
        </>
      )}
    </Button>
  );
};
