/*
 * Copyright (c) Flashoffer Developers
 * Released under the MIT license.
 */

export {
  FlashofferThemeProvider,
  createFlashofferTheme,
  createSpaciousTypographyTheme,
  createSunriseGlowTheme,
  createMidnightPulseTheme,
  createOceanBreezeTheme,
  createForestCanopyTheme,
  createMonochromeFocusTheme
} from "./theme/FlashofferThemeProvider";
export type { FlashofferThemePreset } from "./theme/FlashofferThemeProvider";
export type { FlashofferThemeProviderProps } from "./theme/FlashofferThemeProvider";

export { PrimaryCtaButton } from "./components/PrimaryCtaButton";
export type { PrimaryCtaButtonProps } from "./components/PrimaryCtaButton";

export { OutlineCtaButton } from "./components/OutlineCtaButton";
export type { OutlineCtaButtonProps } from "./components/OutlineCtaButton";

export { HeroBanner } from "./components/HeroBanner";
export type { HeroBannerProps } from "./components/HeroBanner";

export { SectionHeader } from "./components/SectionHeader";
export type { SectionHeaderProps } from "./components/SectionHeader";

export { Section } from "./components/Section";
export type { SectionProps } from "./components/Section";

export { LoginView } from "./components/LoginView";
export type { LoginViewProps, LoginCredentials } from "./components/LoginView";

export { PreviewCard } from "./components/PreviewCard";
export type { PreviewCardProps } from "./components/PreviewCard";

export { MultipleChoiceQuiz } from "./components/MultipleChoiceQuiz";
export type {
  MultipleChoiceAnswer,
  MultipleChoiceOption,
  MultipleChoiceQuizProps,
  QuizConfettiOptions,
  QuizConfettiPreset
} from "./components/MultipleChoiceQuiz";

export { CountdownTimer } from "./components/CountdownTimer";
export type { CountdownTimerProps } from "./components/CountdownTimer";

export { InstagramEngagementSection } from "./components/InstagramEngagementSection";
export type { InstagramEngagementSectionProps } from "./components/InstagramEngagementSection";

export { Footer } from "./components/Footer";
export type { FooterProps, FooterLink } from "./components/Footer";

export { Figure } from "./components/Figure";
export type { FigureProps } from "./components/Figure";

export {
  AutoTrack,
  EngagementProvider,
  EventConsole,
  logQuizCompletion,
  useEngagement,
  useRecordInteraction,
  useViewTracker,
  ViewTracker,
} from "./analytics";
export type {
  AutoTrackProps,
  EngagementContextValue,
  EngagementEvent,
  EngagementProviderProps,
  EventConsoleProps,
  QuizAnalyticsOptions,
  QuizCompletionPayload,
  ViewTrackerProps,
} from "./analytics";
