FROM python:3.11-slim
RUN apt-get update && apt-get install -y libgl1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY FSRCNN_x2.pb .
COPY bot.py .
CMD ["python", "bot.py"]