import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import { Figure, Section } from "flashoffer-react";

const FIGURE_META = JSON.stringify({ orientation: "landscape" });

export function FigureSpotlightSection() {
  return (
    <Box
      component="section"
      data-track-id="figure-section"
      data-track-label="Figure component"
      data-track-meta={FIGURE_META}
    >
      <Section
        eyebrow="MEDIA"
        title="Pair imagery with supporting context"
      >
        <Typography color="text.secondary">
          Use Figure to keep visuals responsive across breakpoints while pairing
          them with captions or attributions.
        </Typography>
        <Box
          sx={{
            display: "flex",
            justifyContent: "center",
            width: "100%"
          }}
        >
          <Figure
            src="https://images.unsplash.com/photo-1489515217757-5fd1be406fef?auto=format&fit=crop&w=960&q=80"
            alt="Product marketer reviewing launch campaign timelines"
            caption="Launch dashboards stay legible on any device thanks to responsive scaling."
            sx={{
              maxWidth: 560
            }}
          />
        </Box>
      </Section>
    </Box>
  );
}

export { FIGURE_META };
