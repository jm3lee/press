# syntax=docker/dockerfile:1.6

######################################################################
# Flashoffer demo build
#
# This Dockerfile builds the React-based Flashoffer demo as well as the
# supporting static assets served by nginx. Multi-stage builds keep Node.js
# tooling out of the final runtime image while allowing layer reuse across
# the flashoffer-react and flashoffer-demo packages.
######################################################################

# Base Node.js layer shared by all build stages. The slim variant provides
# npm without unnecessary language runtimes.
FROM node:22-slim AS base
WORKDIR /workspace

# Install dependencies for the Flashoffer React package so subsequent
# stages can reuse the layer when only source files change.
FROM base AS flashoffer-react-deps
WORKDIR /workspace/app/flashoffer/flashoffer-react
COPY app/flashoffer/flashoffer-react/package.json app/flashoffer/flashoffer-react/package-lock.json ./
RUN --mount=type=cache,target=/root/.npm,sharing=locked npm ci

# Build the production Flashoffer React bundle.
FROM flashoffer-react-deps AS flashoffer-react-build
COPY app/flashoffer/flashoffer-react ./
RUN npm run build

# Build the static demo shell that embeds the Flashoffer widget.
FROM flashoffer-react-build AS flashoffer-demo-build
WORKDIR /workspace/app/flashoffer/flashoffer-demo
COPY app/flashoffer/flashoffer-demo/package.json app/flashoffer/flashoffer-demo/package-lock.json ./
RUN --mount=type=cache,target=/root/.npm,sharing=locked npm ci
COPY app/flashoffer/flashoffer-demo ./
RUN npm run build

# Runtime image for running the demo via the Vite preview server. This is
# primarily used for local development or integration tests.
FROM node:22-slim AS runner
ENV NODE_ENV=production
ENV PORT=4173
WORKDIR /workspace
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
    apt-get update \
    && apt-get install --no-install-recommends -y git
COPY --from=flashoffer-react-build /workspace/app/flashoffer/flashoffer-react /workspace/app/flashoffer/flashoffer-react
COPY --from=flashoffer-demo-build /workspace/app/flashoffer/flashoffer-demo /workspace/app/flashoffer/flashoffer-demo
COPY app/flashoffer/flashoffer-demo/entrypoint.sh /usr/local/bin/flashoffer-entrypoint
RUN chmod +x /usr/local/bin/flashoffer-entrypoint
EXPOSE 4173
ENTRYPOINT ["flashoffer-entrypoint"]

# Production image served by nginx. Only the static assets are copied in,
# keeping the container small and secure.
FROM nginx:1.27-alpine AS production
WORKDIR /usr/share/nginx/html
COPY app/flashoffer/flashoffer-demo/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=flashoffer-demo-build /workspace/app/flashoffer/build/static/js ./
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
