/*
 * Copyright (c) Flashoffer Developers
 * Released under the MIT license.
 */

import type { QuizAnalyticsOptions, QuizCompletionPayload } from "../QuizAnalytics";

describe("logQuizCompletion", () => {
  const globalScope = globalThis as typeof globalThis & {
    fetch?: typeof fetch;
    crypto?: { randomUUID?: () => string };
  };
  const originalFetch = globalScope.fetch;
  const originalCrypto = globalScope.crypto;

  let warnSpy: jest.SpyInstance;

  const basePayload: QuizCompletionPayload = {
    selectedOptionId: "opt-1",
    correctOptionId: "opt-2",
    isCorrect: true,
    question: "Who is the Flashoffer mascot?",
    attempt: 1,
  };

  const baseOptions: QuizAnalyticsOptions = {
    quizId: "quiz-1",
  };

  beforeEach(() => {
    jest.resetModules();
    warnSpy = jest.spyOn(console, "warn").mockImplementation(() => {});
  });

  afterEach(() => {
    if (originalFetch === undefined) {
      delete globalScope.fetch;
    } else {
      globalScope.fetch = originalFetch;
    }

    if (originalCrypto === undefined) {
      delete globalScope.crypto;
    } else {
      globalScope.crypto = originalCrypto;
    }

    warnSpy.mockRestore();
    jest.restoreAllMocks();
    jest.clearAllMocks();
  });

  it("returns early when the endpoint is not provided", async () => {
    const fetchMock = jest.fn();
    globalScope.fetch = fetchMock;

    const { logQuizCompletion } = await import("../QuizAnalytics");

    await logQuizCompletion(basePayload, baseOptions);

    expect(fetchMock).not.toHaveBeenCalled();
    expect(warnSpy).not.toHaveBeenCalled();
  });

  it("returns early when fetch is not available", async () => {
    delete globalScope.fetch;

    const { logQuizCompletion } = await import("../QuizAnalytics");

    await expect(
      logQuizCompletion(basePayload, { ...baseOptions, endpoint: "https://api.flashoffer.dev" })
    ).resolves.toBeUndefined();

    expect(warnSpy).not.toHaveBeenCalled();
  });

  it("sends analytics payload with a generated session identifier when the user id is blank", async () => {
    const fetchMock = jest.fn().mockResolvedValue({ ok: true });
    globalScope.fetch = fetchMock;
    delete globalScope.crypto;

    const fixedTimestamp = 1_700_000_000_000;
    const randomValue = 0.3141592653;
    jest.spyOn(Date, "now").mockReturnValue(fixedTimestamp);
    jest.spyOn(Math, "random").mockReturnValue(randomValue);

    const { logQuizCompletion } = await import("../QuizAnalytics");

    await logQuizCompletion(basePayload, {
      ...baseOptions,
      endpoint: "https://api.flashoffer.dev",
      userId: "   ",
    });

    expect(fetchMock).toHaveBeenCalledTimes(1);
    const [, requestInit] = fetchMock.mock.calls[0] as [string, { body?: BodyInit | null; method?: string; headers?: HeadersInit }];
    expect(requestInit?.method).toBe("POST");
    expect(requestInit?.headers).toEqual({ "Content-Type": "application/json" });

    const body = JSON.parse(String(requestInit?.body));
    const expectedRandomFragment = randomValue.toString(16).slice(2, 10);
    const expectedUserId = `${fixedTimestamp.toString(16)}-${expectedRandomFragment}`;

    expect(body.quiz_id).toBe(baseOptions.quizId);
    expect(body.user_id).toBe(expectedUserId);
    expect(body.metadata).toEqual({
      question: basePayload.question,
      selected_option_id: basePayload.selectedOptionId,
      correct_option_id: basePayload.correctOptionId,
      attempt: basePayload.attempt,
    });
    expect(body).not.toHaveProperty("campaign_id");
  });

  it("prefers a provided user id over the generated session id", async () => {
    const fetchMock = jest.fn().mockResolvedValue({ ok: true });
    globalScope.fetch = fetchMock;

    const { logQuizCompletion } = await import("../QuizAnalytics");

    await logQuizCompletion(basePayload, {
      ...baseOptions,
      endpoint: "https://api.flashoffer.dev",
      userId: "user-123",
    });

    expect(fetchMock).toHaveBeenCalledTimes(1);
    const body = JSON.parse(String(fetchMock.mock.calls[0][1]?.body));
    expect(body.user_id).toBe("user-123");
  });

  it("includes the campaign identifier when provided", async () => {
    const fetchMock = jest.fn().mockResolvedValue({ ok: true });
    globalScope.fetch = fetchMock;

    const { logQuizCompletion } = await import("../QuizAnalytics");

    await logQuizCompletion(
      { ...basePayload, campaignId: "cmp-42" },
      {
        ...baseOptions,
        endpoint: "https://api.flashoffer.dev",
      }
    );

    expect(fetchMock).toHaveBeenCalledTimes(1);
    const body = JSON.parse(String(fetchMock.mock.calls[0][1]?.body));
    expect(body.campaign_id).toBe("cmp-42");
  });

  it("uses crypto.randomUUID when available to seed the session id", async () => {
    const fetchMock = jest.fn().mockResolvedValue({ ok: true });
    globalScope.fetch = fetchMock;
    const randomUUID = jest.fn().mockReturnValue("uuid-1234");
    globalScope.crypto = { randomUUID };

    const { logQuizCompletion } = await import("../QuizAnalytics");

    await logQuizCompletion(basePayload, {
      ...baseOptions,
      endpoint: "https://api.flashoffer.dev",
    });

    expect(randomUUID).toHaveBeenCalledTimes(1);
    const body = JSON.parse(String(fetchMock.mock.calls[0][1]?.body));
    expect(body.user_id).toBe("uuid-1234");
  });

  it("logs a warning when the analytics request fails", async () => {
    const fetchMock = jest.fn().mockRejectedValue(new Error("network failure"));
    globalScope.fetch = fetchMock;

    const { logQuizCompletion } = await import("../QuizAnalytics");

    await logQuizCompletion(basePayload, {
      ...baseOptions,
      endpoint: "https://api.flashoffer.dev",
    });

    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(warnSpy).toHaveBeenCalledWith(
      "Failed to log quiz completion",
      expect.any(Error)
    );
  });
});
