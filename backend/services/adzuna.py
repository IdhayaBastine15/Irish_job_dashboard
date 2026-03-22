from __future__ import annotations
import httpx
from datetime import datetime
from config import get_settings

settings = get_settings()

IRISH_COUNTIES = [
    "Dublin", "Cork", "Galway", "Limerick", "Waterford", "Kilkenny",
    "Wexford", "Kildare", "Wicklow", "Meath", "Louth", "Clare",
    "Kerry", "Mayo", "Sligo", "Donegal", "Tipperary", "Carlow",
    "Laois", "Offaly", "Westmeath", "Longford", "Cavan", "Monaghan",
    "Roscommon", "Leitrim",
]


def extract_county(location_str: str | None) -> str | None:
    if not location_str:
        return None
    for county in IRISH_COUNTIES:
        if county.lower() in location_str.lower():
            return county
    return None


def parse_posted_date(date_str: str | None) -> datetime | None:
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


async def fetch_jobs(page: int = 1, category: str = None, location: str = None) -> dict:
    params = {
        "app_id": settings.adzuna_app_id,
        "app_key": settings.adzuna_app_key,
        "results_per_page": settings.adzuna_results_per_page,
        "page": page,
        "content-type": "application/json",
        "what": "",  # all jobs
        "where": location or "ireland",
    }
    if category:
        params["category"] = category

    url = f"{settings.adzuna_base_url}/search/{page}"

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        return resp.json()


async def fetch_categories() -> list[dict]:
    url = f"{settings.adzuna_base_url}/categories"
    params = {
        "app_id": settings.adzuna_app_id,
        "app_key": settings.adzuna_app_key,
    }
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        return resp.json().get("results", [])


def normalize_job(raw: dict) -> dict:
    location_display = raw.get("location", {}).get("display_name", "Ireland")
    county = extract_county(location_display)

    category = raw.get("category", {})

    return {
        "adzuna_id": str(raw.get("id", "")),
        "title": raw.get("title", "").strip(),
        "company": raw.get("company", {}).get("display_name", "Unknown"),
        "location": location_display,
        "county": county,
        "category": category.get("label"),
        "category_tag": category.get("tag"),
        "contract_type": raw.get("contract_type"),
        "contract_time": raw.get("contract_time"),
        "salary_min": raw.get("salary_min"),
        "salary_max": raw.get("salary_max"),
        "salary_predicted": raw.get("salary_is_predicted", "0") == "1",
        "description": raw.get("description", "").strip(),
        "redirect_url": raw.get("redirect_url"),
        "posted_date": parse_posted_date(raw.get("created")),
        "raw_data": raw,
    }
