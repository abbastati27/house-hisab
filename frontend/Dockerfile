# Build Stage
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production Stage (Static Export)
FROM node:20-alpine AS runner
WORKDIR /app
RUN npm install -g serve
COPY --from=builder /app/out ./out

# Expose frontend port
EXPOSE 3000

# Serve the static site
CMD ["serve", "-s", "out", "-l", "3000"]
