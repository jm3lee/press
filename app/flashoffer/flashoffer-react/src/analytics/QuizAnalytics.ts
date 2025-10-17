/*
 * Copyright (c) Flashoffer Developers
 * Released under the MIT license.
 */

function generateUserId(): string {
  if (
    typeof crypto !== "undefined" &&
    typeof crypto.randomUUID === "function"
  ) {
    return crypto.randomUUID();
  }
  const random = Math.random().toString(16).slice(2, 10);
  return `${Date.now().toString(16)}-${random}`;
}

const sessionUserId = generateUserId();

function resolveUserId(explicitUserId?: string): string {
  if (explicitUserId && explicitUserId.trim() !== "") {
    return explicitUserId;
  }
  return sessionUserId;
}

/**
 * Metadata about an answered quiz question to forward to the analytics API.
 */
export interface QuizCompletionPayload {
  selectedOptionId: string;
  correctOptionId?: string;
  isCorrect?: boolean;
  question: string;
  attempt: number;
  campaignId?: string;
}

/**
 * Configuration for sending quiz analytics events to the Flashoffer backend.
 */
export interface QuizAnalyticsOptions {
  endpoint?: string;
  quizId: string;
  /**
   * Override to provide a caller-managed identifier instead of the session id.
   */
  userId?: string;
}

/**
 * Records a quiz completion event for the provided quiz analytics configuration.
 * Generates a fresh session identifier on each page load unless one is supplied.
 *
 * @param payload - Details about the quiz attempt to record.
 * @param options - Analytics configuration, including quiz identifier and endpoint.
 */
export async function logQuizCompletion(
  payload: QuizCompletionPayload,
  options: QuizAnalyticsOptions
): Promise<void> {
  const endpoint = options.endpoint;
  if (!endpoint) {
    return;
  }

  if (typeof fetch !== "function") {
    return;
  }

  const body = {
    quiz_id: options.quizId,
    user_id: resolveUserId(options.userId),
    event_type: "complete",
    passed: Boolean(payload.isCorrect),
    metadata: {
      question: payload.question,
      selected_option_id: payload.selectedOptionId,
      correct_option_id: payload.correctOptionId,
      attempt: payload.attempt,
    },
    occurred_at: new Date().toISOString(),
    ...(payload.campaignId ? { campaign_id: payload.campaignId } : {}),
  };

  try {
    await fetch(endpoint, {
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
