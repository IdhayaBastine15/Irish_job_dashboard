from __future__ import annotations
import httpx
from datetime import datetime
from config import get_settings

settings = get_settings()

REED_BASE_URL = "https://www.reed.co.uk/api/1.0"

IRISH_COUNTIES = [
    "Dublin", "Cork", "Galway", "Limerick", "Waterford", "Kilkenny",
    "Wexford", "Kildare", "Wicklow", "Meath", "Louth", "Clare",
    "Kerry", "Mayo", "Sligo", "Donegal", "Tipperary", "Carlow",
    "Laois", "Offaly", "Westmeath", "Longford", "Cavan", "Monaghan",
    "Roscommon", "Leitrim",
]

# keyword → category mapping (checked in order, first match wins)
CATEGORY_RULES = [
    ("IT & Technology",       ["developer", "software", "engineer", "devops", "cloud", "data", "python", "java", "frontend", "backend", "fullstack", "full stack", "qa ", "tester", "testing", "cybersecurity", "network", "sysadmin", "it support", "machine learning", "artificial intelligence", " ai ", "architect", "scrum", "agile", "php", "react", "angular", "typescript", "javascript", "infrastructure", "platform", "site reliability", "mobile"]),
    ("Healthcare",            ["nurse", "doctor", "carer", "care assistant", "physician", "therapist", "pharmacist", "medical", "clinical", "dental", "optician", "audiologist", "hearing aid", "healthcare", "nhs", "gp ", "consultant", "midwife", "radiographer", "paramedic", "occupational"]),
    ("Finance & Accounting",  ["accountant", "finance", "financial", "analyst", "banking", "investment", "tax", "audit", "payroll", "treasury", "credit", "underwriter", "actuary", "accounts"]),
    ("Sales & Marketing",     ["sales", "marketing", "account manager", "business development", "seo", "digital marketing", "social media", "brand", "campaign", "e-commerce", "ecommerce", "growth"]),
    ("Engineering",           ["mechanical", "electrical", "civil", "structural", "manufacturing", "process engineer", "chemical engineer", "embedded", "hardware", "firmware", "autocad"]),
    ("Education & Training",  ["teacher", "lecturer", "tutor", "trainer", "education", "teaching", "academic", "professor", "school", "learning"]),
    ("HR & Recruitment",      ["hr ", "human resources", "recruiter", "recruitment", "talent", "people partner", "people ops", "compensation"]),
    ("Customer Service",      ["customer service", "customer support", "helpdesk", "help desk", "call centre", "contact centre", "service advisor"]),
    ("Construction & Trades", ["construction", "electrician", "plumber", "carpenter", "builder", "site manager", "quantity surveyor", "foreman", "bricklayer", "joiner", "trades"]),
    ("Logistics & Transport", ["driver", "logistics", "warehouse", "supply chain", "delivery", "transport", "freight", "haulage", "fleet"]),
    ("Legal & Compliance",    ["solicitor", "legal", "lawyer", "paralegal", "compliance", "regulatory", "gdpr", "in-house counsel"]),
    ("Management",            ["operations manager", "general manager", "managing director", "chief", "head of", "vp ", "vice president", "director of", "programme manager", "project manager"]),
    ("Admin & Office",        ["administrator", "admin", "receptionist", "office manager", "secretary", "pa ", "personal assistant", "coordinator", "clerk"]),
    ("Science & Research",    ["scientist", "researcher", "biologist", "chemist", "laboratory", "research", "r&d", "genomics", "biotech"]),
]


def classify_category(title: str) -> str:
    t = title.lower()
    for category, keywords in CATEGORY_RULES:
        if any(kw in t for kw in keywords):
            return category
    return "Other"


def extract_county(location_str: str | None) -> str | None:
    if not location_str:
        return None
    for county in IRISH_COUNTIES:
        if county.lower() in location_str.lower():
            return county
    return None


def parse_reed_date(date_str: str | None) -> datetime | None:
    if not date_str:
        return None
    for fmt in ("%d/%m/%Y", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(date_str, fmt)
        except (ValueError, AttributeError):
            continue
    return None


# Search multiple Irish locations to maximise coverage
SEARCH_LOCATIONS = ["Ireland", "Dublin", "Cork", "Galway", "Limerick", "Waterford"]


async def _fetch_page(client: httpx.AsyncClient, location: str, skip: int) -> list:
    params = {
        "locationName": location,
        "resultsToTake": settings.reed_results_per_page,
        "resultsToSkip": skip,
    }
    resp = await client.get(f"{REED_BASE_URL}/search", params=params, auth=(settings.reed_api_key, ""))
    resp.raise_for_status()
    return resp.json().get("results", [])


async def fetch_all_jobs() -> list:
    """Fetch jobs across all Irish search locations, deduped by jobId."""
    seen_ids: set = set()
    all_results: list = []

    async with httpx.AsyncClient(timeout=30) as client:
        for location in SEARCH_LOCATIONS:
            for page in range(1, settings.reed_max_pages + 1):
                skip = (page - 1) * settings.reed_results_per_page
                results = await _fetch_page(client, location, skip)
                if not results:
                    break
                for job in results:
                    jid = str(job.get("jobId", ""))
                    if jid and jid not in seen_ids:
                        seen_ids.add(jid)
                        all_results.append(job)

    return all_results


def normalize_job(raw: dict) -> dict:
    location = raw.get("locationName", "Ireland")
    title = (raw.get("jobTitle") or "").strip()
    county = extract_county(location)

    return {
        "adzuna_id": str(raw.get("jobId", "")),
        "title": title,
        "company": raw.get("employerName") or "Unknown",
        "location": location,
        "county": county,
        "category": classify_category(title),
        "category_tag": None,
        "contract_type": raw.get("contractType"),
        "contract_time": "full_time" if raw.get("fullTime") else ("part_time" if raw.get("partTime") else None),
        "salary_min": raw.get("minimumSalary"),
        "salary_max": raw.get("maximumSalary"),
        "salary_predicted": False,
        "description": (raw.get("jobDescription") or "").strip(),
        "redirect_url": raw.get("jobUrl"),
        "posted_date": parse_reed_date(raw.get("date")),
        "raw_data": raw,
    }
