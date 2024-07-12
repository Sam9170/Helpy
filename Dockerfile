FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY .env .env

ENV $(cat .env | xargs)

ENV FLET_SERVER_PORT 8550

EXPOSE 8550

CMD ["python", "chat.py"]
