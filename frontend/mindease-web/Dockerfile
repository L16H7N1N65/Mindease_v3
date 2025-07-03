FROM node:20-alpine AS base

# Install dependencies only when needed
FROM base AS deps
WORKDIR .

# Copy package.json and package-lock.json
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm install
# Build the Next.js application
RUN npm run build

# Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production
# Build the React Native application


# Expose port for development server
EXPOSE 8080

# Start the Metro bundler
CMD ["npm", "start"]

# # Create a non-root user and group
# RUN addgroup --system --gid 1001 nodejs
# RUN adduser --system --uid 1001 nextjs

# # Copy necessary files from builder
# COPY --from=builder /app/public ./public
# COPY --from=builder /app/.next/standalone ./
# COPY --from=builder /app/.next/static ./.next/static

# # Set proper ownership
# RUN chown -R nextjs:nodejs /app

# # Switch to non-root user
# USER nextjs

# # Expose port
# EXPOSE 3000

# # Set environment variables
# ENV PORT 3000
# ENV HOSTNAME "0.0.0.0"

# # Start the application
# CMD ["node", "server.js"]
