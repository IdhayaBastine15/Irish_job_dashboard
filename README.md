# Irish Job Dashboard

A cloud-native job market analytics platform for Ireland — built with Python, FastAPI, PostgreSQL, Elasticsearch, Docker, Kubernetes, and AWS.

Aggregates live job listings from Adzuna, extracts skills using NLP, generates AI-powered market insights via Claude, and presents everything through a React dashboard.

---

## Live Demo

| Service | URL |
|---|---|
| Frontend | https://gleeful-valkyrie-0d7c67.netlify.app |
| Backend API | http://irish-jobs-alb-618477737.eu-west-1.elb.amazonaws.com |
| API Docs | http://irish-jobs-alb-618477737.eu-west-1.elb.amazonaws.com/docs |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend                             │
│              React + Vite + Tailwind CSS                    │
│                   Netlify (CDN)                             │
└──────────────────────┬──────────────────────────────────────┘
                       │  /api/* (proxied)
┌──────────────────────▼──────────────────────────────────────┐
│                      Backend API                            │
│                FastAPI + Uvicorn (ASGI)                     │
│              Railway (dev) / AWS ECS Fargate (prod)         │
│                                                             │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │  REST APIs  │  │ ETL Pipeline │  │  AI Insights     │   │
│  │  5 routers  │  │  E → T → L  │  │  Claude API      │   │
│  └─────────────┘  └──────────────┘  └──────────────────┘   │
└───────┬──────────────────┬──────────────────────────────────┘
        │                  │
┌───────▼──────┐   ┌───────▼──────────┐
│  PostgreSQL  │   │  Elasticsearch   │
│  (jobs, logs)│   │  (full-text      │
│  RDS / Rail  │   │   job search)    │
└──────────────┘   └──────────────────┘
```

---

## Tech Stack

### Backend
| Technology | Purpose |
|---|---|
| Python 3.11 | Runtime |
| FastAPI 0.109 | Async REST API framework |
| SQLAlchemy 2.0 + asyncpg | Async ORM + PostgreSQL driver |
| Alembic | Database schema migrations |
| Pydantic v2 | Data validation and settings |
| APScheduler | Periodic pipeline scheduling (every 6h) |
| httpx | Async HTTP client for external APIs |
| Anthropic SDK | Claude AI for market insights |

### Data Pipeline (ETL)
| Stage | What it does |
|---|---|
| **Extract** | Fetches jobs from Adzuna API, retries up to 3× per page |
| **Transform** | Normalises fields, extracts Irish counties, extracts skills |
| **Load** | Upserts to PostgreSQL, indexes to Elasticsearch |

Pipeline status is tracked in the database and exposed via `/api/pipeline/status`.

### Frontend
| Technology | Purpose |
|---|---|
| React 18 | UI framework |
| Vite | Build tool and dev server |
| Tailwind CSS | Utility-first styling |
| Recharts | Data visualisation (charts) |
| Axios | HTTP client |
| React Router v6 | Client-side routing |

### Infrastructure
| Technology | Purpose |
|---|---|
| Docker | Container image for the backend |
| Docker Compose | Local development (postgres + elasticsearch + backend) |
| Kubernetes | Production manifests (Deployment, Service, HPA, Ingress) |
| Terraform | AWS infrastructure as code |
| GitHub Actions | CI/CD — test → build → push to ECR → deploy to ECS |

### AWS (Production)
| Service | Purpose |
|---|---|
| ECS Fargate | Runs Docker containers (serverless, auto-scales 2–8 tasks) |
| RDS PostgreSQL 15 | Managed relational database |
| OpenSearch 2.11 | Managed Elasticsearch for job search |
| ECR | Docker image registry |
| ALB | Application Load Balancer (public entry point) |
| S3 | Resume file storage (private, encrypted) |
| SSM Parameter Store | Encrypted API key storage |
| IAM + OIDC | GitHub Actions deploys via role assumption (no static keys) |
| VPC | Isolated network with public/private subnets and NAT Gateway |

---

## Project Structure

```
Irish_job_dashboard/
│
├── backend/                    # FastAPI application
│   ├── main.py                 # App entry point, scheduler, CORS
│   ├── config.py               # Pydantic settings (env vars)
│   ├── database.py             # SQLAlchemy async engine
│   ├── models.py               # ORM models (Job, SyncLog, Application, Resume)
│   ├── schemas.py              # Pydantic request/response schemas
│   ├── Dockerfile              # Production container image
│   │
│   ├── routers/                # API route handlers
│   │   ├── jobs.py             # GET /api/jobs/
│   │   ├── stats.py            # GET /api/stats/*
│   │   ├── insights.py         # GET /api/insights/*  (Claude AI)
│   │   ├── applications.py     # Job application tracker
│   │   ├── resume.py           # Resume upload and skill matching
│   │   └── pipeline.py         # GET /api/pipeline/status, POST /trigger
│   │
│   ├── pipeline/               # ETL pipeline (Databricks-style)
│   │   ├── context.py          # PipelineContext + StageResult
│   │   ├── extract.py          # Fetch from Adzuna (with retry)
│   │   ├── transform.py        # Normalise + skill extraction
│   │   ├── load.py             # Upsert to PostgreSQL + Elasticsearch
│   │   └── runner.py           # Orchestrator: E → T → L
│   │
│   ├── services/               # External integrations
│   │   ├── adzuna.py           # Adzuna API client
│   │   ├── search.py           # Elasticsearch index + search
│   │   ├── skill_extractor.py  # Skill taxonomy matching + spaCy NER
│   │   └── claude_insights.py  # Claude AI market analysis
│   │
│   └── tests/                  # BDD tests (pytest-bdd)
│       ├── features/           # Gherkin .feature files
│       └── steps/              # Step definitions
│
├── frontend/                   # React application
│   ├── src/
│   │   ├── pages/              # Dashboard, Jobs, Skills, Insights
│   │   ├── components/         # Header, Sidebar, Charts, JobCard
│   │   ├── api/index.js        # Axios API layer
│   │   ├── context/            # React Context state
│   │   └── hooks/              # useJobs, useStats
│   └── vite.config.js
│
├── pipeline/                   # ETL (imported by backend)
│
├── k8s/                        # Kubernetes manifests
│   ├── namespace.yml
│   ├── configmap.yml
│   ├── secret.yml
│   ├── postgres/               # StatefulSet + Service
│   ├── elasticsearch/          # StatefulSet + Service
│   ├── backend/                # Deployment + Service + HPA
│   ├── ingress.yml             # nginx Ingress
│   └── apply.sh                # Ordered deploy script
│
├── infra/                      # Terraform (AWS)
│   ├── main.tf                 # Provider + S3 backend
│   ├── variables.tf
│   ├── vpc.tf                  # VPC, subnets, security groups
│   ├── ecr.tf                  # Container registry
│   ├── rds.tf                  # PostgreSQL database
│   ├── opensearch.tf           # Search cluster
│   ├── s3.tf                   # Resume storage
│   ├── iam.tf                  # Roles (ECS, GitHub Actions OIDC)
│   ├── ecs.tf                  # Fargate cluster, ALB, auto-scaling
│   ├── ssm.tf                  # Encrypted secrets
│   └── outputs.tf
│
├── .github/workflows/
│   └── ci.yml                  # Test → Build → Push ECR → Deploy ECS
├── docker-compose.yml          # Local dev (postgres + elasticsearch + backend)
└── netlify.toml                # Frontend build + API proxy config
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/health` | Health check |
| GET | `/api/jobs/` | List jobs (filter by category, county, skills) |
| GET | `/api/jobs/{id}` | Single job detail |
| GET | `/api/stats/overview` | Total jobs, companies, counties |
| GET | `/api/stats/by-category` | Job counts per category |
| GET | `/api/stats/by-county` | Job counts per Irish county |
| GET | `/api/stats/top-skills` | Most in-demand skills |
| GET | `/api/stats/salary-distribution` | Salary range breakdown |
| GET | `/api/stats/sync-logs` | Recent pipeline run history |
| GET | `/api/insights/market/{category}` | Claude AI market analysis |
| GET | `/api/insights/job/{id}` | Claude AI job-specific insight |
| GET | `/api/pipeline/status` | ETL pipeline run summaries |
| POST | `/api/pipeline/trigger` | Manually trigger a pipeline run |
| POST | `/api/resume/upload` | Upload CV (PDF/DOCX/TXT) |
| GET | `/api/applications/` | List tracked job applications |

---

## Running Locally

### With Docker (recommended)

```bash
# Clone the repo
git clone https://github.com/IdhayaBastine15/Irish_job_dashboard.git
cd Irish_job_dashboard

# Add your API keys
cp backend/.env.example backend/.env
# Edit backend/.env with your Adzuna + Anthropic keys

# Start everything
docker-compose up
```

- Backend API: http://localhost:8000
- API docs: http://localhost:8000/docs
- Elasticsearch: http://localhost:9200

### Without Docker

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in your keys
uvicorn main:app --reload

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

---

## CI/CD Pipeline

Every push to `main` triggers three GitHub Actions jobs:

```
1. TEST    → pytest with real PostgreSQL service container
2. BUILD   → docker build → push to AWS ECR (tagged with git SHA)
3. DEPLOY  → update ECS task definition → rolling deploy to Fargate
              waits for stability, auto-rollbacks if health checks fail
```

---

## Deploying to AWS

```bash
# 1. Install tools
brew install awscli terraform

# 2. Configure AWS credentials
aws configure

# 3. Create Terraform state bucket
aws s3 mb s3://irish-jobs-tf-state --region eu-west-1

# 4. Set your secrets
cd infra
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with real values

# 5. Deploy all infrastructure
terraform init
terraform plan
terraform apply

# 6. Add AWS_ROLE_ARN output value as a GitHub secret
# Then every git push auto-deploys to AWS
```

---

## Data Sources

| Source | Type | Notes |
|---|---|---|
| Adzuna API | Job listings | Primary source — 250 jobs per sync |
| Claude AI (Anthropic) | AI insights | Market analysis per category |

---

## Environment Variables

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection (asyncpg) |
| `SYNC_DATABASE_URL` | PostgreSQL connection (psycopg2) |
| `ELASTICSEARCH_URL` | Elasticsearch / OpenSearch endpoint |
| `ADZUNA_APP_ID` | Adzuna API credentials |
| `ADZUNA_APP_KEY` | Adzuna API credentials |
| `ANTHROPIC_API_KEY` | Claude AI API key |
| `SYNC_INTERVAL_HOURS` | How often the ETL pipeline runs (default: 6) |
