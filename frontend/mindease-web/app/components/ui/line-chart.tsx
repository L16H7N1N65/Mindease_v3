// app/components/ui/line-chart.tsx
import React from 'react';

interface LineChartDataPoint {
  x: string | number;
  y: number;
}

interface LineChartProps {
  data: LineChartDataPoint[];
}

export const LineChart: React.FC<LineChartProps> = ({ data }) => {
  // Calculate the maximum Y value for scaling
  const maxY = Math.max(...data.map(point => point.y)) || 1;

  // Generate points for the polyline based on data.
  // The chart is normalized to a 100x100 viewBox.
  const points = data.map((point, index) => {
    const x = (index / (data.length - 1)) * 100;
    const y = 100 - (point.y / maxY) * 100;
    return `${x},${y}`;
  }).join(' ');

  return (
    <div className="p-4 bg-white shadow rounded">
      <svg viewBox="0 0 100 100" className="w-full h-64">
        {/* Render a simple polyline */}
        <polyline 
          fill="none" 
          stroke="#6366F1" 
          strokeWidth="2" 
          points={points}
        />
      </svg>
    </div>
  );
};
