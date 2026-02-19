FROM python:3.11-slim
WORKDIR /app
COPY services/common /app/common
COPY services/device_sim /app
RUN pip install --no-cache-dir -r requirements.txt
ENV PYTHONUNBUFFERED=1
CMD ["python", "main.py"]
