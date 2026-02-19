FROM python:3.11-slim
WORKDIR /app
COPY services /app/services
RUN pip install --no-cache-dir paho-mqtt fastapi uvicorn
CMD ["uvicorn", "services.metrics.main:app", "--host", "0.0.0.0", "--port", "8000"]
