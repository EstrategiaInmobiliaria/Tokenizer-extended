FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

COPY ai_gateway/requirements.txt ./ai_gateway/requirements.txt
RUN pip install --no-cache-dir -r ai_gateway/requirements.txt

COPY ai_gateway ./ai_gateway

RUN useradd --create-home appuser
USER appuser

EXPOSE 8080
CMD ["uvicorn", "ai_gateway.main:app", "--host", "0.0.0.0", "--port", "8080"]
