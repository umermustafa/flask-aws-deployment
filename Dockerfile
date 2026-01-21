# Stage 1 : Build the application environment

FROM python:slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl procps \
    && rm -rf /var/lib/apt/lists/*


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2 : Run the application environment

FROM python:slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl procps \
    && rm -rf /var/lib/apt/lists/*

RUN adduser --disabled-password --gecos '' appuser

COPY --from=builder /usr/local /usr/local
COPY . .

RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 5001

ENV FLASK_APP=app.py
ENV FLASK_ENV=development

# CMD ["flask", "run", "--host=0.0.0.0", "--port=5001"]

HEALTHCHECK CMD curl --fail http://localhost:5001/health || exit 1

CMD ["gunicorn","--bind","0.0.0.0:5001","app:app","--workers=2","--threads=4","--timeout=60","--access-logfile=-","--error-logfile=-"]