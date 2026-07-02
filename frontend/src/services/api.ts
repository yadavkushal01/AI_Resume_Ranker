import type {
  AnalysisPhase,
  BackendStatus,
  RankResponse,
} from "@/types/ranking";

const API_URL = (import.meta.env.VITE_API_URL || "http://127.0.0.1:8000").replace(/\/$/, "");
const DEFAULT_TIMEOUT_MS = Number(import.meta.env.VITE_RANK_TIMEOUT_MS || 900_000);

export class ApiRequestError extends Error {
  constructor(
    message: string,
    readonly code: "http" | "network" | "timeout" | "invalid_response",
    readonly status?: number,
  ) {
    super(message);
    this.name = "ApiRequestError";
  }
}

type RankCandidatesOptions = {
  onPhaseChange?: (phase: AnalysisPhase) => void;
  onUploadProgress?: (progress: number) => void;
  timeoutMs?: number;
};

function parseErrorDetail(responseText: string): string | undefined {
  if (!responseText) {
    return undefined;
  }

  try {
    const payload = JSON.parse(responseText) as { detail?: string };
    return payload.detail;
  } catch {
    return undefined;
  }
}

export async function checkBackend(): Promise<BackendStatus> {
  const response = await fetch(`${API_URL}/`, {
    headers: { Accept: "application/json" },
  });

  if (!response.ok) {
    throw new ApiRequestError(
      `Backend health check failed with status ${response.status}.`,
      "http",
      response.status,
    );
  }

  const payload = (await response.json()) as BackendStatus;

  if (!payload || typeof payload.message !== "string") {
    throw new ApiRequestError(
      "Backend health check returned an invalid response.",
      "invalid_response",
    );
  }

  return payload;
}

function parseRankResponse(payload: unknown): RankResponse {
  if (
    !payload ||
    typeof payload !== "object" ||
    !Array.isArray((payload as RankResponse).candidates)
  ) {
    throw new ApiRequestError(
      "The backend returned an empty or unexpected ranking response.",
      "invalid_response",
    );
  }

  return payload as RankResponse;
}


export function rankCandidates(
  jobDescription: string,
  file: File | null | undefined,
  options: RankCandidatesOptions = {},
): Promise<RankResponse> {
  return new Promise((resolve, reject) => {
    const formData = new FormData();
    formData.append("job_description", jobDescription);

    if (file) {
      formData.append("file", file);
    }

    const request = new XMLHttpRequest();
    const timeoutMs = options.timeoutMs ?? DEFAULT_TIMEOUT_MS;

    request.open("POST", `${API_URL}/rank`);
    request.timeout = timeoutMs;
    request.responseType = "text";

    if (file) {
      options.onPhaseChange?.("uploading");
      options.onUploadProgress?.(0);

      request.upload.onprogress = (event) => {
        if (!event.lengthComputable) {
          return;
        }

        options.onUploadProgress?.(Math.round((event.loaded / event.total) * 100));
      };

      request.upload.onload = () => {
        options.onUploadProgress?.(100);
        options.onPhaseChange?.("processing");
      };
    } else {
      options.onPhaseChange?.("processing");
      options.onUploadProgress?.(100);
    }

    request.onerror = () => {
      reject(
        new ApiRequestError(
          "Unable to reach the backend. Confirm the FastAPI server is running.",
          "network",
        ),
      );
    };

    request.ontimeout = () => {
      reject(
        new ApiRequestError(
          "The ranking request timed out while the backend was processing the dataset. Increase VITE_RANK_TIMEOUT_MS if your datasets are very large.",
          "timeout",
        ),
      );
    };

    request.onload = () => {
      if (request.status < 200 || request.status >= 300) {
        reject(
          new ApiRequestError(
            parseErrorDetail(request.responseText) ||
              `Backend request failed with status ${request.status}.`,
            "http",
            request.status,
          ),
        );
        return;
      }

      let payload: RankResponse;

      try {
        payload = parseRankResponse(JSON.parse(request.responseText) as RankResponse);
      } catch (error) {
        if (error instanceof ApiRequestError) {
          reject(error);
          return;
        }

        reject(
          new ApiRequestError("The backend returned an invalid JSON response.", "invalid_response"),
        );
        return;
      }

      resolve(payload);
    };

    request.send(formData);
  });
}
