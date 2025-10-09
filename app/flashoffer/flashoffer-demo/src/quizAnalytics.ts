/*
 * Copyright (c) Flashoffer Developers
 * Released under the MIT license.
 */

const QUIZ_EVENTS_ENDPOINT =
  typeof import.meta.env.VITE_FLASHOFFER_QUIZ_EVENTS_ENDPOINT === "string" &&
  import.meta.env.VITE_FLASHOFFER_QUIZ_EVENTS_ENDPOINT.trim() !== ""
    ? import.meta.env.VITE_FLASHOFFER_QUIZ_EVENTS_ENDPOINT
    : undefined;

const QUIZ_ID = "flashoffer-demo.best-follow-up";
const USER_STORAGE_KEY = "flashoffer-demo:quiz-user-id";

let cachedUserId: string | null = null;

function generateUserId(): string {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  const random = Math.random().toString(16).slice(2, 10);
  return `${Date.now().toString(16)}-${random}`;
}

function readStoredUserId(): string | null {
  if (typeof window === "undefined") {
    return null;
  }
  try {
    const stored = window.sessionStorage.getItem(USER_STORAGE_KEY);
    return stored && stored.trim() !== "" ? stored : null;
  } catch (error) {
    console.warn("Unable to access sessionStorage for quiz analytics", error);
    return null;
  }
}

function writeStoredUserId(userId: string): void {
  if (typeof window === "undefined") {
    return;
  }
  try {
    window.sessionStorage.setItem(USER_STORAGE_KEY, userId);
  } catch (error) {
    console.warn("Unable to persist quiz analytics user identifier", error);
  }
}

function resolveUserId(): string {
  if (cachedUserId) {
    return cachedUserId;
  }
  const stored = readStoredUserId();
  if (stored) {
    cachedUserId = stored;
    return cachedUserId;
  }
  cachedUserId = generateUserId();
  writeStoredUserId(cachedUserId);
  return cachedUserId;
}

export interface QuizCompletionPayload {
  selectedOptionId: string;
  correctOptionId?: string;
  isCorrect?: boolean;
  question: string;
  attempt: number;
}

export async function logQuizCompletion(
  payload: QuizCompletionPayload
): Promise<void> {
  if (!QUIZ_EVENTS_ENDPOINT) {
    return;
  }
  if (typeof fetch !== "function") {
    return;
  }

  const body = {
    quiz_id: QUIZ_ID,
    user_id: resolveUserId(),
    event_type: "complete",
    passed: Boolean(payload.isCorrect),
    metadata: {
      question: payload.question,
      selected_option_id: payload.selectedOptionId,
      correct_option_id: payload.correctOptionId,
      attempt: payload.attempt,
    },
    occurred_at: new Date().toISOString(),
  };

  try {
    await fetch(QUIZ_EVENTS_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      keepalive: true,
      credentials: "include",
    });
  } catch (error) {
    console.warn("Failed to log quiz completion", error);
  }
}

