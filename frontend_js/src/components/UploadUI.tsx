import { useState, useRef } from "react";
import { Upload, Image, Video, AudioWaveform, X, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";

interface UploadUIProps {
  onFileSelect: (file: File) => void;
  onFrameSelect?: (frames: number) => void;
  maxFrames?: number;
  isProcessing?: boolean;
}

export const UploadUI = ({ onFileSelect, onFrameSelect, maxFrames = 30, isProcessing = false }: UploadUIProps) => {
  const [isDragging, setIsDragging] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [frames, setFrames] = useState(30);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDragIn = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragOut = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      handleFileSelection(files[0]);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFileSelection(files[0]);
    }
  };

  const handleFileSelection = (file: File) => {
    setSelectedFile(file);
    onFileSelect(file);
  };

  const handleClearFile = () => {
    setSelectedFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const isVideo = selectedFile?.type.startsWith("video/");

  return (
    <section id="upload-section" className="py-10 relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-b from-background via-card to-background" />
      
      <div className="container mx-auto px-4 relative z-10 max-w-4xl">
        {/* Section Header */}
        <div className="text-center mb-12 space-y-4 animate-fade-in">
          <h2 className="text-4xl md:text-5xl font-bold font-['Orbitron']">
            Upload for{" "}
            <span className="bg-gradient-to-r from-cyan-300 via-blue-400 to-purple-500 bg-clip-text text-transparent">Analysis</span>
          </h2>
          <p className="text-lg text-muted-foreground">
            Drop your file or click to browse. We support images, videos, and audio files.
          </p>
        </div>

        {/* Upload Zone */}
        <div
          onDrop={handleDrop}
          onDragOver={handleDrag}
          onDragEnter={handleDragIn}
          onDragLeave={handleDragOut}
          onClick={() => !selectedFile && fileInputRef.current?.click()}
          className={`relative group cursor-pointer transition-all duration-300 ${
            isDragging ? 'scale-105' : ''
          }`}
        >
          <div className={`glass-neon rounded-3xl p-12 transition-all duration-300 ${
            isDragging ? 'shadow-neon border-primary/50' : 'hover:shadow-glow'
          } ${isProcessing ? 'pointer-events-none opacity-50' : ''}`}>
            {/* Ripple Effect on Hover */}
            {isDragging && (
              <div className="absolute inset-0 rounded-3xl overflow-hidden pointer-events-none">
                <div className="absolute inset-0 bg-primary/10 animate-ripple" />
              </div>
            )}

            {selectedFile ? (
              // File Preview
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="glass-effect rounded-2xl p-3">
                      {selectedFile.type.startsWith("image/") ? (
                        <Image className="w-8 h-8 text-primary" />
                      ) : selectedFile.type.startsWith("video/") ? (
                        <Video className="w-8 h-8 text-secondary" />
                      ) : (
                        <AudioWaveform className="w-8 h-8 text-destructive" />
                      )}
                    </div>
                    <div>
                      <p className="font-medium">{selectedFile.name}</p>
                      <p className="text-sm text-muted-foreground">
                        {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                    </div>
                  </div>
                  {!isProcessing && (
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleClearFile();
                      }}
                      className="rounded-full hover:bg-destructive/20"
                    >
                      <X className="w-5 h-5" />
                    </Button>
                  )}
                </div>

                {/* Frame Selector for Videos */}
                {isVideo && onFrameSelect && (
                  <div className="glass-effect rounded-2xl p-6 space-y-4">
                    <div className="flex items-center justify-between">
                      <label className="text-sm font-medium">
                        Number of Frames to Analyze
                      </label>
                      <span className="text-2xl  font-bold font-['Orbitron'] leading-tight bg-gradient-to-r from-cyan-300 via-blue-400 to-purple-500 bg-clip-text text-transparent">
                        {frames}
                      </span>
                    </div>
                    <input
                      type="range"
                      min="10"
                      max={maxFrames}
                      step="5"
                      value={frames}
                      onChange={(e) => {
                        const value = parseInt(e.target.value);
                        setFrames(value);
                        onFrameSelect(value);
                      }}
                      className="w-full h-2 bg-secondary rounded-lg appearance-none cursor-pointer accent-primary"
                    />
                    <p className="text-xs text-muted-foreground text-center">
                      More frames = Higher accuracy but slower processing
                    </p>
                  </div>
                )}

                {/* Processing State */}
                {isProcessing && (
                  <div className="flex items-center justify-center gap-3 p-6 glass-effect rounded-2xl">
                    <Loader2 className="w-6 h-6 animate-spin text-primary" />
                    <span className="text-lg font-medium">Analyzing your file...</span>
                  </div>
                )}
              </div>
            ) : (
              // Empty State
              <div className="text-center space-y-6">
                {/* Icons */}
                <div className="flex items-center justify-center gap-8 mb-8">
                  {[
                    { icon: Image, color: "text-primary", label: "Images" },
                    { icon: Video, color: "text-secondary", label: "Videos" },
                    { icon: AudioWaveform, color: "text-destructive", label: "Audio" },
                  ].map(({ icon: Icon, color, label }, i) => (
                    <div key={i} className="space-y-2">
                      <div className={`glass-effect rounded-2xl p-6 ${color} group-hover:scale-110 transition-transform duration-300`}
                           style={{ animationDelay: `${i * 0.1}s` }}>
                        <Icon className="w-12 h-12" strokeWidth={1.5} />
                      </div>
                      <p className="text-xs text-muted-foreground">{label}</p>
                    </div>
                  ))}
                </div>

                {/* Upload Icon */}
                <div className="relative inline-block">
                  <div className="absolute inset-0 bg-primary/20 rounded-full blur-2xl animate-pulse-glow" />
                  <Upload className="w-16 h-16 text-primary relative z-10 mx-auto" strokeWidth={1.5} />
                </div>

                {/* Text */}
                <div className="space-y-2">
                  <p className="text-2xl font-bold font-['Orbitron']">
                    Drop your file here
                  </p>
                  <p className="text-muted-foreground">
                    or click to browse from your device
                  </p>
                </div>

                {/* Supported Formats */}
                <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass-effect text-sm">
                  <span className="text-muted-foreground">Supports:</span>
                  <span className="text-primary font-medium">JPG, PNG, MP4, AVI, MOV, MP3, WAV</span>
                </div>
              </div>
            )}
          </div>

          {/* Hidden File Input */}
          <input
            ref={fileInputRef}
            type="file"
            onChange={handleFileInput}
            accept="image/*,video/*,audio/*"
            className="hidden"
          />

          {/* Glowing Border Animation */}
          {isDragging && (
            <div className="absolute inset-0 rounded-3xl border-2 border-primary animate-pulse-glow pointer-events-none" />
          )}
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-6 mt-12">
          {[
            { title: "Secure", desc: "End-to-end encryption" },
            { title: "Fast", desc: "Results in seconds" },
            { title: "Private", desc: "Files auto-deleted" },
          ].map((feature, i) => (
            <div key={i} className="glass-effect rounded-2xl p-6 text-center hover:shadow-glow transition-all duration-300">
              <h4 className="font-bold mb-2 font-['Orbitron']">{feature.title}</h4>
              <p className="text-sm text-muted-foreground">{feature.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};