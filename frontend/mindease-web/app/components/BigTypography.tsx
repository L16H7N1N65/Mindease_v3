import React from "react";
import { cn } from "@/lib/utils";

type BigTypographyProps = {
  className?: string;
  children: React.ReactNode;
  as?: "h1" | "h2" | "h3" | "h4" | "div" | "p";
  size?: "xl" | "2xl" | "3xl" | "4xl" | "5xl" | "6xl" | "7xl" | "8xl";
  weight?: "normal" | "medium" | "semibold" | "bold";
  gradient?: boolean;
  animate?: boolean;
  align?: "left" | "center" | "right";
};

export const BigTypography = ({
  className,
  children,
  as: Component = "h1",
  size = "5xl",
  weight = "bold",
  gradient = false,
  animate = false,
  align = "left",
}: BigTypographyProps) => {
  return (
    <Component
      className={cn(
        "tracking-tight",
        size === "xl" && "text-xl md:text-2xl",
        size === "2xl" && "text-2xl md:text-3xl",
        size === "3xl" && "text-3xl md:text-4xl",
        size === "4xl" && "text-4xl md:text-5xl",
        size === "5xl" && "text-5xl md:text-6xl",
        size === "6xl" && "text-6xl md:text-7xl",
        size === "7xl" && "text-7xl md:text-8xl",
        size === "8xl" && "text-8xl md:text-9xl",
        weight === "normal" && "font-normal",
        weight === "medium" && "font-medium",
        weight === "semibold" && "font-semibold",
        weight === "bold" && "font-bold",
        align === "left" && "text-left",
        align === "center" && "text-center",
        align === "right" && "text-right",
        gradient && "bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent",
        animate && "animate-in fade-in slide-in-from-bottom-4 duration-1000",
        className
      )}
    >
      {children}
    </Component>
  );
};

export const GradientText = ({
  className,
  children,
}: {
  className?: string;
  children: React.ReactNode;
}) => {
  return (
    <span
      className={cn(
        "bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent",
        className
      )}
    >
      {children}
    </span>
  );
};
