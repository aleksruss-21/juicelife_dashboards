FROM python:3.10.7-slim-buster
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY cfg cfg
COPY service service
COPY telegram_bot telegram_bot
COPY storage storage
COPY .env .
CMD python -m telegram_bot.tg_app.py