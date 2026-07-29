FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app_log_simulator.py .
COPY VERSION .
COPY README.md .

COPY examples ./examples

CMD ["python", "app_log_simulator.py"]
