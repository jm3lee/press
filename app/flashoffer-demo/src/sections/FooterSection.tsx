import Box from "@mui/material/Box";
import Stack from "@mui/material/Stack";
import { Footer, Section } from "flashoffer-react";

const FOOTER_LINKS = [
  { label: "Docs", href: "https://example.com/docs" },
  { label: "Status", href: "https://status.example.com" },
  { label: "Support", href: "mailto:support@example.com" }
];

export function FooterSection() {
  return (
    <Box
      component="section"
      data-track-id="footer"
      data-track-label="Footer"
      data-track-meta={JSON.stringify({ links: FOOTER_LINKS.length })}
    >
      <Stack spacing={3}>
        <Section
          eyebrow="FOOTER"
          title="Close with a helpful footer"
          description="Surface documentation, status pages, and support channels without writing bespoke markup."
          paragraphs={[]}
        />
        <Footer
          links={FOOTER_LINKS}
          copyrightText="© 2025 Flashoffer. All rights reserved."
        />
      </Stack>
    </Box>
  );
}

export { FOOTER_LINKS };
