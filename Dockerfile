FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir python-telegram-bot cohere
CMD ["python", "cohere_bot.py"]