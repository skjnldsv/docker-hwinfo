FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

RUN pip install flask psutil
COPY app.py /app.py
CMD ["python", "/app.py"]