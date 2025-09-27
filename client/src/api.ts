const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export type CopilotRequest = {
  prompt: string;
  intent: string;
};

export type CopilotResponse = {
  message?: string;
};

export async function fetchJson<T>(path: string, init?: RequestInit) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {})
    },
    ...init
  });

  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }

  return (await response.json()) as T;
}

export function inferTabIntent(input: string): string {
  const text = input.toLowerCase();
  if (text.includes("plan")) return "plan";
  if (text.includes("compliance") || text.includes("control")) return "compliance";
  if (text.includes("narrative") || text.includes("story")) return "narratives";
  return "copilot";
}

export async function postCopilotPrompt(body: CopilotRequest) {
  try {
    return await fetchJson<CopilotResponse>("/copilot", {
      method: "POST",
      body: JSON.stringify(body)
    });
  } catch (error) {
    console.error(error);
    return { message: "Unable to reach Copilot service." };
  }
}
