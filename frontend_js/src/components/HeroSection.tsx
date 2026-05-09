import { Button } from "@/components/ui/button";
import { Shield, Upload, Sparkles } from "lucide-react";
import cloudshieldLogo from "@/assets/cloudshield-logo.png";
import { HologramCube } from "./HologramCube";

interface HeroSectionProps {
  onTryDetection: () => void;
  onUploadClick: () => void;
}

export const HeroSection = ({ onTryDetection, onUploadClick }: HeroSectionProps) => {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0 bg-gradient-to-b from-background via-background to-card">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_20%,hsl(189_94%_55%/0.1),transparent_50%)]" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_70%_80%,hsl(270_80%_60%/0.1),transparent_50%)]" />
        
        {/* Animated Grid */}
        <div className="absolute inset-0 bg-[linear-gradient(to_right,hsl(240_10%_15%)_1px,transparent_1px),linear-gradient(to_bottom,hsl(240_10%_15%)_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_80%_50%_at_50%_50%,#000_60%,transparent_100%)]" />
      </div>

      {/* Floating Particles */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {[...Array(20)].map((_, i) => (
          <div
            key={i}
            className="absolute w-1 h-1 bg-primary rounded-full animate-float opacity-40"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 5}s`,
              animationDuration: `${5 + Math.random() * 10}s`,
            }}
          />
        ))}
      </div>

      <div className="container mx-auto px-4 relative z-10">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Left Content */}
          <div className="space-y-8 animate-fade-in">
            {/* Logo & Brand */}
            <div className="flex items-center gap-4 mb-6">
              <img 
                src={cloudshieldLogo} 
                alt="DeepDetect" 
                className="w-16 h-16 animate-pulse-glow"
              />
              <div>
                <h1 className="text-4xl font-bold font-['Orbitron'] bg-gradient-to-r from-cyan-300 via-blue-400 to-purple-500 bg-clip-text text-transparent">
                  DeepDetect
                </h1>
                <p className="text-3x1 text-muted-foreground">Powered by Advanced AI</p>
              </div>
            </div>

            {/* Main Headline */}
            <div className="space-y-4">
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass-neon animate-pulse-glow">
                <Sparkles className="w-4 h-4 text-primary" />
                <span className="text-sm font-medium text-primary">91.4% Detection Accuracy</span>
              </div>
              
              <h2 className="text-5xl md:text-7xl font-bold font-['Orbitron'] leading-tight">
                Detect Deepfakes{" "}
                <span className="text-5xl md:text-7xl font-bold font-['Orbitron'] leading-tight bg-gradient-to-r from-cyan-300 via-blue-400 to-purple-500 bg-clip-text text-transparent">
                  Instantly
                </span>
              </h2>
              
              <p className="text-xl text-muted-foreground leading-relaxed max-w-xl">
                Advanced AI-powered forensics to verify authenticity of images, videos, and audio. 
                Protect yourself from manipulated media.
              </p>
            </div>

            {/* CTA Buttons */}
            <div className="flex flex-wrap gap-4">
              {/* <Button 
                size="lg" 
                onClick={onTryDetection}
                className="text-lg px-8 py-6 gradient-primary shadow-neon hover:shadow-glow-purple transition-all duration-300 hover:scale-105 font-['Orbitron']"
              >
                <Shield className="w-5 h-5 mr-2" />
                Try Detection
              </Button> */}
              
              <Button 
                size="lg" 
                variant="outline"
                onClick={onUploadClick}
                className="text-lg px-10 py-7 neon-border hover:bg-primary/10 transition-all duration-300 hover:scale-110 font-['Orbitron'] rounded-xl"
              >
                <Upload className="w-5 h-5 mr-2" />
                Try Detection
              </Button>
            </div>

            {/* Stats */}
            {/* <div className="grid grid-cols-3 gap-6 pt-8 border-t border-border/50 [&_*]:text-black">
              {[
                { value: "1M+", label: "Files Analyzed" },
                { value: "91.4%", label: "Accuracy" },
                { value: "<2s", label: "Avg Speed" },
              ].map((stat, i) => (
                <div key={i} className="space-y-1">
                  <div className="text-3xl font-bold gradient-primary bg-clip-text text-transparent font-['Orbitron']">
                    {stat.value}
                  </div>
                  <div className="text-sm text-muted-foreground">{stat.label}</div>
                </div>
              ))}
            </div> */}
          </div>

          {/* Right - Hologram Cube */}
          <div className="relative flex items-center justify-center">
            <HologramCube />
          </div>
        </div>
      </div>

      {/* Bottom Gradient */}
      <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-background to-transparent" />
    </section>
  );
};