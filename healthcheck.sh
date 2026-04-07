#!/bin/bash
# Boardy auto-recovery healthcheck
# Checks if services are responding, restarts if not

cd /opt/boardy

check_service() {
    local url=$1
    local name=$2
    local code
    code=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 --max-time 10 "$url" 2>/dev/null)
    if [ "$code" != "200" ]; then
        echo "$(date): $name is DOWN (HTTP $code), restarting..." >> /var/log/boardy-healthcheck.log
        docker compose -f docker-compose.prod.yml --env-file .env.prod restart "$name" 2>&1 >> /var/log/boardy-healthcheck.log
        return 1
    fi
    return 0
}

check_service "http://localhost:8000/health" "backend"
check_service "http://localhost:3000/" "frontend"
