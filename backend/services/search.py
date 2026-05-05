from __future__ import annotations
import httpx
from config import get_settings

settings = get_settings()
ES_URL = settings.elasticsearch_url
INDEX = "jobs"


async def ensure_index():
    """Create the jobs index with mappings if it doesn't exist."""
    mapping = {
        "mappings": {
            "properties": {
                "adzuna_id":    {"type": "keyword"},
                "title":        {"type": "text", "analyzer": "english"},
                "company":      {"type": "keyword"},
                "location":     {"type": "keyword"},
                "county":       {"type": "keyword"},
                "category":     {"type": "keyword"},
                "description":  {"type": "text", "analyzer": "english"},
                "skills":       {"type": "keyword"},
                "salary_min":   {"type": "float"},
                "salary_max":   {"type": "float"},
                "posted_at":    {"type": "date"},
                "job_url":      {"type": "keyword", "index": False},
            }
        }
    }
    async with httpx.AsyncClient() as client:
        resp = await client.head(f"{ES_URL}/{INDEX}")
        if resp.status_code == 404:
            await client.put(f"{ES_URL}/{INDEX}", json=mapping)


async def index_job(job: dict):
    """Index a single job document."""
    doc_id = job.get("adzuna_id") or job.get("id")
    async with httpx.AsyncClient() as client:
        await client.put(
            f"{ES_URL}/{INDEX}/_doc/{doc_id}",
            json=job,
        )


async def search_jobs(query: str, filters: dict | None = None, size: int = 20, from_: int = 0) -> dict:
    """Full-text search jobs in Elasticsearch."""
    must = []

    if query:
        must.append({
            "multi_match": {
                "query": query,
                "fields": ["title^3", "description", "skills^2", "company"],
            }
        })

    filter_clauses = []
    if filters:
        if filters.get("category"):
            filter_clauses.append({"term": {"category": filters["category"]}})
        if filters.get("county"):
            filter_clauses.append({"term": {"county": filters["county"]}})
        if filters.get("salary_min"):
            filter_clauses.append({"range": {"salary_min": {"gte": filters["salary_min"]}}})

    body = {
        "from": from_,
        "size": size,
        "query": {
            "bool": {
                "must": must or [{"match_all": {}}],
                "filter": filter_clauses,
            }
        },
        "sort": [{"posted_at": {"order": "desc"}}],
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{ES_URL}/{INDEX}/_search", json=body)
        resp.raise_for_status()
        data = resp.json()

    hits = data["hits"]["hits"]
    total = data["hits"]["total"]["value"]
    return {
        "total": total,
        "results": [h["_source"] for h in hits],
    }
