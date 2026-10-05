FROM nikolaik/python-nodejs:python3.11-nodejs20-slim

WORKDIR /app

# Install Caddy & Supervisor
RUN apt-get update && apt-get install -y curl debian-keyring debian-archive-keyring apt-transport-https supervisor && \
    curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg && \
    curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list && \
    apt-get update && apt-get install -y caddy && \
    rm -rf /var/lib/apt/lists/*

# Setup Python backend
COPY backend/requirements.txt /app/backend/
RUN pip install --no-cache-dir -r /app/backend/requirements.txt
COPY backend/ /app/backend/

# Setup Node frontend
COPY frontend/package*.json /app/frontend/
WORKDIR /app/frontend
RUN npm install
COPY frontend/ /app/frontend/

# Set API URL to empty so frontend uses relative paths (routed via Caddy)
ENV NEXT_PUBLIC_API_URL=""
ENV NEXT_PUBLIC_WS_URL=""
RUN npm run build

WORKDIR /app

# Setup Caddy and Supervisor
COPY Caddyfile /etc/caddy/Caddyfile
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Expose default port (Railway overrides this with $PORT)
ENV PORT=8080
EXPOSE 8080

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
