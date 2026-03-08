# 🇮🇪 Irish Jobs Market Dashboard

> A real-time analytics dashboard tracking the Irish tech job market — built with FastAPI, React, and PostgreSQL.

![Python]
![FastAPI]
![React]
![PostgreSQL]

---

## 📌 Overview

The Irish Jobs Market Dashboard is a full-stack data application that pulls live job listings from the **Adzuna API**, processes and stores them in PostgreSQL, and visualises key hiring trends through an interactive React frontend.

Designed specifically for the Irish tech market, this project helps job seekers and analysts understand which skills are in demand, which companies are hiring, and how the market is evolving over time.

---

## ✨ Features

- 🔄 **Live Data Pipeline** — Automated ingestion of job listings via the Adzuna API
- 🧠 **Skill Extraction** — NLP-based parsing to identify in-demand technologies from job descriptions
- 📊 **Interactive Visualisations** — Charts and filters for salary ranges, job categories, top companies, and location breakdown
- 🗄️ **PostgreSQL Storage** — Structured data model for historical trend analysis
- ⚡ **FastAPI Backend** — RESTful API serving processed data to the frontend

---

## 🏗️ Architecture

```
Adzuna API
    ↓
Data Ingestion (Python)
    ↓
PostgreSQL Database
    ↓
FastAPI REST API
    ↓
React Dashboard (Charts + Filters)
```

---

## 🛠️ Tech Stack

| Layer       | Technology              |
|-------------|-------------------------|
| Frontend    | React, Recharts         |
| Backend     | FastAPI, Python         |
| Database    | PostgreSQL              |
| Data Source | Adzuna Jobs API         |
| DevTools    | Git, dotenv             |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Adzuna API key ([get one free](https://developer.adzuna.com/))

### 1. Clone the repo

```bash
git clone https://github.com/IdhayaBastine15/Irish_job_dashboard.git
cd Irish_job_dashboard
```

### 2. Backend setup

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Add your Adzuna API key and PostgreSQL credentials to .env
uvicorn main:app --reload
```

### 3. Frontend setup

```bash
cd frontend
npm install
npm start
```

### 4. Run the data pipeline

```bash
python pipeline/ingest.py
```

---

## 📁 Project Structure

```
Irish_job_dashboard/
├── backend/
│   ├── main.py          # FastAPI app
│   ├── models.py        # Database models
│   ├── routes/          # API endpoints
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/  # Chart and UI components
│   │   └── App.jsx
│   └── package.json
├── pipeline/
│   └── ingest.py        # Adzuna data ingestion script
└── README.md
```

---

## 📸 Screenshots

> *Coming soon*

---

## 🗺️ Roadmap

- [ ] Add company-level filtering
- [ ] Weekly trend email digest
- [ ] Deploy to cloud (Render / Railway)
- [ ] LinkedIn jobs integration

---

## 👤 Author

**Idhaya Bastine Kennedy**  
Full-Stack Engineer · Dublin, Ireland  
[GitHub](https://github.com/IdhayaBastine15) · [LinkedIn](https://www.linkedin.com/in/idhaya-bastine-kennedy)
