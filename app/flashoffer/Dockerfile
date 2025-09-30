# syntax=docker/dockerfile:1.6

FROM node:22-slim AS base
WORKDIR /workspace

FROM base AS flashoffer-react-deps
WORKDIR /workspace/app/flashoffer-react
COPY app/flashoffer-react/package.json app/flashoffer-react/package-lock.json ./
RUN npm ci

FROM flashoffer-react-deps AS flashoffer-react-build
COPY app/flashoffer-react ./
RUN npm run build

FROM flashoffer-react-build AS flashoffer-demo-build
WORKDIR /workspace/app/flashoffer-demo
COPY app/flashoffer-demo/package.json app/flashoffer-demo/package-lock.json ./
RUN npm ci
COPY app/flashoffer-demo ./
RUN npm run build

FROM node:22-slim AS runner
ENV NODE_ENV=production
WORKDIR /workspace
COPY --from=flashoffer-react-build /workspace/app/flashoffer-react /workspace/app/flashoffer-react
COPY --from=flashoffer-demo-build /workspace/app/flashoffer-demo /workspace/app/flashoffer-demo

FROM nginx:1.27-alpine AS production
WORKDIR /usr/share/nginx/html
COPY app/flashoffer/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=flashoffer-demo-build /workspace/app/flashoffer-demo/ ./
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
