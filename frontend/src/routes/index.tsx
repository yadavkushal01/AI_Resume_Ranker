import { createFileRoute } from "@tanstack/react-router";

import { ResumeRankerPage } from "@/components/dashboard/resume-ranker-page";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "TalentMind AI Resume Ranker" },
      {
        name: "description",
        content:
          "AI-powered candidate ranking for structured recruiter datasets and job descriptions.",
      },
      { property: "og:title", content: "TalentMind AI Resume Ranker" },
      {
        property: "og:description",
        content:
          "Analyze candidate datasets, rank applicants, and review strengths, weaknesses, and skill gaps.",
      },
    ],
  }),
  component: ResumeRankerPage,
});
