# Host Pre-Flight (16 GB self-host)

Single-tenant Linux host. Run once per box before the first `docker compose up`.

## Required

- Docker Engine ≥ 24 with the Compose v2 plugin (`docker compose version` reports `v2.x`). The legacy `docker-compose` v1 binary silently ignores `deploy.resources.limits`.
- 16 GB RAM, ≥ 30 GB free disk on the partition that holds `/var/lib/docker`.
- Outbound HTTPS to Docker Hub (`postgres:16-alpine`, `python:3.12-slim`, `nginx`).

## Swap (4 GB)

Migrations and the Vite build can spike past container limits. Add swap once:

```
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
sudo sysctl vm.swappiness=10
```

## Docker daemon ulimits

`/etc/docker/daemon.json` — raise the open-file ceiling so Postgres + uvicorn workers don't bottleneck on FDs:

```
{
  "default-ulimits": {
    "nofile": { "Name": "nofile", "Hard": 65536, "Soft": 65536 }
  },
  "log-driver": "json-file",
  "log-opts": { "max-size": "10m", "max-file": "5" }
}
```

`sudo systemctl restart docker` after editing.

## First-run "go"

```
cd infra && cp .env.prod.example .env.prod && $EDITOR .env.prod && \
  docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --build
```

`POSTGRES_PASSWORD` and `JWT_SECRET_KEY` are required — compose interpolation fails fast if either is empty.

## Smoke

```
curl -fsS http://localhost:8000/api/v1/health
docker stats --no-stream
psql -h 127.0.0.1 -U bbms_user -d blood_bank -c 'select * from alembic_version;'
```

Expect `{"status":"ok"}`, every container under its declared limit, and one row at the head Alembic revision.

## LAN exposure (opt-in only)

Postgres binds to `127.0.0.1` by default. To expose on LAN, set `POSTGRES_BIND_HOST=0.0.0.0` in `.env.prod` and rotate `POSTGRES_PASSWORD` to a strong value first — credential-stuffing surface is real.
