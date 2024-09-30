FROM python:3.11-slim

WORKDIR /opt/linebot
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

WORKDIR /opt/linebot/src

CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]