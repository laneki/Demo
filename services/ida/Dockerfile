FROM python:3.11-slim
WORKDIR /app
COPY services /app/services
COPY data /app/data
RUN pip install --no-cache-dir paho-mqtt pydantic pandas scikit-learn joblib
CMD ["python", "-m", "services.ida.main"]
