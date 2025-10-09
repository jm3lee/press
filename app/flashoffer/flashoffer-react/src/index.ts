/*
 * Copyright (c) Flashoffer Developers
 * Released under the MIT license.
 */

export {
  FlashofferThemeProvider,
  createFlashofferTheme,
  createSpaciousTypographyTheme
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

export { PreviewCard } from "./components/PreviewCard";
export type { PreviewCardProps } from "./components/PreviewCard";

export { MultipleChoiceQuiz } from "./components/MultipleChoiceQuiz";
export type {
  MultipleChoiceAnswer,
  MultipleChoiceOption,
  MultipleChoiceQuizProps
} from "./components/MultipleChoiceQuiz";

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
  ViewTrackerProps,
} from "./analytics";
