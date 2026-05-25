# TODO: Dockerfile for gRPC server
FROM python:3.11-slim
WORKDIR /app
COPY grpc_server/requirements.txt .
RUN pip install -r requirements.txt
COPY . .
ENV PYTHONPATH=/app
CMD ["python", "grpc_server/server.py"]
