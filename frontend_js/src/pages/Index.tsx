import { analyzeDeepfake } from "@/lib/api";
import { useState } from "react";
import { HeroSection } from "@/components/HeroSection";
import { UploadUI } from "@/components/UploadUI";
import { HowItWorks } from "@/components/HowItWorks";
import { ResultsPanel } from "@/components/ResultsComponents";
import { toast } from "@/hooks/use-toast";

export default function Index() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [maxFrames, setMaxFrames] = useState(30);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const [results, setResults] = useState<{
    isDeepfake: boolean;
    confidence: number;
    details?: {
      fakeProbability: number;
      realProbability: number;
      framesAnalyzed?: number;
      framesDetectedFake?: number;
      framesDetectedReal?: number;
    };
  } | null>(null);

  // Smooth scroll to upload area
  const scrollToUpload = () => {
    const el = document.getElementById("upload-section");
    el?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  // Called when a file is selected
  const handleFileSelect = async (file: File) => {
    setSelectedFile(file);
    setResults(null);

    toast({
      title: "File Selected",
      description: `${file.name} is ready for analysis`,
    });

    await handleAnalyze(file);
  };

  // Main deepfake analysis logic
  const handleAnalyze = async (file: File) => {
    if (!file || file.size === 0) {
    console.warn("Skipping empty or invalid analyze call.");
    return;
    }
    setIsAnalyzing(true);

    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("max_frames", String(maxFrames));

      const apiResults = await analyzeDeepfake(formData, file);

      setResults(apiResults);

      toast({
        title: "Analysis Complete",
        description: `Detection: ${
          apiResults.isDeepfake ? "Deepfake" : "Authentic"
        } (${(apiResults.confidence * 100).toFixed(1)}% confidence)`,
        variant: apiResults.isDeepfake ? "destructive" : "default",
      });

      setTimeout(() => {
        window.scrollTo({
          top: document.documentElement.scrollHeight,
          behavior: "smooth",
        });
      }, 150);
    } catch (error) {
      toast({
        title: "Analysis Failed",
        description: "Error analyzing your file. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="min-h-screen bg-background relative overflow-hidden">
      {/* Background Blurs */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-0 -left-1/4 w-1/2 h-1/2 bg-primary/5 rounded-full blur-[100px] animate-pulse" />
        <div
          className="absolute bottom-0 -right-1/4 w-1/2 h-1/2 bg-secondary/5 rounded-full blur-[100px] animate-pulse"
          style={{ animationDelay: "1s" }}
        />
      </div>

      <div className="relative z-10">
        <HeroSection
          onTryDetection={scrollToUpload}
          onUploadClick={scrollToUpload}
        />


        <UploadUI
          onFileSelect={handleFileSelect}
          onFrameSelect={setMaxFrames}
          maxFrames={maxFrames}
          isProcessing={isAnalyzing}
        />

        

        {results && (
          <ResultsPanel
            isDeepfake={results.isDeepfake}
            confidence={results.confidence}
            details={results.details}
          />
        )}
        <HowItWorks />
        {/* Footer */}
        <footer className="py-12 border-t border-border/50">
          <div className="container mx-auto px-4">
            <div className="text-center space-y-4">
              <p className="text-3xl font-bold font-['Orbitron'] gradient-primary bg-clip-text text-white ">
                DeepDetect
              </p>
              <p className="text-sm text-muted-foreground">
                Advanced Deepfake Detection Platform
              </p>
              <p className="text-xs text-muted-foreground">
                © 2025 DeepDetect. Protecting media authenticity with
                cutting-edge AI.
              </p>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
}
