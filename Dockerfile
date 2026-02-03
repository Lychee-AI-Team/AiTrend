FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y git curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY config/ ./config/
COPY CODE_CONSTITUTION.md .
COPY SECURITY.md .
COPY README.md .

RUN mkdir -p logs/traces memory .backup

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

CMD ["python3", "-m", "src.hourly"]
