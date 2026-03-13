# ============================================================================
# ContribHub Web — Multi-stage Next.js Dockerfile
# ============================================================================

# ── Stage 1: Install dependencies ──────────────────────────────────────────
FROM node:22-alpine AS deps

WORKDIR /app

# Install libc6-compat for Alpine compatibility with native modules
RUN apk add --no-cache libc6-compat

# Copy root workspace files for npm workspaces resolution
COPY package.json package-lock.json ./
COPY apps/web/package.json ./apps/web/package.json
COPY packages/shared/package.json ./packages/shared/package.json

RUN npm ci --workspace=apps/web --include-workspace-root

# ── Stage 2: Build the application ────────────────────────────────────────
FROM node:22-alpine AS builder

WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY --from=deps /app/apps/web/node_modules ./apps/web/node_modules
COPY --from=deps /app/packages/shared/node_modules ./packages/shared/node_modules 2>/dev/null || true

# Copy source code
COPY packages/shared ./packages/shared
COPY apps/web ./apps/web
COPY package.json turbo.json ./

# Build arguments for public env vars baked into the client bundle
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

# Enable Next.js standalone output for minimal Docker image
ENV NEXT_TELEMETRY_DISABLED=1

RUN npx turbo run build --filter=@contribhub/web

# ── Stage 3: Production runner ─────────────────────────────────────────────
FROM node:22-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Non-root user for security
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copy standalone output from the build stage
COPY --from=builder /app/apps/web/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/apps/web/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/apps/web/.next/static ./apps/web/.next/static

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "apps/web/server.js"]
