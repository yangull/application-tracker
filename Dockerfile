# Dockerfile — instructions to build the application-tracker image
# Docker reads this top to bottom and executes each step

FROM python:3.12-slim
# Start from an official Python 3.12 image
# "slim" means a minimal Linux OS with just Python — smaller and faster than the full image
# This replaces needing Python installed on the host machine

WORKDIR /app
# Set the working directory inside the container to /app
# All following commands run from this directory
# Like doing "cd /app" inside the container

COPY requirements.txt .
# Copy requirements.txt from your machine into the container's /app folder
# We copy this BEFORE the rest of the code — this is intentional (explained below)

RUN pip install --no-cache-dir -r requirements.txt
# Install all dependencies inside the container
# --no-cache-dir keeps the image smaller by not storing the pip cache
# This runs during the BUILD step, not when the container starts

COPY . .
# Now copy the rest of your code into the container
# The reason we copy requirements.txt first and install, THEN copy code:
# Docker caches each step — if your code changes but requirements.txt didn't,
# Docker skips the pip install step and uses the cache — much faster rebuilds

EXPOSE 8000
# Documents that the container listens on port 8000
# Doesn't actually open the port — that happens in docker-compose.yml

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
# The command that runs when the container starts
# --host 0.0.0.0 means "accept connections from outside the container"
# Without this, uvicorn would only listen inside the container and be unreachable