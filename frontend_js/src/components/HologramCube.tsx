import { Image, Video, AudioWaveform } from "lucide-react";

export const HologramCube = () => {
  return (
    <div className="relative w-full max-w-md aspect-square flex items-center justify-center">
      {/* Outer Glow Ring */}
      <div className="absolute inset-0 rounded-full bg-gradient-to-r from-primary/20 via-secondary/20 to-primary/20 animate-spin-slow blur-3xl" />
      
      {/* Central Hologram Container */}
      <div className="relative w-72 h-72 animate-float">
        {/* 3D Cube Effect */}
        <div className="absolute inset-0 transform-gpu preserve-3d animate-spin-slow">
          {/* Front Face - Image Icon */}
          <div className="absolute inset-0 flex items-center justify-center glass-neon rounded-2xl transform translate-z-12 animate-pulse-glow">
            <div className="relative">
              <div className="absolute inset-0 bg-primary/20 rounded-full blur-2xl" />
              <Image className="w-20 h-20 text-primary relative z-10" strokeWidth={1.5} />
            </div>
          </div>
          
          {/* Back Face - Video Icon */}
          <div className="absolute inset-0 flex items-center justify-center glass-neon rounded-2xl transform rotate-y-180 translate-z-12">
            <div className="relative">
              <div className="absolute inset-0 bg-secondary/20 rounded-full blur-2xl" />
              <Video className="w-20 h-20 text-secondary relative z-10" strokeWidth={1.5} />
            </div>
          </div>
        </div>

        {/* Rotating Ring */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-full h-full border-2 border-primary/30 rounded-full animate-spin-slow" 
               style={{ animationDuration: '15s' }} />
        </div>
        
        {/* Audio Waveform - Orbiting */}
        <div className="absolute inset-0 flex items-center justify-center animate-spin-slow" 
             style={{ animationDuration: '10s' }}>
          <div className="absolute top-0 transform -translate-y-8">
            <div className="glass-neon rounded-2xl p-4 shadow-neon-purple">
              <AudioWaveform className="w-12 h-12 text-secondary" strokeWidth={1.5} />
            </div>
          </div>
        </div>

        {/* Holographic Scan Lines */}
        <div className="absolute inset-0 overflow-hidden rounded-2xl pointer-events-none">
          {[...Array(5)].map((_, i) => (
            <div
              key={i}
              className="absolute w-full h-px bg-gradient-to-r from-transparent via-primary/50 to-transparent"
              style={{
                top: `${(i + 1) * 20}%`,
                animation: `shimmer 2s linear infinite`,
                animationDelay: `${i * 0.2}s`,
              }}
            />
          ))}
        </div>

        {/* Corner Brackets */}
        {['top-left', 'top-right', 'bottom-left', 'bottom-right'].map((corner) => (
          <div
            key={corner}
            className={`absolute w-8 h-8 border-2 border-primary ${
              corner.includes('top') ? 'top-0' : 'bottom-0'
            } ${
              corner.includes('left') ? 'left-0' : 'right-0'
            } ${
              corner.includes('top') && corner.includes('left')
                ? 'border-r-0 border-b-0'
                : corner.includes('top') && corner.includes('right')
                ? 'border-l-0 border-b-0'
                : corner.includes('bottom') && corner.includes('left')
                ? 'border-r-0 border-t-0'
                : 'border-l-0 border-t-0'
            }`}
          />
        ))}

        {/* Data Streams */}
        <div className="absolute -left-24 top-1/2 transform -translate-y-1/2">
          <div className="flex flex-col gap-2">
            {[...Array(4)].map((_, i) => (
              <div
                key={i}
                className="h-1 bg-gradient-to-r from-primary/0 via-primary to-primary/0 rounded-full"
                style={{
                  width: `${60 + Math.random() * 40}px`,
                  animationDelay: `${i * 0.3}s`,
                }}
              />
            ))}
          </div>
        </div>

        <div className="absolute -right-24 top-1/2 transform -translate-y-1/2">
          <div className="flex flex-col gap-2">
            {[...Array(4)].map((_, i) => (
              <div
                key={i}
                className="h-1 bg-gradient-to-r from-secondary/0 via-secondary to-secondary/0 rounded-full"
                style={{
                  width: `${60 + Math.random() * 40}px`,
                  animationDelay: `${i * 0.3}s`,
                }}
              />
            ))}
          </div>
        </div>
      </div>

      {/* Bottom Text */}
      <div className="absolute -bottom-12 left-1/2 transform -translate-x-1/2 text-center">
        <p className="text-sm text-primary font-['Orbitron'] tracking-wider">
          AI-POWERED DETECTION
        </p>
      </div>
    </div>
  );
};