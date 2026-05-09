import { CheckCircle2, AlertTriangle, Shield, TrendingUp } from "lucide-react";
import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";

interface ResultsDisplayProps {
  isDeepfake: boolean;
  confidence: number;
  details?: {
    fake_probability?: number;
    real_probability?: number;
    frames_analyzed?: number;
    frames_detected_fake?: number;
    frames_detected_real?: number;
  };
}

export const ResultsDisplay = ({ isDeepfake, confidence, details }: ResultsDisplayProps) => {
  const confidencePercentage = Math.round(confidence * 100);

  return (
    <div className="space-y-6 rounded-xl glass-effect p-8 animate-in fade-in-0 slide-in-from-bottom-4 duration-500">
      {/* Main Result */}
      <div className="text-center">
        <div className={cn(
          "mx-auto mb-4 flex h-20 w-20 items-center justify-center rounded-full",
          isDeepfake ? "bg-destructive/20 animate-glow" : "bg-success/20"
        )}>
          {isDeepfake ? (
            <AlertTriangle className="h-10 w-10 text-destructive" />
          ) : (
            <CheckCircle2 className="h-10 w-10 text-success" />
          )}
        </div>
        
        <h2 className="mb-2 text-3xl font-bold">
          {isDeepfake ? (
            <span className="text-destructive">Deepfake Detected</span>
          ) : (
            <span className="text-success">Authentic Media</span>
          )}
        </h2>
        
        <p className="text-muted-foreground">
          {isDeepfake 
            ? "This media appears to be AI-generated or manipulated"
            : "This media appears to be genuine and unaltered"
          }
        </p>
      </div>

      {/* Confidence Score */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-primary" />
            <span className="font-semibold">Confidence Score</span>
          </div>
          <span className="text-2xl font-bold text-primary">{confidencePercentage}%</span>
        </div>
        
        <Progress 
          value={confidencePercentage} 
          className="h-3"
        />
        
        <p className="text-xs text-muted-foreground">
          {confidencePercentage >= 90 ? "Very High" : 
           confidencePercentage >= 75 ? "High" :
           confidencePercentage >= 60 ? "Moderate" : "Low"} confidence in the analysis
        </p>
      </div>

      {/* Detailed Probabilities */}
      {details && (
        <div className="grid gap-4 rounded-lg bg-muted/30 p-4">
          <h3 className="flex items-center gap-2 text-sm font-semibold">
            <Shield className="h-4 w-4 text-primary" />
            Detailed Analysis
          </h3>
          
          <div className="grid gap-3 text-sm">
            {details.real_probability !== undefined && (
              <div className="flex justify-between">
                <span className="text-muted-foreground">Real Probability:</span>
                <span className="font-medium text-success">
                  {Math.round(details.real_probability * 100)}%
                </span>
              </div>
            )}
            
            {details.fake_probability !== undefined && (
              <div className="flex justify-between">
                <span className="text-muted-foreground">Fake Probability:</span>
                <span className="font-medium text-destructive">
                  {Math.round(details.fake_probability * 100)}%
                </span>
              </div>
            )}
            
            {details.frames_analyzed !== undefined && (
              <>
                <div className="my-2 h-px bg-border" />
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Frames Analyzed:</span>
                  <span className="font-medium">{details.frames_analyzed}</span>
                </div>
                
                {details.frames_detected_fake !== undefined && (
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Fake Frames:</span>
                    <span className="font-medium text-destructive">
                      {details.frames_detected_fake}
                    </span>
                  </div>
                )}
                
                {details.frames_detected_real !== undefined && (
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Real Frames:</span>
                    <span className="font-medium text-success">
                      {details.frames_detected_real}
                    </span>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      )}

      {/* Warning Message */}
      <div className="rounded-lg border border-primary/20 bg-primary/5 p-4 text-sm">
        <p className="text-muted-foreground">
          <strong className="text-foreground">Note:</strong> This analysis is provided for informational purposes. 
          Always verify important media through multiple sources and professional services.
        </p>
      </div>
    </div>
  );
};
