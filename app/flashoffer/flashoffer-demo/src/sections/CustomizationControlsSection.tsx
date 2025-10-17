/*
 * Copyright (c) Flashoffer Developers
 * Released under the MIT license.
 */

import Box from "@mui/material/Box";
import Divider from "@mui/material/Divider";
import FormControl from "@mui/material/FormControl";
import MenuItem from "@mui/material/MenuItem";
import Paper from "@mui/material/Paper";
import Select from "@mui/material/Select";
import type { SelectChangeEvent } from "@mui/material/Select";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { Section } from "flashoffer-react";
import type { HeroAlignment } from "./types";

export interface CustomizationControlsSectionProps {
  heroAlignment: HeroAlignment;
  onHeroAlignmentChange: (nextAlignment: HeroAlignment) => void;
  controlsMeta: string;
}

export function CustomizationControlsSection({
  heroAlignment,
  onHeroAlignmentChange,
  controlsMeta
}: CustomizationControlsSectionProps) {
  return (
    <Paper
      elevation={0}
      sx={{ p: { xs: 3, md: 4 } }}
      data-track-id="customization-panel"
      data-track-label="Customization controls"
      data-track-meta={controlsMeta}
    >
      <Stack spacing={3}>
        <Section
          align="left"
          eyebrow="CUSTOMIZE"
          title="Customize the showcase"
        >
          <Typography color="text.secondary">
            Switch palettes or tweak hero alignment to preview how Flashoffer
            primitives adapt.
          </Typography>
        </Section>
        <Divider flexItem sx={{ borderColor: "divider" }} />
        <Box maxWidth={280}>
          <Typography variant="overline" color="text.secondary">
            Hero alignment
          </Typography>
          <FormControl fullWidth sx={{ mt: 1.5 }}>
            <Select
              value={heroAlignment}
              onChange={(event: SelectChangeEvent<HeroAlignment>) => {
                const nextAlignment = event.target.value as HeroAlignment;
                onHeroAlignmentChange(nextAlignment);
              }}
              inputProps={{ "aria-label": "Select hero alignment" }}
              data-track-id="hero-alignment"
              data-track-label="Hero alignment selector"
              data-track-meta={JSON.stringify({ alignment: heroAlignment })}
            >
              <MenuItem value="center">Centered</MenuItem>
              <MenuItem value="left">Left aligned</MenuItem>
            </Select>
          </FormControl>
        </Box>
      </Stack>
    </Paper>
  );
}
