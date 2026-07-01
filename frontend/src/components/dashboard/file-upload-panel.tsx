import { useCallback, useRef, useState } from "react";
import { AlertCircle, FileUp, Loader2, UploadCloud, X } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import type { AnalysisPhase } from "@/types/ranking";
import { formatFileSize } from "@/utils/format";
import { getAcceptedFileTypes, getSupportedFileTypesLabel } from "@/utils/file-validation";

type FileUploadPanelProps = {
  error: string | null;
  file: File | null;
  isBusy: boolean;
  phase: AnalysisPhase;
  uploadProgress: number;
  onClearFile: () => void;
  onFileSelect: (file: File | null) => void;
};

export function FileUploadPanel({
  error,
  file,
  isBusy,
  onClearFile,
  onFileSelect,
  phase,
  uploadProgress,
}: FileUploadPanelProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleFiles = useCallback(
    (files: FileList | null) => {
      const selectedFile = files?.[0] ?? null;
      onFileSelect(selectedFile);
    },
    [onFileSelect],
  );

  return (
    <section className="rounded-[1.75rem] border border-border/70 bg-card/85 p-6 shadow-panel backdrop-blur md:p-7">
      <div className="flex items-start justify-between gap-4">
        <div className="space-y-2">
          <div className="inline-flex h-11 w-11 items-center justify-center rounded-2xl bg-brand-gold/15 text-brand-gold">
            <FileUp className="h-5 w-5" />
          </div>
          <div>
            <h2 className="font-display text-xl font-semibold text-foreground">
              Candidate Dataset
            </h2>
            <p className="mt-1 max-w-xl text-sm text-muted-foreground">
              Upload anonymized candidate data in JSONL, JSON, CSV, or XLSX format. Drag and drop
              works, and you can still browse manually if you prefer.
            </p>
          </div>
        </div>
        <div className="rounded-full border border-border/60 bg-background/70 px-3 py-1 text-xs font-medium text-muted-foreground">
          {getSupportedFileTypesLabel()}
        </div>
      </div>

      <div className="mt-5 space-y-4">
        <div
          role="button"
          tabIndex={isBusy ? -1 : 0}
          onClick={() => {
            if (!isBusy) {
              inputRef.current?.click();
            }
          }}
          onKeyDown={(event) => {
            if ((event.key === "Enter" || event.key === " ") && !isBusy) {
              event.preventDefault();
              inputRef.current?.click();
            }
          }}
          onDragOver={(event) => {
            event.preventDefault();
            if (!isBusy) {
              setIsDragging(true);
            }
          }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={(event) => {
            event.preventDefault();
            setIsDragging(false);

            if (!isBusy) {
              handleFiles(event.dataTransfer.files);
            }
          }}
          className={`rounded-[1.5rem] border-2 border-dashed px-5 py-10 text-center transition duration-200 ${
            isBusy
              ? "cursor-not-allowed border-border/60 bg-background/55 opacity-75"
              : isDragging
                ? "border-brand-cyan bg-brand-cyan/8 shadow-spotlight"
                : "cursor-pointer border-border/70 bg-background/50 hover:border-brand-cyan/70 hover:bg-brand-cyan/6"
          }`}
        >
          <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-3xl bg-gradient-signal text-card shadow-spotlight">
            {phase === "uploading" || phase === "processing" ? (
              <Loader2 className="h-7 w-7 animate-spin" />
            ) : (
              <UploadCloud className="h-7 w-7" />
            )}
          </div>

          <h3 className="mt-4 font-display text-lg font-semibold text-foreground">
            Drag and drop your dataset
          </h3>
          <p className="mt-2 text-sm text-muted-foreground">
            Drop one file here, or use the browse button below to choose a file from disk.
          </p>

          <input
            ref={inputRef}
            type="file"
            accept={getAcceptedFileTypes()}
            className="hidden"
            disabled={isBusy}
            onChange={(event) => handleFiles(event.target.files)}
          />
        </div>

        <div className="flex flex-col gap-3 sm:flex-row">
          <Button
            type="button"
            variant="outline"
            className="h-11 rounded-full border-border/70 bg-background/70 px-5"
            disabled={isBusy}
            onClick={() => inputRef.current?.click()}
          >
            Browse Files
          </Button>
          <p className="flex items-center text-xs text-muted-foreground">
            Supported formats: {getSupportedFileTypesLabel()}
          </p>
        </div>

        {file ? (
          <div className="rounded-[1.3rem] border border-border/70 bg-background/70 px-4 py-4">
            <div className="flex items-start gap-3">
              <div className="inline-flex h-11 w-11 items-center justify-center rounded-2xl bg-brand-ink text-brand-cyan">
                <FileUp className="h-5 w-5" />
              </div>

              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-semibold text-foreground">{file.name}</p>
                <p className="mt-1 text-xs text-muted-foreground">{formatFileSize(file.size)}</p>
              </div>

              <button
                type="button"
                disabled={isBusy}
                onClick={onClearFile}
                className="inline-flex h-9 w-9 items-center justify-center rounded-full border border-border/70 text-muted-foreground transition hover:border-foreground/20 hover:text-foreground disabled:cursor-not-allowed disabled:opacity-50"
                aria-label="Remove uploaded file"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            {(phase === "uploading" || phase === "processing") && (
              <div className="mt-4 space-y-2">
                <div className="flex items-center justify-between text-xs text-muted-foreground">
                  <span>
                    {phase === "uploading"
                      ? "Uploading dataset to backend..."
                      : "Upload complete. Backend is processing candidate rankings..."}
                  </span>
                  <span>{phase === "uploading" ? `${uploadProgress}%` : "Analyzing"}</span>
                </div>
                <Progress
                  value={phase === "uploading" ? uploadProgress : 100}
                  className={phase === "processing" ? "animate-progress-wave" : ""}
                />
              </div>
            )}
          </div>
        ) : null}

        {error ? (
          <div className="flex items-center gap-2 rounded-2xl border border-destructive/30 bg-destructive/8 px-4 py-3 text-sm text-destructive">
            <AlertCircle className="h-4 w-4 shrink-0" />
            <span>{error}</span>
          </div>
        ) : (
          <p className="text-xs text-muted-foreground">
            XLSX and CSV uploads should contain the same candidate fields as the JSON dataset, using
            JSON values for nested sections when needed.
          </p>
        )}
      </div>
    </section>
  );
}
