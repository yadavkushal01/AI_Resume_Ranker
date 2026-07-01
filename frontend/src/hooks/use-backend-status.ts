import { useCallback, useEffect, useState } from "react";

import { checkBackend } from "@/services/api";
import type { BackendConnectionState } from "@/types/ranking";

type BackendStatusSnapshot = {
  message: string;
  status: BackendConnectionState;
};

export function useBackendStatus() {
  const [snapshot, setSnapshot] = useState<BackendStatusSnapshot>({
    message: "Checking backend connection...",
    status: "checking",
  });

  const refresh = useCallback(async () => {
    try {
      const response = await checkBackend();
      setSnapshot({
        message: response.message,
        status: "online",
      });
    } catch {
      setSnapshot({
        message: "Backend offline. Start the FastAPI server to analyze candidates.",
        status: "offline",
      });
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  return {
    message: snapshot.message,
    refresh,
    status: snapshot.status,
  };
}
