import { useCallback, useState } from "react";
import { Upload, FileVideo, Image as ImageIcon } from "lucide-react";
import { cn } from "@/lib/utils";

interface UploadZoneProps {
  onFileSelect: (file: File) => void;
  accept?: string;
  className?: string;
}

export const UploadZone = ({ onFileSelect, accept = "image/*,video/*", className }: UploadZoneProps) => {
  const [isDragging, setIsDragging] = useState(false);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDragIn = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.dataTransfer.items && e.dataTransfer.items.length > 0) {
      setIsDragging(true);
    }
  }, []);

  const handleDragOut = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      onFileSelect(e.dataTransfer.files[0]);
    }
  }, [onFileSelect]);

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      onFileSelect(e.target.files[0]);
    }
  };

  return (
    <div
      className={cn(
        "relative overflow-hidden rounded-xl border-2 border-dashed transition-all duration-300",
        isDragging
          ? "border-primary bg-primary/5 shadow-glow"
          : "border-border bg-card/50 hover:border-primary/50 hover:bg-card/70",
        className
      )}
      onDragEnter={handleDragIn}
      onDragLeave={handleDragOut}
      onDragOver={handleDrag}
      onDrop={handleDrop}
    >
      <label className="flex cursor-pointer flex-col items-center justify-center p-12 text-center">
        <div className={cn(
          "mb-4 rounded-full p-6 transition-all duration-300",
          isDragging ? "bg-primary/20 scale-110" : "bg-primary/10"
        )}>
          <Upload className={cn(
            "h-12 w-12 transition-all duration-300",
            isDragging ? "text-primary scale-110" : "text-primary/70"
          )} />
        </div>
        
        <h3 className="mb-2 text-xl font-semibold text-foreground">
          {isDragging ? "Drop your file here" : "Upload Image or Video"}
        </h3>
        
        <p className="mb-4 text-sm text-muted-foreground">
          Drag and drop your file here, or click to browse
        </p>

        <div className="flex gap-4 text-xs text-muted-foreground">
          <div className="flex items-center gap-1">
            <ImageIcon className="h-4 w-4" />
            <span>Images: JPG, PNG, BMP, TIFF, WebP</span>
          </div>
          <div className="flex items-center gap-1">
            <FileVideo className="h-4 w-4" />
            <span>Videos: MP4, AVI, MOV, MKV</span>
          </div>
        </div>

        <input
          type="file"
          accept={accept}
          onChange={handleFileInput}
          className="hidden"
        />
      </label>

      {/* Animated gradient border effect */}
      {isDragging && (
        <div className="pointer-events-none absolute inset-0 animate-pulse rounded-xl bg-gradient-to-r from-primary/20 via-transparent to-primary/20" />
      )}
    </div>
  );
};
