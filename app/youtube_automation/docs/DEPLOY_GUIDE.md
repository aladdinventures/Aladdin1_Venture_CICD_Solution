# 🚀 Deployment Guide
## 1. Prerequisites
- Ubuntu 22.04+
- Docker & Docker Compose installed
- `.env` file configured

## 2. Deployment Steps
```bash
chmod +x install.sh
./install.sh
```
After installation, access:
📍 `http://<your-server-ip>:8000/docs`

---
## 3. Docker Commands
```bash
docker compose ps
docker compose logs -f
docker compose down
```

---
## 4. Environment Variables
Ensure `.env` includes valid keys for:
- `JWT_SECRET_KEY`
- `DATABASE_URL`
- `AI_PROVIDER`
- `OPENAI_API_KEY` (if applicable)

---
## 5. CI/CD Integration
Each push with a tag `v*` triggers automatic deployment workflow via GitHub Actions.
