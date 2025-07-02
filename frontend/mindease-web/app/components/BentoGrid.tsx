import React from "react";
import { cn } from "@/lib/utils";

type BentoGridProps = {
  className?: string;
  children: React.ReactNode;
};

export const BentoGrid = ({
  className,
  children,
}: BentoGridProps) => {
  return (
    <div className={cn("grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 auto-rows-max", className)}>
      {children}
    </div>
  );
};

type BentoCardProps = {
  className?: string;
  title?: string;
  description?: string;
  icon?: React.ReactNode;
  header?: React.ReactNode;
  children?: React.ReactNode;
  colSpan?: number;
  rowSpan?: number;
  highlight?: boolean;
};

export const BentoCard = ({
  className,
  title,
  description,
  icon,
  header,
  children,
  colSpan = 1,
  rowSpan = 1,
  highlight = false,
}: BentoCardProps) => {
  return (
    <div 
      className={cn(
        "row-span-1 rounded-xl p-4 md:p-6 flex flex-col justify-between bg-card border border-border shadow-sm transition-all duration-300 hover:shadow-md",
        highlight && "ring-2 ring-primary",
        colSpan === 2 && "md:col-span-2",
        colSpan === 3 && "md:col-span-3 lg:col-span-3",
        rowSpan === 2 && "row-span-2",
        className
      )}
    >
      {header || (
        <div className="flex items-start justify-between gap-4">
          {icon && <div className="flex-shrink-0 text-primary">{icon}</div>}
          <div className="flex-grow">
            {title && <h3 className="text-lg md:text-xl font-semibold tracking-tight mb-2">{title}</h3>}
            {description && <p className="text-sm text-muted-foreground">{description}</p>}
          </div>
        </div>
      )}
      {children && <div className={cn("mt-4", !header && !title && !description && "mt-0")}>{children}</div>}
    </div>
  );
};
