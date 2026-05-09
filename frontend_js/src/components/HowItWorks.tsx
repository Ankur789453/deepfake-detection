import { useState, useEffect, useRef } from "react";
import { Image, Video, AudioWaveform, ChevronLeft, ChevronRight } from "lucide-react";

const capabilities = [
  {
    icon: Image,
    title: "Image Deepfake Detection",
    description: "Advanced forensic analysis reveals manipulation patterns invisible to the human eye",
    features: ["Pixel-level analysis", "Metadata verification", "AI artifact detection"],
    color: "from-primary to-primary/50",
    hoverEffect: "Heatmap Overlay",
  },
  {
    icon: Video,
    title: "Video Deepfake Detection",
    description: "Frame-by-frame temporal analysis detects inconsistencies across video sequences",
    features: ["Temporal consistency", "Face morphing detection", "Audio-visual sync"],
    color: "from-secondary to-secondary/50",
    hoverEffect: "Frame Split View",
  },
  {
    icon: AudioWaveform,
    title: "Audio Deepfake Detection",
    description: "Voice fingerprinting and spectrogram analysis identifies synthetic speech patterns",
    features: ["Voice biometrics", "MFCC analysis", "Frequency anomalies"],
    color: "from-green-400 to-green-600/50",
    hoverEffect: "Spectrogram View",
  },
];

export const HowItWorks = () => {
  const [activeIndex, setActiveIndex] = useState(0);
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Auto-advance every 5s when not hovered
  useEffect(() => {
    const interval = setInterval(() => {
      if (hoveredIndex === null) setActiveIndex((p) => (p + 1) % capabilities.length);
    }, 5000);
    return () => clearInterval(interval);
  }, [hoveredIndex]);

  // Scroll to active card (calculates card width same as CapabilitySlider)
  useEffect(() => {
    if (!containerRef.current) return;
    const container = containerRef.current;
    // Card width on small screens should match w-[90%], on md w-[45%], on lg w-[30%]
    // We'll compute current card width by measuring the first child
    const firstCard = container.querySelector<HTMLElement>(".cap-card");
    if (firstCard) {
      container.scrollTo({ left: firstCard.offsetLeft, behavior: "smooth" });
      // If activeIndex > 0, scroll to that child's offset
      const target = container.querySelectorAll<HTMLElement>(".cap-card")[activeIndex];
      if (target) container.scrollTo({ left: target.offsetLeft, behavior: "smooth" });
    }
  }, [activeIndex]);

  const scrollToIndex = (index: number) => {
    setActiveIndex(index);
    if (containerRef.current) {
      const target = containerRef.current.querySelectorAll<HTMLElement>(".cap-card")[index];
      if (target) containerRef.current.scrollTo({ left: target.offsetLeft, behavior: "smooth" });
    }
  };

  return (
    <section className="py-0 relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-b from-background via-card to-background" />
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,hsl(189_94%_55%/0.05),transparent_70%)]" />

      <div className="container mx-auto px-4 relative z-10">
        {/* Section Header */}
        <div className="text-center mb-16 space-y-4 animate-fade-in">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass-effect">
            <span className="text-sm font-medium text-primary font-['Orbitron']">CORE CAPABILITIES</span>
          </div>
          <h2 className="text-4xl md:text-6xl font-bold font-['Orbitron']">
            Triple-Layer{' '}
            <span className="bg-gradient-to-r from-cyan-300 via-blue-400 to-purple-500 bg-clip-text text-transparent">Detection</span>
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">Comprehensive analysis across all media types using cutting-edge AI forensics</p>
        </div>

        {/* Cards Container (matches CapabilitySlider sizing) */}
        <div
          ref={containerRef}
          className="flex gap-6 overflow-x-auto snap-x snap-mandatory hide-scrollbar py-8 pb-8 mb-0"
          onMouseEnter={() => setHoveredIndex(activeIndex)}
          onMouseLeave={() => setHoveredIndex(null)}
          style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
        >
          {capabilities.map((capability, index) => {
            const Icon = capability.icon;
            const isActive = false;
            const isHovered = index === hoveredIndex;

            return (
              <div
                key={index}
                className={`cap-card flex-shrink-0 w-[90%] md:w-[45%] lg:w-[30%] snap-center transition-all duration-500 ${
                  isHovered ? 'scale-100' : 'scale-95 opacity-60'
                }`}
                onMouseEnter={() => setHoveredIndex(index)}
                onMouseLeave={() => setHoveredIndex(null)}
                // onClick={() => scrollToIndex(index)}
              >
                <div className={`glass-neon rounded-3xl p-8 h-full relative overflow-visible group cursor-pointer animate-tilt ${isHovered ? 'shadow-neon' : ''}`}>
                  {/* Number Badge */}
                  <div className="absolute -top-6 left-1/2 transform -translate-x-1/2 text-8xl font-bold text-primary/40 font-['Orbitron'] pointer-events-none">
                    0{index + 1}
                  </div>


                  {/* Icon */}
                  <div className="relative mb-6">
                    <div
                      className={`
                        absolute inset-0 bg-gradient-to-br ${capability.color}
                        rounded-full blur-2xl opacity-50
                        animate-pulse-glow
                        group-hover:opacity-80
                        transition-all
                      `}
                    />

                    <div className="relative glass-effect rounded-2xl p-4 w-fit group-hover:scale-110 transition-transform duration-300">
                      <Icon className="w-12 h-12 text-primary" strokeWidth={1.5} />
                    </div>
                  </div>

                  {/* Content */}
                  <h3 className="text-2xl font-bold mb-4 font-['Orbitron']">{capability.title}</h3>
                  <p className="text-muted-foreground mb-6 leading-relaxed">{capability.description}</p>

                  {/* Features */}
                  <ul className="space-y-3">
                    {capability.features.map((feature, i) => (
                      <li key={i} className="flex items-center gap-3 text-sm group/item">
                        <div className="w-1.5 h-1.5 rounded-full bg-primary group-hover/item:scale-150 transition-transform" />
                        <span className="group-hover/item:text-primary transition-colors">{feature}</span>
                      </li>
                    ))}
                  </ul>

                  {/* Hover Glow */}
                  <div className="absolute inset-0 bg-gradient-to-br from-primary/0 via-primary/0 to-primary/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
                  {/* Hover Effect Indicator */}
                  <div
                    className={`text-sm font-medium font-['Orbitron'] text-primary transition-opacity mt-4 ${
                      isHovered ? "opacity-100" : "opacity-0"
                    }`}
                  >
                    → {capability.hoverEffect}
                  </div>

                  {/* Scan Line Effect */}
                  {isHovered && (
                    <div className="absolute inset-0 overflow-hidden pointer-events-none">
                    <div className="absolute w-full h-px bg-gradient-to-r from-transparent via-primary to-transparent animate-shimmer" />
                    </div>
                  )}

                  {/* Animated Border */}
                  <div className="absolute inset-0 rounded-3xl overflow-hidden pointer-events-none">
                    <div className="absolute inset-0 border border-primary/0 group-hover:border-primary/20 transition-colors duration-500" />
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Navigation
        <div className="flex items-center justify-center gap-4">
          <button onClick={() => scrollToIndex((activeIndex - 1 + capabilities.length) % capabilities.length)} className="rounded-full neon-border p-2">
            <ChevronLeft className="w-5 h-5" />
          </button>

          <div className="flex gap-2">
            {capabilities.map((_, index) => (
              <button key={index} onClick={() => scrollToIndex(index)} className={`w-2 h-2 rounded-full transition-all duration-300 ${index === activeIndex ? 'bg-primary w-8 shadow-neon' : 'bg-border hover:bg-muted-foreground'}`} />
            ))}
          </div>

          <button onClick={() => scrollToIndex((activeIndex + 1) % capabilities.length)} className="rounded-full neon-border p-2">
            <ChevronRight className="w-5 h-5" />
          </button>
        </div> */}
      </div>

      <style>{` .hide-scrollbar::-webkit-scrollbar { display: none; } `}</style>
    </section>
  );
};
