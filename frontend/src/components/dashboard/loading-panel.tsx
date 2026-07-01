import { Loader2, Radar } from "lucide-react";

import { Progress } from "@/components/ui/progress";
import type { AnalysisPhase } from "@/types/ranking";

type LoadingPanelProps = {
  phase: AnalysisPhase;
  uploadProgress: number;
};

export function LoadingPanel({ phase, uploadProgress }: LoadingPanelProps) {
  const isUploading = phase === "uploading";

  return (
    <section className="rounded-[1.75rem] border border-border/70 bg-card/88 p-6 shadow-panel backdrop-blur md:p-7">
      <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
        <div className="flex items-start gap-4">
          <div className="inline-flex h-14 w-14 items-center justify-center rounded-[1.4rem] bg-gradient-signal text-card shadow-spotlight">
            {isUploading ? (
              <Loader2 className="h-7 w-7 animate-spin" />
            ) : (
              <Radar className="h-7 w-7 animate-pulse" />
            )}
          </div>

          <div>
            <h3 className="font-display text-xl font-semibold text-foreground">
              {isUploading ? "Uploading candidate dataset..." : "AI is analyzing candidates..."}
            </h3>
            <p className="mt-2 max-w-2xl text-sm text-muted-foreground">
              {isUploading
                ? "We are streaming your file to the FastAPI service now. Inputs stay locked until the upload finishes."
                : "TalentMind is scoring skill alignment, experience, strengths, and ranking confidence across the uploaded candidates."}
            </p>
          </div>
        </div>

        <div className="rounded-full border border-border/60 bg-background/70 px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-muted-foreground">
          {isUploading ? `${uploadProgress}% uploaded` : "Processing"}
        </div>
      </div>

      <div className="mt-6 space-y-4">
        <Progress
          value={isUploading ? uploadProgress : 100}
          className={isUploading ? "" : "animate-progress-wave"}
        />

        <div className="grid gap-3 md:grid-cols-3">
          {[
            "Parsing uploaded records",
            "Matching the job description",
            "Preparing ranked candidate insights",
          ].map((label, index) => (
            <div
              key={label}
              className={`rounded-[1.2rem] border p-4 text-sm animate-fade-up ${
                phase === "processing"
                  ? "border-brand-cyan/30 bg-brand-cyan/8 text-foreground"
                  : "border-border/60 bg-background/55 text-muted-foreground"
              }`}
              style={{ animationDelay: `${index * 80}ms` }}
            >
              <div className="mb-2 h-1.5 rounded-full bg-gradient-signal opacity-70" />
              {label}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
