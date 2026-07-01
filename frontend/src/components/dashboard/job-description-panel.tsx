import { AlertCircle, FileText } from "lucide-react";

import { Textarea } from "@/components/ui/textarea";

type JobDescriptionPanelProps = {
  characterCount: number;
  error: string | null;
  isBusy: boolean;
  value: string;
  onChange: (value: string) => void;
};

export function JobDescriptionPanel({
  characterCount,
  error,
  isBusy,
  value,
  onChange,
}: JobDescriptionPanelProps) {
  return (
    <section className="rounded-[1.75rem] border border-border/70 bg-card/85 p-6 shadow-panel backdrop-blur md:p-7">
      <div className="flex items-start justify-between gap-4">
        <div className="space-y-2">
          <div className="inline-flex h-11 w-11 items-center justify-center rounded-2xl bg-brand-cyan/12 text-brand-cyan">
            <FileText className="h-5 w-5" />
          </div>
          <div>
            <h2 className="font-display text-xl font-semibold text-foreground">Job Description</h2>
            <p className="mt-1 max-w-xl text-sm text-muted-foreground">
              Paste the role brief, responsibilities, and must-have skills. TalentMind will infer
              the ranking criteria from the text you provide.
            </p>
          </div>
        </div>
        <div className="rounded-full border border-border/60 bg-background/70 px-3 py-1 text-xs font-medium text-muted-foreground">
          {characterCount} characters
        </div>
      </div>

      <div className="mt-5 space-y-3">
        <Textarea
          value={value}
          onChange={(event) => onChange(event.target.value)}
          disabled={isBusy}
          placeholder="Example: We are hiring a Retrieval Engineer with strong Python, vector database, ranking, semantic search, and LLM experience..."
          className="min-h-[260px] rounded-[1.4rem] border-border/70 bg-background/65 px-5 py-4 text-sm leading-7 shadow-none transition focus-visible:ring-2 focus-visible:ring-brand-cyan/40 disabled:cursor-not-allowed disabled:opacity-70"
        />

        {error ? (
          <div className="flex items-center gap-2 rounded-2xl border border-destructive/30 bg-destructive/8 px-4 py-3 text-sm text-destructive">
            <AlertCircle className="h-4 w-4 shrink-0" />
            <span>{error}</span>
          </div>
        ) : (
          <p className="text-xs text-muted-foreground">
            Empty job descriptions are blocked so the backend receives valid ranking context.
          </p>
        )}
      </div>
    </section>
  );
}
