import { API_BASE_URL } from "@/lib/constants";
import type { ApiErrorBody } from "@/types/chat";

/**
 * Raised for any non-2xx HTTP response from the backend. Carries the HTTP
 * status so callers (hooks) can branch on 429 / 502 / 503 without string
 * matching on the message.
 */
export class ApiError extends Error {
  readonly status: number;
  readonly code?: string;

  constructor(message: string, status: number, code?: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
  }
}

/**
 * Raised when the request never got an HTTP response at all -- DNS
 * failure, refused connection, CORS block, or a client-side timeout.
 * Distinct from ApiError because there is no status code to branch on;
 * this always means "the backend is unreachable."
 */
export class NetworkError extends Error {
  constructor(message = "Unable to reach the server.") {
    super(message);
    this.name = "NetworkError";
  }
}

interface RequestOptions extends RequestInit {
  /** Abort the request after this many milliseconds. Default 30s. */
  timeoutMs?: number;
}

function isApiErrorBody(value: unknown): value is ApiErrorBody {
  return (
    typeof value === "object" &&
    value !== null &&
    "error" in value &&
    typeof (value as ApiErrorBody).error?.message === "string"
  );
}

async function request<TResponse>(
  path: string,
  options: RequestOptions = {}
): Promise<TResponse> {
  const { timeoutMs = 30_000, ...init } = options;
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...(init.headers ?? {}),
      },
      signal: controller.signal,
    });
  } catch (error) {
    clearTimeout(timeoutId);
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new NetworkError(
        "The request timed out. The server may be slow or unreachable."
      );
    }
    throw new NetworkError();
  }
  clearTimeout(timeoutId);

  if (!response.ok) {
    let message = `Request failed with status ${response.status}.`;
    let code: string | undefined;

    try {
      const body: unknown = await response.json();
      if (isApiErrorBody(body)) {
        message = body.error.message;
        code = body.error.code;
      }
    } catch {
      // Response body wasn't JSON (or was empty) -- keep the default message.
    }

    throw new ApiError(message, response.status, code);
  }

  return (await response.json()) as TResponse;
}

export const apiClient = {
  get: <T>(path: string, options?: RequestOptions) =>
    request<T>(path, { ...options, method: "GET" }),
  post: <T>(path: string, body: unknown, options?: RequestOptions) =>
    request<T>(path, {
      ...options,
      method: "POST",
      body: JSON.stringify(body),
    }),
};
