const SUPPORTED_FILE_EXTENSIONS = [".jsonl", ".json", ".csv", ".xlsx"] as const;
const MAX_FILE_SIZE_MB = 15;

export function getAcceptedFileTypes(): string {
  return SUPPORTED_FILE_EXTENSIONS.join(",");
}

export function getSupportedFileTypesLabel(): string {
  return SUPPORTED_FILE_EXTENSIONS.join(" | ");
}

export function validateCandidateFile(file: File): string | null {
  const extension = file.name.slice(file.name.lastIndexOf(".")).toLowerCase();

  if (
    !SUPPORTED_FILE_EXTENSIONS.includes(extension as (typeof SUPPORTED_FILE_EXTENSIONS)[number])
  ) {
    return "Unsupported dataset format. Upload a JSONL, JSON, CSV, or XLSX file.";
  }

  if (file.size > MAX_FILE_SIZE_MB * 1024 * 1024) {
    return `File is too large. Please upload a dataset smaller than ${MAX_FILE_SIZE_MB} MB.`;
  }

  return null;
}
