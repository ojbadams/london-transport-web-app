FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY common common
COPY data_fetcher/src src
COPY data_fetcher/main.py main.py

ENV PYTHONUNBUFFERED=1

CMD ["python", "-u", "main.py"]
