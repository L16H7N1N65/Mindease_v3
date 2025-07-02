# ───────────────────────────────────────────────
# build stage: compile wheels & install deps
# ───────────────────────────────────────────────
FROM python:3.11-slim AS builder

# env flags
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# deps needed only to build wheels
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential gcc g++ libpq-dev curl \
 && rm -rf /var/lib/apt/lists/*

# python venv
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# copy only requirements first (for layer cache)
COPY requirements.txt .

# faster rebuilds: wheel cache
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt


# ───────────────────────────────────────────────
# runtime stage
# ───────────────────────────────────────────────
FROM python:3.11-slim AS production

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    PYTHONPATH="/app" \
    HF_HOME="/tmp/hf-cache" \
    HUGGINGFACE_HUB_CACHE="/tmp/hf-cache"

# runtime libs only
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      libpq5=15.* curl \
 && rm -rf /var/lib/apt/lists/* \
 && apt-get clean

# ----- non-root user -----
RUN addgroup --gid 10001 mindease \
 && adduser  --uid 10001 --gid 10001 --disabled-password --gecos "" mindease

# copy venv from builder
COPY --from=builder /opt/venv /opt/venv

# copy source last (so code changes don’t invalidate pip layer)
WORKDIR /app
COPY . .

# make writable dirs
RUN mkdir -p /app/logs /app/uploads /app/data /tmp/hf-cache \
 && chown -R 10001:10001 /app /tmp/hf-cache

USER 10001

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/api/v1/health/ || exit 1

# tiny shell wrapper → lets you override workers/host/port easily
ENTRYPOINT ["sh", "-c"]
CMD ["uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers ${WORKERS:-4}"]
