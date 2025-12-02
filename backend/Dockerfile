FROM python:3.10-slim

# System packages needed for scapy + networking
RUN apt-get update && apt-get install -y \
    tcpdump \
    libpcap-dev \
    net-tools \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python requirements
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY backend/ ./

# Flask runs on port 5000
EXPOSE 5000

ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Run Flask via gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
