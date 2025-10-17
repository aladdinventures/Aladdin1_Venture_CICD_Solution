# 🎬 YouTube Automation System v3.0

AI-powered automation platform for YouTube content management, designed under **Aladdin Venture Lab** architecture.

---

## 🚀 Overview
This project automates content scheduling, publishing, analytics, and AI-based title/thumbnail generation.  
Built with **FastAPI**, **Celery**, **Redis**, **PostgreSQL**, and **Docker Compose** for seamless deployment.

---

## 🧩 Project Structure
```
youtube_automation_v3/
├── backend/              # FastAPI app & Celery workers
├── frontend/             # React / Next.js interface (optional future module)
├── scripts/              # Shell scripts and automation tools
├── docs/                 # Documentation & deployment guides
├── install.sh            # One-click installation script
├── .env.example          # Environment variables template
├── docker-compose.yml    # Multi-container orchestration
└── README.md
```

---

## ⚙️ Installation (One-Click)
```bash
chmod +x install.sh
./install.sh
```

After installation:
- API available at: `http://<server-ip>:8000/docs`
- Redis: `localhost:6379`
- PostgreSQL: `localhost:5432`

---

## 🧠 Features
✅ AI title & keyword generation  
✅ Automated scheduling & publishing  
✅ Celery background task queue  
✅ RESTful API documentation via FastAPI  
✅ Modular, container-based architecture  

---

## 🧰 Requirements
- Ubuntu 22.04 or later  
- Docker & Docker Compose  
- Python 3.10+  
- Minimum 2 GB RAM

---

## 🧾 License
© 2025 Aladdin Venture Lab.  
All rights reserved. Proprietary use only.
🌐 Official website: [www.aladdin-trading.ca](https://www.aladdin-trading.ca)
