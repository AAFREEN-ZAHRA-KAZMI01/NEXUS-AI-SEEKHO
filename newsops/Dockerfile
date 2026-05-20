FROM python:3.11-slim

WORKDIR /app

RUN apt-get clean && apt-get update -o Acquire::http::No-Cache=True -o Acquire::http::Pipeline-Depth=0 && apt-get install -y --fix-missing \
    gcc \
    g++ \
    libxml2-dev \
    libxslt-dev \
    libjpeg-dev \
    zlib1g-dev \
    curl \
    tesseract-ocr \
    tesseract-ocr-eng \
    poppler-utils \
    libpoppler-cpp-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --default-timeout=100 --no-cache-dir -r requirements.txt

RUN useradd -m -u 1001 newsops \
    && mkdir -p /app/data /app/logs \
    && chown -R newsops:newsops /app/data /app/logs

COPY --chown=newsops:newsops . .

USER newsops

EXPOSE 8000

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_HOST=0.0.0.0 \
    APP_PORT=8000

RUN chmod +x ./scripts/start.sh

CMD ["./scripts/start.sh"]
