/*
 * Copyright (c) Flashoffer Developers
 * Released under the MIT license.
 */

import Avatar from "@mui/material/Avatar";
import Box from "@mui/material/Box";
import Card from "@mui/material/Card";
import CardActions from "@mui/material/CardActions";
import CardContent from "@mui/material/CardContent";
import CardHeader from "@mui/material/CardHeader";
import IconButton from "@mui/material/IconButton";
import Stack from "@mui/material/Stack";
import SvgIcon from "@mui/material/SvgIcon";
import Typography from "@mui/material/Typography";
import type { SvgIconProps } from "@mui/material/SvgIcon";
import { useMemo, useState } from "react";

import { ViewTracker, useRecordInteraction } from "../analytics";
import { Section } from "./Section";

/**
 * Configuration options for {@link InstagramEngagementSection}.
 */
export interface InstagramEngagementSectionProps {
  /**
   * Instagram handle presented in the demo card header.
   * Defaults to "instagramcreators".
   */
  handle?: string;
  /**
   * Identifier associated with the mocked Instagram post or reel.
   * Defaults to "reels-remix-checklist".
   */
  postId?: string;
  /**
   * Track identifier supplied to the engagement provider for view events.
   * Defaults to "instagram-engagement-card".
   */
  trackId?: string;
  /**
   * Starting number of likes rendered next to the Instagram CTA row.
   * Defaults to 87234 (87.2K likes).
   */
  initialLikes?: number;
  /**
   * Number of saves displayed beside the live like count.
   * Defaults to 4159.
   */
  saves?: number;
}

/**
 * Heart-shaped icon that mirrors Instagram's like control.
 */
function HeartIcon(props: SvgIconProps) {
  return (
    <SvgIcon viewBox="0 0 24 24" {...props}>
      <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" />
    </SvgIcon>
  );
}

/**
 * Upward arrow icon used for the Instagram share affordance.
 */
function ShareIcon(props: SvgIconProps) {
  return (
    <SvgIcon viewBox="0 0 24 24" {...props}>
      <path d="M16 5l-3.5 3.5 1.42 1.42L17 8.33V15h2V8.33l3.08 3.59L23.5 10.5 18 5z" />
      <path d="M6 5h5V3H6c-1.1 0-2 .9-2 2v12a2 2 0 002 2h5v-2H6z" />
    </SvgIcon>
  );
}

/**
 * Formats large counters using Intl compact notation for captions.
 */
function formatCompact(value: number): string {
  return new Intl.NumberFormat("en", {
    notation: "compact",
    maximumFractionDigits: 1,
  }).format(value);
}

/**
 * Instagram-inspired section that demonstrates recording like and share events.
 *
 * Renders a mocked Reels card with gradient artwork, Instagram-style avatar,
 * and icon buttons that emit engagement events. Wrap the component in
 * {@link EngagementProvider} to ensure the analytics hooks are active.
 */
export function InstagramEngagementSection({
  handle = "instagramcreators",
  postId = "reels-remix-checklist",
  trackId = "instagram-engagement-card",
  initialLikes = 87_234,
  saves = 4_159,
}: InstagramEngagementSectionProps) {
  const [liked, setLiked] = useState(false);
  const [displayedLikes, setDisplayedLikes] = useState(initialLikes);
  const recordInteraction = useRecordInteraction();
  const baseMeta = useMemo(
    () => ({
      surface: "instagram",
      handle,
      postId,
    }),
    [handle, postId]
  );

  const formattedLikes = useMemo(
    () => formatCompact(displayedLikes),
    [displayedLikes]
  );

  const formattedSaves = useMemo(() => formatCompact(saves), [saves]);

  const handleLikeClick = () => {
    const nextLiked = !liked;
    const updatedLikes = Math.max(0, displayedLikes + (nextLiked ? 1 : -1));
    setLiked(nextLiked);
    setDisplayedLikes(updatedLikes);
    recordInteraction("instagram-like", {
      ...baseMeta,
      action: nextLiked ? "liked" : "unliked",
      likes: updatedLikes,
    });
  };

  const handleShareClick = () => {
    recordInteraction("instagram-share", {
      ...baseMeta,
      channel: "stories",
    });
  };

  return (
    <Section
      align="left"
      eyebrow="Instagram playbook"
      title="Recreate creator-style engagement loops"
    >
      <Typography variant="body1" color="text.secondary">
        Mirror the like and share mechanics Instagram creators rely on to keep
        Reels conversations active. The heart and share actions emit Flashoffer
        engagement events so product analytics can quantify reactions.
      </Typography>
      <ViewTracker
        as={Card}
        trackId={trackId}
        meta={baseMeta}
        sx={{
          borderRadius: 4,
          border: (theme) => `1px solid ${theme.palette.divider}`,
          overflow: "hidden",
          maxWidth: 420,
          width: "100%",
          backgroundColor: "background.paper",
          boxShadow: (theme) => theme.shadows[3],
        }}
      >
        <CardHeader
          avatar={
            <Avatar
              alt={`${handle} avatar`}
              sx={{
                background:
                  "radial-gradient(circle at 30% 30%, #feda75, #fa7e1e 45%, #d62976 65%, #962fbf 80%, #4f5bd5)",
                color: "common.white",
                fontWeight: 700,
              }}
            >
              IG
            </Avatar>
          }
          title={`@${handle}`}
          subheader="Reels templates"
          sx={{ pb: 0.5 }}
        />
        <CardContent sx={{ pt: 1.5 }}>
          <Box
            role="img"
            aria-label="Instagram Reels preview"
            sx={{
              borderRadius: 3,
              background:
                "linear-gradient(135deg, #feda75 10%, #fa7e1e 35%, #d62976 65%, #962fbf 85%, #4f5bd5)",
              color: "common.white",
              minHeight: { xs: 220, sm: 260 },
              display: "flex",
              alignItems: "flex-end",
              p: 2,
            }}
          >
            <Stack spacing={0.5}>
              <Typography variant="subtitle1" fontWeight={600} color="inherit">
                Remix this transitions checklist
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.85 }} color="inherit">
                Layer trending audio and captions to publish faster.
              </Typography>
            </Stack>
          </Box>
        </CardContent>
        <CardActions
          sx={{
            px: 2,
            pb: 2,
            display: "flex",
            justifyContent: "space-between",
          }}
        >
          <Stack direction="row" spacing={1.5} alignItems="center">
            <IconButton
              aria-label={liked ? "Unlike reel" : "Like reel"}
              aria-pressed={liked}
              onClick={handleLikeClick}
              color={liked ? "error" : "default"}
            >
              <HeartIcon
                sx={{
                  transition: (theme) =>
                    theme.transitions.create("transform", {
                      duration: theme.transitions.duration.shorter,
                    }),
                  transform: liked ? "scale(1.05)" : "scale(1)",
                }}
              />
            </IconButton>
            <IconButton
              aria-label="Share to Instagram stories"
              onClick={handleShareClick}
            >
              <ShareIcon />
            </IconButton>
          </Stack>
          <Stack spacing={0.25} alignItems="flex-end">
            <Typography variant="subtitle2">{formattedLikes} likes</Typography>
            <Typography variant="caption" color="text.secondary">
              {formattedSaves} saves
            </Typography>
          </Stack>
        </CardActions>
      </ViewTracker>
    </Section>
  );
}
