FROM python:3.10.7-slim-buster
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD python -m telegram_bot.tg_app.py
