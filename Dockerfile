# ---------- Build React frontend ----------
FROM node:22-alpine AS frontend-build

WORKDIR /app/frontend

# Frontend dependencies
COPY frontend/package*.json ./
RUN npm ci

# Copy frontend source and build it
COPY frontend/ ./
RUN npm run build


# Run Python backend
FROM python:3.11-slim

WORKDIR /app

# Install Tesseract and OpenCV system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY backend/requirements.txt /app/backend/requirements.txt

RUN pip install --no-cache-dir \
    -r /app/backend/requirements.txt

# Backend
COPY backend/ /app/backend/

COPY --from=frontend-build \
    /app/frontend/dist \
    /app/frontend/dist

WORKDIR /app/backend

EXPOSE 10000

# Start FastAPI using Render's assigned port
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-10000}"]