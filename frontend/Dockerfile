FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY common common
COPY frontend/static static
COPY frontend/main.py main.py

ENV PYTHONUNBUFFERED=1

CMD ["python", "-u", "main.py"]
