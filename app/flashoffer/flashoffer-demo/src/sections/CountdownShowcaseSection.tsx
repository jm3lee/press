import Box from "@mui/material/Box";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { useMemo } from "react";
import { CountdownTimer, Section } from "flashoffer-react";

export function CountdownShowcaseSection() {
  const earlyAccessEnd = useMemo(
    () => new Date(Date.now() + 1000 * 60 * 60 * 45),
    []
  );
  const restockEnd = useMemo(
    () => new Date(Date.now() + 1000 * 60 * 90),
    []
  );
  const trackMeta = JSON.stringify({ variants: 2 });

  return (
    <Box
      component="section"
      data-track-id="countdown-showcase"
      data-track-label="Countdown timer showcase"
      data-track-meta={trackMeta}
    >
      <Section
        align="center"
        eyebrow="LIMITED-TIME PROMOS"
        title="Drive urgency with countdowns"
      >
        <Typography color="text.secondary">
          CountdownTimer spotlights dwindling inventory and time-sensitive
          campaigns with live updates. Combine bold copy with quantity cues to
          motivate action across flash drops or restock alerts.
        </Typography>
        <Stack
          direction={{ xs: "column", lg: "row" }}
          spacing={3}
          alignItems="stretch"
          justifyContent="center"
        >
          <Box sx={{ width: "100%", maxWidth: 420 }}>
            <CountdownTimer
              endTime={earlyAccessEnd}
              timerLabel="Early access ends in"
              headline="Creator passes are almost gone."
              quantityRemaining={42}
              quantityLabel="Passes left"
            />
          </Box>
          <Box sx={{ width: "100%", maxWidth: 420 }}>
            <CountdownTimer
              endTime={restockEnd}
              timerLabel="Restock drops in"
              headline="Set an alert for the next batch."
            />
          </Box>
        </Stack>
      </Section>
    </Box>
  );
}
