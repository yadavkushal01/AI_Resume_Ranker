import { useState } from "react";
import { Bot, RefreshCcw, Sparkles } from "lucide-react";
import { toast } from "sonner";

import { FileUploadPanel } from "@/components/dashboard/file-upload-panel";
import { JobDescriptionPanel } from "@/components/dashboard/job-description-panel";
import { LoadingPanel } from "@/components/dashboard/loading-panel";
import { ResultsPanel } from "@/components/dashboard/results-panel";
import { Button } from "@/components/ui/button";
import { useBackendStatus } from "@/hooks/use-backend-status";
import { ApiRequestError, rankCandidates } from "@/services/api";
import type { AnalysisPhase, RankResponse } from "@/types/ranking";
import { validateCandidateFile } from "@/utils/file-validation";

const TOP_CANDIDATES_LIMIT = 100;

const STATUS_STYLES = {
  checking: "border-border/70 bg-background/75 text-muted-foreground",
  offline: "border-destructive/20 bg-destructive/10 text-destructive",
  online: "border-brand-cyan/20 bg-brand-cyan/12 text-brand-cyan",
} as const;

export function ResumeRankerPage() {
  const [jobDescription, setJobDescription] = useState("");
  const [jobError, setJobError] = useState<string | null>(null);
  const [fileError, setFileError] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [phase, setPhase] = useState<AnalysisPhase>("idle");
  const [uploadProgress, setUploadProgress] = useState(0);
  const [response, setResponse] = useState<RankResponse | null>(null);

  const { message: backendMessage, refresh, status } = useBackendStatus();
  const isBusy = phase !== "idle";

  function handleFileSelect(file: File | null) {
    if (!file) {
      setSelectedFile(null);
      setFileError(null);
      return;
    }

    const validationMessage = validateCandidateFile(file);

    if (validationMessage) {
      setSelectedFile(null);
      setFileError(validationMessage);
      toast.error(validationMessage);
      return;
    }

    setSelectedFile(file);
    setFileError(null);
  }

  function limitTopCandidates(nextResponse: RankResponse): RankResponse {
    const candidates = nextResponse.candidates.slice(0, TOP_CANDIDATES_LIMIT);

    return {
      ...nextResponse,
      summary: {
        ...nextResponse.summary,
        total_candidates: candidates.length,
      },
      candidates,
    };
  }

  async function handleAnalyze() {
    let blocked = false;

    if (!jobDescription.trim()) {
      setJobError("Paste the job description before launching the ranking flow.");
      toast.error("Job description is required.");
      blocked = true;
    } else {
      setJobError(null);
    }

    if (!selectedFile) {
      setFileError("Upload a supported candidate dataset before running analysis.");
      toast.error("Candidate dataset is required.");
      blocked = true;
    } else {
      setFileError(null);
    }

    if (blocked) {
      return;
    }

    setUploadProgress(0);
    setResponse(null);

    if (!selectedFile) {
      return;
    }

    setPhase("uploading");

    try {
      const nextResponse = await rankCandidates(jobDescription.trim(), selectedFile, {
        onPhaseChange: setPhase,
        onUploadProgress: setUploadProgress,
      });

      const limitedResponse = limitTopCandidates(nextResponse);

      setResponse(limitedResponse);
      setPhase("idle");
      toast.success(
        `${limitedResponse.summary.total_candidates} top candidates ranked for ${limitedResponse.job.job_title}.`,
      );
      void refresh();
    } catch (error) {
      setPhase("idle");
      setUploadProgress(0);

      const message =
        error instanceof ApiRequestError
          ? error.message
          : "Something unexpected happened while analyzing candidates.";

      toast.error(message);
      void refresh();
    }
  }

  return (
    <div className="min-h-screen">
      <header className="sticky top-0 z-30 border-b border-border/50 bg-background/80 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-5 py-4 md:px-7">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-3xl bg-gradient-signal shadow-spotlight">
              <Bot className="h-6 w-6 text-card" />
            </div>
            <div>
              <p className="font-display text-lg font-semibold text-foreground">
                TalentMind AI Resume Ranker
              </p>
              <p className="text-sm text-muted-foreground">
                AI-Powered Intelligent Candidate Discovery Platform
              </p>
            </div>
          </div>

          <div
            className={`rounded-full border px-3 py-1.5 text-xs font-semibold uppercase tracking-[0.16em] ${STATUS_STYLES[status]}`}
            title={backendMessage}
          >
            {status === "online"
              ? "Backend Online"
              : status === "offline"
                ? "Backend Offline"
                : "Checking"}
          </div>
        </div>
      </header>

      <main className="mx-auto flex max-w-7xl flex-col gap-8 px-5 py-10 md:px-7 md:py-12">
        <section className="overflow-hidden rounded-[2rem] border border-border/60 bg-card/78 p-7 shadow-panel backdrop-blur xl:p-9">
          <div className="grid gap-8 xl:grid-cols-[1.1fr_0.9fr] xl:items-end">
            <div className="space-y-5">
              <div className="inline-flex items-center gap-2 rounded-full border border-brand-cyan/20 bg-brand-cyan/10 px-3 py-1.5 text-xs font-semibold uppercase tracking-[0.18em] text-brand-cyan">
                <Sparkles className="h-3.5 w-3.5" />
                Intelligent Candidate Discovery
              </div>
              <div className="space-y-4">
                <h1 className="max-w-4xl font-display text-4xl font-semibold leading-tight text-foreground md:text-5xl">
                  Turn recruiter briefs and candidate datasets into ranked hiring intelligence.
                </h1>
                <p className="max-w-3xl text-base leading-7 text-muted-foreground">
                  Paste the role description, upload a structured candidate file, and let TalentMind
                  surface the strongest matches with AI reasoning, strengths, weaknesses, and
                  missing skill gaps in one pass.
                </p>
              </div>
            </div>

            <div className="rounded-[1.7rem] border border-border/60 bg-background/60 p-5">
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                Recruiter Workflow
              </p>
              <ul className="mt-4 space-y-3 text-sm text-muted-foreground">
                <li>1. Paste the role brief and required skills.</li>
                <li>2. Upload JSONL, JSON, CSV, or XLSX candidate data.</li>
                <li>3. Review the top 100 ranked candidates with expandable insights.</li>
              </ul>
              <button
                type="button"
                onClick={() => void refresh()}
                className="mt-5 inline-flex items-center gap-2 text-sm font-medium text-brand-cyan transition hover:text-foreground"
              >
                <RefreshCcw className="h-4 w-4" />
                Refresh backend status
              </button>
            </div>
          </div>
        </section>

        <section className="grid gap-6 xl:grid-cols-2">
          <JobDescriptionPanel
            characterCount={jobDescription.length}
            error={jobError}
            isBusy={isBusy}
            value={jobDescription}
            onChange={setJobDescription}
          />

          <FileUploadPanel
            error={fileError}
            file={selectedFile}
            isBusy={isBusy}
            phase={phase}
            uploadProgress={uploadProgress}
            onClearFile={() => {
              setSelectedFile(null);
              setFileError(null);
            }}
            onFileSelect={handleFileSelect}
          />
        </section>

        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <p className="text-sm text-muted-foreground">{backendMessage}</p>
          <Button
            type="button"
            size="lg"
            disabled={isBusy}
            onClick={handleAnalyze}
            className="h-12 rounded-full bg-gradient-signal px-6 text-sm font-semibold text-card shadow-spotlight transition hover:opacity-95"
          >
            {isBusy ? "Analyzing Candidates..." : "Analyze & Rank Candidates"}
          </Button>
        </div>

        {isBusy ? (
          <LoadingPanel phase={phase} uploadProgress={uploadProgress} />
        ) : null}

        <ResultsPanel response={response} />
      </main>
    </div>
  );
}
