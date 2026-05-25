# TODO: Dockerfile for REST gateway
FROM python:3.11-slim
WORKDIR /app
COPY gateway/requirements.txt .
RUN pip install -r requirements.txt
COPY . .
ENV PYTHONPATH=/app
CMD ["uvicorn", "gateway.app:app", "--host", "0.0.0.0", "--port", "8080"]
