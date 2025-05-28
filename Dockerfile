FROM python:3.9-slim-buster

WORKDIR /app
COPY . .

ENV TORCH_URL=https://download.pytorch.org/whl/cpu/torch_stable.html

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt -f $TORCH_URL

CMD ["python", "main.py"]
