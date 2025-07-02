import React from "react";
import { cn } from "@/lib/utils";

type GentleMessageProps = {
  className?: string;
  children: React.ReactNode;
  animate?: boolean;
  delay?: number;
  subtle?: boolean;
};

export const GentleMessage = ({
  className,
  children,
  animate = true,
  delay = 0,
  subtle = false,
}: GentleMessageProps) => {
  return (
    <p
      className={cn(
        "text-lg md:text-xl leading-relaxed",
        subtle && "text-muted-foreground",
        animate && "animate-in fade-in slide-in-from-bottom-4 duration-1000",
        className
      )}
      style={{ animationDelay: delay ? `${delay}ms` : undefined }}
    >
      {children}
    </p>
  );
};
