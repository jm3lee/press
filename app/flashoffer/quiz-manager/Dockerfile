# syntax=docker/dockerfile:1.7

FROM node:22-slim

WORKDIR /app/flashoffer

# Install flashoffer-react so local file dependency is available.
COPY app/flashoffer/flashoffer-react/package.json app/flashoffer/flashoffer-react/package-lock.json ./flashoffer-react/
RUN --mount=type=cache,target=/root/.npm,sharing=locked \
    cd flashoffer-react && npm ci --cache /root/.npm --prefer-offline

COPY app/flashoffer/flashoffer-react ./flashoffer-react
RUN cd flashoffer-react && npm run build

# Install quiz-manager dependencies with the local flashoffer-react linkage in place.
COPY app/flashoffer/quiz-manager/package.json app/flashoffer/quiz-manager/package-lock.json ./quiz-manager/
RUN --mount=type=cache,target=/root/.npm,sharing=locked \
    cd quiz-manager && npm ci --cache /root/.npm --prefer-offline

COPY app/flashoffer/quiz-manager ./quiz-manager

WORKDIR /app/flashoffer/quiz-manager

EXPOSE 5175

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5175"]
