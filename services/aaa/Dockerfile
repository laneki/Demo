FROM python:3.11-slim
WORKDIR /app
COPY services /app/services
RUN pip install --no-cache-dir paho-mqtt pydantic
CMD ["python", "-m", "services.aaa.main"]
