import { CheckCircle2, AlertTriangle, TrendingUp, Activity } from "lucide-react";
import { Progress } from "@/components/ui/progress";

interface ResultsPanelProps {
  isDeepfake: boolean;
  confidence: number;
  details?: {
    fakeProbability: number;
    realProbability: number;
    framesAnalyzed?: number;
    framesDetectedFake?: number;
    framesDetectedReal?: number;
  };
}

export const ResultsPanel = ({ isDeepfake, confidence, details }: ResultsPanelProps) => {
  const confidenceLevel =
    confidence >= 0.9 ? "Very High" :
    confidence >= 0.7 ? "High" :
    confidence >= 0.5 ? "Moderate" : "Low";

  return (
    <section className="py-8 relative overflow-hidden">
      <div className="container mx-auto px-4 max-w-4xl relative z-10">
        {/* Main Result Card */}
        <div className="glass-neon rounded-3xl p-12 mb-8 relative overflow-hidden animate-scale-in">
          {/* Background Effect */}
          <div className={`absolute inset-0 ${
            isDeepfake 
              ? 'bg-gradient-to-br from-destructive/10 to-destructive/5' 
              : 'bg-gradient-to-br from-success/10 to-success/5'
          }`} />

          {/* Content */}
          <div className="relative z-10 text-center space-y-6">
            {/* Icon */}
            <div className="inline-block relative">
              <div className={`absolute inset-0 ${
                isDeepfake ? 'bg-destructive/20' : 'bg-success/20'
              } rounded-full blur-3xl animate-pulse-glow`} />
              {isDeepfake ? (
                <AlertTriangle className="w-24 h-24 text-destructive relative z-10" strokeWidth={1.5} />
              ) : (
                <CheckCircle2 className="w-24 h-24 text-success relative z-10" strokeWidth={1.5} />
              )}
            </div>

            {/* Status */}
            <div>
              <h2 className="text-5xl font-bold font-['Orbitron'] mb-3">
                {isDeepfake ? (
                  <span className="text-destructive">Deepfake Detected</span>
                ) : (
                  <span className="text-success">Authentic Content</span>
                )}
              </h2>
              <p className="text-xl text-muted-foreground">
                {isDeepfake 
                  ? "This media appears to be artificially generated or manipulated" 
                  : "This media appears to be genuine and unaltered"}
              </p>
            </div>

            {/* Confidence Score */}
            <div className="inline-flex flex-col gap-4 glass-effect rounded-2xl p-8 min-w-[300px]">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Confidence Score</span>
                <span className={`text-3xl font-bold font-['Orbitron'] ${
                  isDeepfake ? 'text-destructive' : 'text-success'
                }`}>
                  {(confidence * 100).toFixed(1)}%
                </span>
              </div>
              <Progress 
                value={confidence * 100} 
                className="h-3"
              />
              <span className={`text-sm font-medium ${
                confidence >= 0.7 ? 'text-success' : confidence >= 0.5 ? 'text-yellow-500' : 'text-destructive'
              }`}>
                {confidenceLevel} Confidence
              </span>
            </div>
          </div>
        </div>

        {/* Detailed Analysis */}
        {details && (
          <div className="grid md:grid-cols-2 gap-6">
            {/* Probability Breakdown */}
            <div className="glass-neon rounded-3xl p-8 animate-slide-in-left">
              <div className="flex items-center gap-3 mb-6">
                <TrendingUp className="w-6 h-6 text-primary" />
                <h3 className="text-2xl font-bold font-['Orbitron']">Probability Analysis</h3>
              </div>
              
              <div className="space-y-6">
                {/* Fake Probability */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Deepfake/AI Generated</span>
                    <span className="font-bold text-destructive">
                      {(details.fakeProbability * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="h-3 bg-secondary rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-gradient-to-r from-destructive to-destructive/70 transition-all duration-1000"
                      style={{ width: `${details.fakeProbability * 100}%` }}
                    />
                  </div>
                </div>

                {/* Real Probability */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Real/Authentic</span>
                    <span className="font-bold text-success">
                      {(details.realProbability * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="h-3 bg-secondary rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-gradient-to-r from-success to-success/70 transition-all duration-1000"
                      style={{ width: `${details.realProbability * 100}%` }}
                    />
                  </div>
                </div>

                {/* Threshold Indicator */}
                <div className="glass-effect rounded-xl p-4 text-sm">
                  <p className="text-muted-foreground">
                    Detection Threshold: <span className="text-primary font-bold">51%</span>
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    Content is classified as deepfake if fake probability exceeds this threshold
                  </p>
                </div>
              </div>
            </div>

            {/* Frame Analysis (for videos) */}
            {details.framesAnalyzed && (
              <div className="glass-neon rounded-3xl p-8 animate-slide-in-right">
                <div className="flex items-center gap-3 mb-6">
                  <Activity className="w-6 h-6 text-secondary" />
                  <h3 className="text-2xl font-bold font-['Orbitron']">Frame Analysis</h3>
                </div>
                
                <div className="space-y-6">
                  {/* Total Frames */}
                  <div className="glass-effect rounded-xl p-4">
                    <div className="text-sm text-muted-foreground mb-1">Total Frames Analyzed</div>
                    <div className="text-4xl font-bold gradient-primary bg-clip-text text-transparent font-['Orbitron']">
                      {details.framesAnalyzed}
                    </div>
                  </div>

                  {/* Frame Breakdown */}
                  <div className="grid grid-cols-2 gap-4">
                    <div className="glass-effect rounded-xl p-4">
                      <div className="text-xs text-muted-foreground mb-1">Fake Detected</div>
                      <div className="text-2xl font-bold text-destructive font-['Orbitron']">
                        {details.framesDetectedFake || 0}
                      </div>
                    </div>
                    <div className="glass-effect rounded-xl p-4">
                      <div className="text-xs text-muted-foreground mb-1">Real Detected</div>
                      <div className="text-2xl font-bold text-success font-['Orbitron']">
                        {details.framesDetectedReal || 0}
                      </div>
                    </div>
                  </div>

                  {/* Visual Representation */}
                  <div className="space-y-2">
                    <div className="text-sm text-muted-foreground">Distribution</div>
                    <div className="flex h-4 rounded-full overflow-hidden">
                      <div 
                        className="bg-destructive"
                        style={{ 
                          width: `${((details.framesDetectedFake || 0) / details.framesAnalyzed) * 100}%` 
                        }}
                      />
                      <div 
                        className="bg-success"
                        style={{ 
                          width: `${((details.framesDetectedReal || 0) / details.framesAnalyzed) * 100}%` 
                        }}
                      />
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Disclaimer */}
        <div className="glass-effect rounded-2xl p-6 mt-8 text-center">
          <p className="text-sm text-muted-foreground">
            <span className="font-bold text-foreground">Important:</span> While our AI achieves high accuracy, 
            always verify media authenticity through multiple sources and methods. This tool should be used 
            as part of a comprehensive verification process.
          </p>
        </div>
      </div>
    </section>
  );
};

// Additional Result Display Components

export const HeatmapOverlay = () => {
  return (
    <div className="glass-neon rounded-2xl p-6">
      <h4 className="font-bold mb-4 font-['Orbitron']">Manipulation Heatmap</h4>
      <div className="aspect-video bg-gradient-to-br from-destructive/20 via-yellow-500/20 to-success/20 rounded-xl relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_40%,hsl(0_84%_60%/0.5),transparent_50%)]" />
        <div className="absolute bottom-4 left-4 right-4 glass-effect rounded-lg p-3 text-sm">
          <p className="text-muted-foreground">Red areas indicate high probability of manipulation</p>
        </div>
      </div>
    </div>
  );
};

export const FaceBoundingBox = () => {
  return (
    <div className="glass-neon rounded-2xl p-6">
      <h4 className="font-bold mb-4 font-['Orbitron']">Face Detection</h4>
      <div className="aspect-video bg-card rounded-xl relative overflow-hidden border border-primary/30">
        <div className="absolute top-1/4 left-1/4 w-1/2 h-1/2 border-2 border-primary shadow-neon rounded-lg">
          <div className="absolute -top-2 -left-2 w-4 h-4 border-t-2 border-l-2 border-primary" />
          <div className="absolute -top-2 -right-2 w-4 h-4 border-t-2 border-r-2 border-primary" />
          <div className="absolute -bottom-2 -left-2 w-4 h-4 border-b-2 border-l-2 border-primary" />
          <div className="absolute -bottom-2 -right-2 w-4 h-4 border-b-2 border-r-2 border-primary" />
        </div>
        <div className="absolute top-4 left-4 glass-effect rounded-lg px-3 py-2 text-sm">
          <span className="text-primary font-bold">Face Detected</span>
        </div>
      </div>
    </div>
  );
};

export const AudioSpectrogram = () => {
  return (
    <div className="glass-neon rounded-2xl p-6">
      <h4 className="font-bold mb-4 font-['Orbitron']">Audio Spectrogram</h4>
      <div className="aspect-video bg-gradient-to-b from-secondary/20 to-background rounded-xl relative overflow-hidden">
        {[...Array(20)].map((_, i) => (
          <div
            key={i}
            className="absolute bottom-0 bg-gradient-to-t from-secondary to-secondary/50"
            style={{
              left: `${i * 5}%`,
              width: '4%',
              height: `${Math.random() * 80 + 20}%`,
              opacity: 0.7,
            }}
          />
        ))}
        <div className="absolute bottom-4 left-4 right-4 glass-effect rounded-lg p-3 text-sm">
          <p className="text-muted-foreground">MFCC frequency analysis shows normal voice patterns</p>
        </div>
      </div>
    </div>
  );
};