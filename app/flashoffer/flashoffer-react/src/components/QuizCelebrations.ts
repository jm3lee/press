/*
 * Copyright (c) Flashoffer Developers
 * Released under the MIT license.
 */

import type { CreateTypes, Options } from "canvas-confetti";

/**
 * Named presets that determine the appearance of the confetti animation.
 */
export type QuizConfettiPreset = "classic" | "streamers" | "burst";

/**
 * Configuration describing when to play a celebratory confetti animation.
 */
export interface QuizConfettiOptions {
  /** Enables the confetti animation when the learner submits a correct answer. */
  enabled: boolean;
  /** Selects the visual preset to render. Defaults to `"classic"`. */
  preset?: QuizConfettiPreset;
}

interface ConfettiShot {
  options: Options;
  delay?: number;
}

const CONFETTI_PRESETS: Record<QuizConfettiPreset, ConfettiShot[]> = {
  classic: [
    {
      options: {
        particleCount: 140,
        spread: 65,
        startVelocity: 45,
        origin: { y: 0.6 }
      }
    },
    {
      options: {
        particleCount: 90,
        spread: 55,
        startVelocity: 35,
        decay: 0.92,
        origin: { y: 0.6 }
      },
      delay: 120
    }
  ],
  streamers: [
    {
      options: {
        particleCount: 70,
        angle: 60,
        spread: 55,
        startVelocity: 50,
        origin: { x: 0, y: 0.6 }
      }
    },
    {
      options: {
        particleCount: 70,
        angle: 120,
        spread: 55,
        startVelocity: 50,
        origin: { x: 1, y: 0.6 }
      }
    },
    {
      options: {
        particleCount: 60,
        spread: 75,
        startVelocity: 35,
        ticks: 120,
        origin: { x: 0.5, y: 0.45 }
      },
      delay: 180
    }
  ],
  burst: [
    {
      options: {
        particleCount: 200,
        spread: 100,
        startVelocity: 55,
        origin: { x: 0.5, y: 0.6 }
      }
    },
    {
      options: {
        particleCount: 160,
        spread: 120,
        startVelocity: 60,
        decay: 0.9,
        scalar: 1.1,
        origin: { x: 0.5, y: 0.55 }
      },
      delay: 140
    },
    {
      options: {
        particleCount: 180,
        spread: 140,
        startVelocity: 45,
        ticks: 160,
        scalar: 0.9,
        origin: { x: 0.5, y: 0.5 }
      },
      delay: 300
    }
  ]
};

let cachedConfetti: Promise<CreateTypes> | null = null;

async function loadConfettiInstance(): Promise<CreateTypes | null> {
  if (typeof window === "undefined") {
    return null;
  }

  if (!cachedConfetti) {
    cachedConfetti = import("canvas-confetti").then(({ default: confetti }) =>
      confetti.create(undefined, { resize: true, useWorker: true })
    );
  }

  try {
    return await cachedConfetti;
  } catch (error) {
    cachedConfetti = null;
    throw error;
  }
}

function fireConfettiShots(confetti: CreateTypes, shots: ConfettiShot[]): void {
  shots.forEach(({ options, delay }) => {
    if (delay && delay > 0) {
      globalThis.setTimeout(() => {
        void confetti(options);
      }, delay);
      return;
    }
    void confetti(options);
  });
}

/**
 * Resolves author provided configuration into runtime confetti settings.
 */
export function resolveConfettiOptions(
  options?: QuizConfettiOptions
): { enabled: boolean; preset: QuizConfettiPreset } {
  if (!options || options.enabled === false) {
    return { enabled: false, preset: "classic" };
  }

  return { enabled: true, preset: options.preset ?? "classic" };
}

/**
 * Plays the confetti animation for the provided preset.
 */
export async function launchConfetti(preset: QuizConfettiPreset): Promise<void> {
  const confetti = await loadConfettiInstance();
  if (!confetti) {
    return;
  }

  const shots = CONFETTI_PRESETS[preset];
  fireConfettiShots(confetti, shots);
}

