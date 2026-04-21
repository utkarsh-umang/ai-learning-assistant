FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps (minimal). `uvicorn[standard]` can use these for better perf.
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY app /app/app
COPY data /app/data
COPY static /app/static
COPY .env.example /app/.env.example
COPY README.md /app/README.md

# Cloud Run sets $PORT. Default locally is 8080.
ENV PORT=8080
EXPOSE 8080

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]

