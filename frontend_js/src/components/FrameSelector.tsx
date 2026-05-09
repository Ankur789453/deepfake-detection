import { Slider } from "@/components/ui/slider";
import { Film } from "lucide-react";

interface FrameSelectorProps {
  value: number;
  onChange: (value: number) => void;
  min?: number;
  max?: number;
}

export const FrameSelector = ({ value, onChange, min = 10, max = 60 }: FrameSelectorProps) => {
  const handleChange = (values: number[]) => {
    onChange(values[0]);
  };

  return (
    <div className="space-y-4 rounded-xl glass-effect p-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="rounded-lg bg-primary/10 p-2">
            <Film className="h-5 w-5 text-primary" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-foreground">Frame Analysis</h3>
            <p className="text-xs text-muted-foreground">Number of frames to analyze</p>
          </div>
        </div>
        <div className="rounded-lg bg-primary/20 px-4 py-2">
          <span className="text-2xl font-bold text-primary">{value}</span>
          <span className="ml-1 text-sm text-primary/70">frames</span>
        </div>
      </div>
      
      <div className="space-y-2">
        <Slider
          value={[value]}
          onValueChange={handleChange}
          min={min}
          max={max}
          step={1}
          className="cursor-pointer"
        />
        <div className="flex justify-between text-xs text-muted-foreground">
          <span>Faster ({min})</span>
          <span>More Accurate ({max})</span>
        </div>
      </div>

      <div className="rounded-lg bg-muted/50 p-3 text-xs text-muted-foreground">
        <p>
          <strong className="text-foreground">Tip:</strong> More frames = higher accuracy but slower processing. 
          Recommended: 30 frames for balanced performance.
        </p>
      </div>
    </div>
  );
};
