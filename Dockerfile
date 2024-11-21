FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD gunicorn main:app --bind 0.0.0.0:$PORT 