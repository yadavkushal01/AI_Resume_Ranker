export function formatFileSize(bytes: number): string {
  if (bytes < 1024) {
    return `${bytes} B`;
  }

  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`;
  }

  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function formatExperience(years: number): string {
  if (!years) {
    return "0 yrs";
  }

  const rounded = years >= 10 ? years.toFixed(0) : years.toFixed(1);
  return `${rounded.replace(/\.0$/, "")} yrs`;
}

export function formatAnalysisTimestamp(value: string): string {
  const parsed = new Date(value);

  if (Number.isNaN(parsed.getTime())) {
    return "Just now";
  }

  return parsed.toLocaleString();
}
