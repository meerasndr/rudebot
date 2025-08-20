FROM python:3.11-slim

# Optional: speed up builds
ENV PIP_NO_CACHE_DIR=1 PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

WORKDIR /app
COPY pyproject.toml* ./
# If using requirements.txt instead:
# COPY requirements.txt ./
RUN pip install --upgrade pip && \
    pip install uv && \
    uv pip install --system .

COPY . .
ENV PORT=8080
EXPOSE 8080
CMD ["uvicorn","main:app","--host","0.0.0.0","--port","8080"]
