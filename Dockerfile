# Use Python base image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the local content to the container's working directory
COPY . /app

# Install the required dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set the environment variable to avoid buffering of the output
ENV PYTHONUNBUFFERED=1

# Run the bot when the container starts
CMD ["python", "bot.py"]
