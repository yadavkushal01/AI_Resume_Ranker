import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Badge } from "@/components/ui/badge";
import type { RankResponse } from "@/types/ranking";
import { formatAnalysisTimestamp, formatExperience } from "@/utils/format";
import { BookOpen, BriefcaseBusiness, CircleAlert, Medal, Sparkles, Target } from "lucide-react";

type ResultsPanelProps = {
  response: RankResponse | null;
};

function ScoreBar({ score }: { score: number }) {
  return (
    <div className="w-full space-y-2">
      <div className="flex items-center justify-between text-xs uppercase tracking-[0.14em] text-muted-foreground">
        <span>Match Score</span>
        <span>{score}%</span>
      </div>
      <div className="h-2 rounded-full bg-border/70">
        <div
          className="h-full rounded-full bg-gradient-signal transition-[width] duration-700 ease-out"
          style={{ width: `${Math.min(score, 100)}%` }}
        />
      </div>
    </div>
  );
}

function DetailList({ items, tone }: { items: string[]; tone: "success" | "warning" | "neutral" }) {
  if (items.length === 0) {
    return <p className="text-sm text-muted-foreground">No additional signals available.</p>;
  }

  const toneClass =
    tone === "success"
      ? "border-brand-cyan/25 bg-brand-cyan/10 text-brand-cyan"
      : tone === "warning"
        ? "border-brand-gold/25 bg-brand-gold/10 text-brand-gold"
        : "border-border/60 bg-background/70 text-foreground";

  return (
    <div className="flex flex-wrap gap-2">
      {items.map((item) => (
        <span
          key={item}
          className={`rounded-full border px-3 py-1 text-xs font-medium ${toneClass}`}
        >
          {item}
        </span>
      ))}
    </div>
  );
}

export function ResultsPanel({ response }: ResultsPanelProps) {
  if (!response) {
    return (
      <section className="rounded-[1.75rem] border border-dashed border-border/70 bg-card/55 p-8 text-center shadow-panel backdrop-blur md:p-10">
        <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-3xl bg-background/80 text-brand-cyan shadow-sm">
          <Target className="h-8 w-8" />
        </div>
        <h2 className="mt-4 font-display text-2xl font-semibold text-foreground">
          Ranking results will appear here
        </h2>
        <p className="mt-2 text-sm text-muted-foreground">
          Add a job description, upload a supported dataset, and run the analysis to see ranked
          candidate cards with strengths, weaknesses, and missing skills.
        </p>
      </section>
    );
  }

  const topCandidate = response.candidates[0];

  return (
    <section className="space-y-5">
      <div className="rounded-[1.75rem] border border-border/70 bg-card/88 p-6 shadow-panel backdrop-blur md:p-7">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <Badge className="rounded-full bg-brand-ink px-3 py-1 text-brand-cyan hover:bg-brand-ink">
                {response.job.job_title}
              </Badge>
              <Badge
                variant="secondary"
                className="rounded-full bg-background/80 px-3 py-1 text-muted-foreground"
              >
                {response.summary.total_candidates} candidates analyzed
              </Badge>
            </div>
            <h2 className="mt-4 font-display text-2xl font-semibold text-foreground">
              TalentMind Ranking Results
            </h2>
            <p className="mt-2 text-sm text-muted-foreground">
              Source file: {response.summary.source_file} · Analyzed{" "}
              {formatAnalysisTimestamp(response.summary.analyzed_at)}
            </p>
          </div>

          {topCandidate ? (
            <div className="rounded-[1.4rem] border border-brand-cyan/25 bg-brand-cyan/10 px-5 py-4 text-right">
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-brand-cyan">
                Top Match
              </p>
              <p className="mt-1 font-display text-2xl font-semibold text-foreground">
                {topCandidate.candidate_name}
              </p>
              <p className="mt-1 text-sm text-muted-foreground">{topCandidate.match_score}% fit</p>
            </div>
          ) : null}
        </div>
      </div>

      <Accordion type="single" collapsible className="space-y-4">
        {response.candidates.map((candidate) => (
          <AccordionItem
            key={candidate.candidate_id}
            value={candidate.candidate_id}
            className="overflow-hidden rounded-[1.75rem] border border-border/70 bg-card/88 px-0 shadow-panel backdrop-blur"
          >
            <AccordionTrigger className="px-6 py-5 no-underline hover:no-underline md:px-7">
              <div className="grid w-full gap-5 text-left md:grid-cols-[auto_minmax(0,1fr)_260px] md:items-center">
                <div className="flex items-center gap-3">
                  <div className="inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-signal text-sm font-bold text-card shadow-spotlight">
                    #{candidate.rank}
                  </div>
                  <div>
                    <p className="font-display text-lg font-semibold text-foreground">
                      {candidate.candidate_name}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      {candidate.current_title || "Candidate"}{" "}
                      {candidate.current_company ? `at ${candidate.current_company}` : ""}
                    </p>
                  </div>
                </div>

                <div className="space-y-3">
                  <p className="line-clamp-2 text-sm text-muted-foreground">{candidate.reason}</p>
                  <div className="flex flex-wrap gap-2">
                    {candidate.skills.slice(0, 4).map((skill) => (
                      <Badge
                        key={skill}
                        variant="secondary"
                        className="rounded-full bg-background/80 px-3 py-1 text-foreground"
                      >
                        {skill}
                      </Badge>
                    ))}
                  </div>
                </div>

                <div className="space-y-3">
                  <ScoreBar score={candidate.match_score} />
                  <div className="flex flex-wrap items-center gap-3 text-sm text-muted-foreground">
                    <span className="inline-flex items-center gap-2">
                      <BriefcaseBusiness className="h-4 w-4 text-brand-cyan" />
                      {formatExperience(candidate.experience_years)}
                    </span>
                    <span className="inline-flex items-center gap-2">
                      <Medal className="h-4 w-4 text-brand-gold" />
                      {candidate.recommendation}
                    </span>
                  </div>
                </div>
              </div>
            </AccordionTrigger>

            <AccordionContent className="px-6 pb-6 md:px-7">
              <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                <div className="rounded-[1.3rem] border border-border/60 bg-background/60 p-4">
                  <div className="mb-3 flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.16em] text-muted-foreground">
                    <Sparkles className="h-4 w-4 text-brand-cyan" />
                    Strengths
                  </div>
                  <DetailList items={candidate.strengths} tone="success" />
                </div>

                <div className="rounded-[1.3rem] border border-border/60 bg-background/60 p-4">
                  <div className="mb-3 flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.16em] text-muted-foreground">
                    <CircleAlert className="h-4 w-4 text-brand-gold" />
                    Weaknesses
                  </div>
                  <DetailList items={candidate.weaknesses} tone="warning" />
                </div>

                <div className="rounded-[1.3rem] border border-border/60 bg-background/60 p-4">
                  <div className="mb-3 flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.16em] text-muted-foreground">
                    <Target className="h-4 w-4 text-brand-cyan" />
                    Missing Skills
                  </div>
                  <DetailList items={candidate.missing_skills} tone="warning" />
                </div>

                <div className="rounded-[1.3rem] border border-border/60 bg-background/60 p-4">
                  <div className="mb-3 flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.16em] text-muted-foreground">
                    <BookOpen className="h-4 w-4 text-brand-cyan" />
                    Education
                  </div>
                  <ul className="space-y-2 text-sm text-muted-foreground">
                    {candidate.education.length > 0 ? (
                      candidate.education.map((entry) => <li key={entry}>{entry}</li>)
                    ) : (
                      <li>No education details supplied in the dataset.</li>
                    )}
                  </ul>
                </div>
              </div>

              <div className="mt-4 grid gap-4 xl:grid-cols-[1.1fr_0.9fr]">
                <div className="rounded-[1.3rem] border border-border/60 bg-background/60 p-4">
                  <div className="mb-3 flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.16em] text-muted-foreground">
                    <BriefcaseBusiness className="h-4 w-4 text-brand-cyan" />
                    Recent Projects
                  </div>
                  <ul className="space-y-3 text-sm text-muted-foreground">
                    {candidate.projects.length > 0 ? (
                      candidate.projects.map((project) => <li key={project}>{project}</li>)
                    ) : (
                      <li>No recent project summaries were available in the dataset.</li>
                    )}
                  </ul>
                </div>

                <div className="rounded-[1.3rem] border border-border/60 bg-background/60 p-4">
                  <div className="mb-3 flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.16em] text-muted-foreground">
                    <Sparkles className="h-4 w-4 text-brand-gold" />
                    Alignment Signals
                  </div>
                  <div className="space-y-4">
                    <div>
                      <p className="mb-2 text-xs font-semibold uppercase tracking-[0.16em] text-muted-foreground">
                        Matched Required Skills
                      </p>
                      <DetailList items={candidate.matched_required_skills} tone="success" />
                    </div>
                    <div>
                      <p className="mb-2 text-xs font-semibold uppercase tracking-[0.16em] text-muted-foreground">
                        Matched Preferred Skills
                      </p>
                      <DetailList items={candidate.matched_preferred_skills} tone="neutral" />
                    </div>
                  </div>
                </div>
              </div>
            </AccordionContent>
          </AccordionItem>
        ))}
      </Accordion>
    </section>
  );
}
