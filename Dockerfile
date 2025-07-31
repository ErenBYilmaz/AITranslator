FROM python:3.10-slim

# Install system dependencies for audio processing
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ffmpeg \
        espeak-ng \
        libportaudio2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source
COPY . .

# Default to showing the CLI help
ENTRYPOINT ["python", "translator.py"]
CMD ["--help"]
