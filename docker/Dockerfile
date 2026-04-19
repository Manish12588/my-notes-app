# Use the official Python 3.12-slim-bookworm slim image as the base
FROM python:3.12-slim-bookworm

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source code
COPY app/ .

# Run as a non-root user
RUN useradd -m appuser && \
    mkdir -p /app/instance && \
    chown -R appuser:appuser /app
USER appuser

ENV PYTHONUNBUFFERED=1

VOLUME ["/app/instance"]

# Document the port
EXPOSE 5000

# Start the Flask web server
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "1", "app:app"]