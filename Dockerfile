# -------------------------
# Stage 1: Build frontend
# -------------------------
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

# Copy frontend package files and install dependencies
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

# Copy frontend source code and build
COPY frontend ./
RUN npm run build

# -------------------------
# Stage 2: Backend + combined image
# -------------------------
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies for backend
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend ./

# Copy frontend build output
COPY --from=frontend-builder /app/frontend/out ./frontend/out

# Install serve globally to serve frontend
RUN pip install uvicorn fastapi && npm install -g serve

# Expose ports
EXPOSE 8000 3000

# Copy start script
COPY start.sh .
RUN chmod +x start.sh

# Start both backend and frontend
CMD ["./start.sh"]
