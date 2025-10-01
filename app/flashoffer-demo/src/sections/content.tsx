export const OVERVIEW_PARAGRAPHS = [
  "Use the Section component to pair launch announcements, feature guides, or changelog summaries with consistent typography.",
  "Each paragraph is wrapped in semantic markup and inherits spacing from the Flashoffer design tokens, so marketing teams can focus on messaging."
];

export const PREVIEW_CARDS = [
  {
    title: "Personalized launch offers",
    description:
      "Highlight tailored bundles that can be activated in a few clicks. Swap copy and imagery to match your latest campaign without rebuilding layouts.",
    media: (
      <img
        src="https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&fit=crop&w=480&q=80"
        alt="Two teammates collaborating over a laptop"
        style={{ width: "100%", borderRadius: "16px" }}
      />
    )
  },
  {
    title: "Lifecycle automation",
    description:
      "Pair Flashoffer pages with your automation stack to trigger discounts or add-ons in response to usage signals.",
    media: (
      <img
        src="https://images.unsplash.com/photo-1527430253228-e93688616381?auto=format&fit=crop&w=480&q=80"
        alt="Abstract dashboard charts"
        style={{ width: "100%", borderRadius: "16px" }}
      />
    ),
    secondaryCta: {
      label: "View playbook",
      href: "https://example.com/playbook"
    }
  },
  {
    title: "Localized experiences",
    description:
      "Clone the same structure across regions while tuning content, pricing, and compliance disclosures in minutes.",
    media: (
      <img
        src="https://images.unsplash.com/photo-1527430253228-e93688616381?auto=format&fit=crop&w=480&q=80"
        alt="Abstract dashboard charts"
        style={{ width: "100%", borderRadius: "16px" }}
      />
    ),
    primaryCta: {
      label: "See localization tips",
      href: "https://example.com/localization"
    }
  }
];
