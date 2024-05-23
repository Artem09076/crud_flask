FROM python:3.11.7

WORKDIR /videos_data

COPY app.py .
COPY requirements.txt .

RUN pip install -r requirements.txt
