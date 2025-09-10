FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    tini \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
# Harden pip for flaky networks and speed
ENV PIP_DEFAULT_TIMEOUT=120 \
    PIP_DISABLE_PIP_VERSION_CHECK=1
RUN python -m pip install --upgrade pip && \
    (python -m pip install --no-cache-dir -r requirements.txt || \
    python -m pip install --no-cache-dir -r requirements.txt || \
    python -m pip install --no-cache-dir -r requirements.txt)

COPY app /app/app

# Create non-root user
RUN useradd -ms /bin/bash appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -fsS http://127.0.0.1:8000/health || exit 1

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
