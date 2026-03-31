from __future__ import annotations
import httpx
import asyncio
import re
from datetime import datetime, timedelta
from config import get_settings

settings = get_settings()

APIFY_BASE = "https://api.apify.com/v2"
ACTOR_ID = "misceres~indeed-scraper"

IRISH_COUNTIES = [
    "Dublin", "Cork", "Galway", "Limerick", "Waterford", "Kilkenny",
    "Wexford", "Kildare", "Wicklow", "Meath", "Louth", "Clare",
    "Kerry", "Mayo", "Sligo", "Donegal", "Tipperary", "Carlow",
    "Laois", "Offaly", "Westmeath", "Longford", "Cavan", "Monaghan",
    "Roscommon", "Leitrim",
]

CATEGORY_RULES = [
    ("IT & Technology",       ["developer", "software", "engineer", "devops", "cloud", "data", "python", "java", "frontend", "backend", "fullstack", "full stack", "qa ", "tester", "testing", "cybersecurity", "network", "sysadmin", "it support", "machine learning", "artificial intelligence", " ai ", "architect", "scrum", "agile", "php", "react", "angular", "typescript", "javascript", "infrastructure", "platform", "site reliability", "mobile"]),
    ("Healthcare",            ["nurse", "doctor", "carer", "care assistant", "physician", "therapist", "pharmacist", "medical", "clinical", "dental", "optician", "audiologist", "healthcare", "gp ", "consultant", "midwife", "radiographer", "paramedic", "occupational"]),
    ("Finance & Accounting",  ["accountant", "finance", "financial", "analyst", "banking", "investment", "tax", "audit", "payroll", "treasury", "credit", "underwriter", "actuary", "accounts"]),
    ("Sales & Marketing",     ["sales", "marketing", "account manager", "business development", "seo", "digital marketing", "social media", "brand", "campaign", "e-commerce", "ecommerce", "growth"]),
    ("Engineering",           ["mechanical", "electrical", "civil", "structural", "manufacturing", "process engineer", "chemical engineer", "embedded", "hardware", "firmware", "autocad"]),
    ("Education & Training",  ["teacher", "lecturer", "tutor", "trainer", "education", "teaching", "academic", "professor", "school", "learning"]),
    ("HR & Recruitment",      ["hr ", "human resources", "recruiter", "recruitment", "talent", "people partner", "people ops", "compensation"]),
    ("Customer Service",      ["customer service", "customer support", "helpdesk", "help desk", "call centre", "contact centre", "service advisor"]),
    ("Construction & Trades", ["construction", "electrician", "plumber", "carpenter", "builder", "site manager", "quantity surveyor", "foreman", "bricklayer", "joiner", "trades"]),
    ("Logistics & Transport", ["driver", "logistics", "warehouse", "supply chain", "delivery", "transport", "freight", "haulage", "fleet"]),
    ("Legal & Compliance",    ["solicitor", "legal", "lawyer", "paralegal", "compliance", "regulatory", "gdpr"]),
    ("Management",            ["operations manager", "general manager", "managing director", "chief", "head of", "vp ", "vice president", "director of", "programme manager", "project manager"]),
    ("Admin & Office",        ["administrator", "admin", "receptionist", "office manager", "secretary", "pa ", "personal assistant", "coordinator", "clerk"]),
    ("Science & Research",    ["scientist", "researcher", "biologist", "chemist", "laboratory", "research", "r&d", "genomics", "biotech"]),
]

# Tech and engineering searches run first to ensure best coverage of those roles.
# Generic location searches follow to fill in other categories.
SEARCH_QUERIES = [
    {"country": "IE", "location": "Ireland", "position": "software developer",    "maxItems": 100},
    {"country": "IE", "location": "Ireland", "position": "data engineer",         "maxItems": 80},
    {"country": "IE", "location": "Ireland", "position": "devops cloud",          "maxItems": 80},
    {"country": "IE", "location": "Ireland", "position": "mechanical electrical engineer", "maxItems": 80},
    {"country": "IE", "location": "Ireland", "position": "",                      "maxItems": 200},
    {"country": "IE", "location": "Dublin",  "position": "",                      "maxItems": 150},
    {"country": "IE", "location": "Cork",    "position": "",                      "maxItems": 100},
]


def classify_category(title: str) -> str:
    t = title.lower()
    for category, keywords in CATEGORY_RULES:
        if any(kw in t for kw in keywords):
            return category
    return "Other"


def extract_county(location_str: str) -> str:
    if not location_str:
        return None
    for county in IRISH_COUNTIES:
        if county.lower() in location_str.lower():
            return county
    return None


def parse_indeed_date(posted_at: str) -> datetime:
    """Convert Indeed relative dates like '2 days ago' to datetime."""
    if not posted_at:
        return None
    posted_at = posted_at.lower().strip()
    if "just posted" in posted_at or "today" in posted_at:
        return datetime.utcnow()
    match = re.search(r"(\d+)\s*(day|hour|minute)", posted_at)
    if match:
        n = int(match.group(1))
        unit = match.group(2)
        if unit == "day":
            return datetime.utcnow() - timedelta(days=n)
        elif unit == "hour":
            return datetime.utcnow() - timedelta(hours=n)
        elif unit == "minute":
            return datetime.utcnow() - timedelta(minutes=n)
    # Try ISO parse as fallback
    try:
        return datetime.fromisoformat(posted_at.replace("z", ""))
    except Exception:
        return None


def parse_salary(salary_text: str):
    """Extract min/max from salary strings like '€40,000 - €60,000 a year'."""
    if not salary_text:
        return None, None
    numbers = re.findall(r"[\d,]+", salary_text.replace(",", ""))
    numbers = [int(n) for n in numbers if n]
    if len(numbers) >= 2:
        return float(min(numbers)), float(max(numbers))
    elif len(numbers) == 1:
        return float(numbers[0]), float(numbers[0])
    return None, None


async def _run_actor(client: httpx.AsyncClient, input_data: dict) -> str:
    """Start an Apify actor run and return run ID."""
    resp = await client.post(
        f"{APIFY_BASE}/acts/{ACTOR_ID}/runs",
        params={"token": settings.apify_api_token},
        json=input_data,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["data"]["id"]


async def _wait_for_run(client: httpx.AsyncClient, run_id: str, timeout_secs: int = 600) -> bool:
    """Poll run status until SUCCEEDED or failed."""
    deadline = asyncio.get_event_loop().time() + timeout_secs
    while asyncio.get_event_loop().time() < deadline:
        resp = await client.get(
            f"{APIFY_BASE}/actor-runs/{run_id}",
            params={"token": settings.apify_api_token},
            timeout=30,
        )
        resp.raise_for_status()
        status = resp.json()["data"]["status"]
        if status == "SUCCEEDED":
            return True
        if status in ("FAILED", "ABORTED", "TIMED-OUT"):
            print(f"[apify] run {run_id} ended with status: {status}")
            return False
        await asyncio.sleep(15)
    print(f"[apify] run {run_id} timed out waiting")
    return False


async def _fetch_dataset(client: httpx.AsyncClient, run_id: str) -> list:
    """Fetch all items from a completed run's dataset."""
    resp = await client.get(
        f"{APIFY_BASE}/actor-runs/{run_id}/dataset/items",
        params={"token": settings.apify_api_token, "format": "json"},
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()


async def fetch_all_jobs() -> list:
    """Run Apify Indeed scraper for multiple Irish locations, dedupe by job ID."""
    seen_ids: set = set()
    all_results: list = []

    async with httpx.AsyncClient() as client:
        for query in SEARCH_QUERIES:
            try:
                print(f"[apify] starting run: location={query['location']} maxItems={query['maxItems']}")
                run_id = await _run_actor(client, query)
                success = await _wait_for_run(client, run_id)
                if not success:
                    continue
                items = await _fetch_dataset(client, run_id)
                for item in items:
                    jid = str(
                        item.get("id") or
                        item.get("jobId") or
                        item.get("url") or
                        ""
                    )
                    if jid and jid not in seen_ids:
                        seen_ids.add(jid)
                        all_results.append(item)
                print(f"[apify] location={query['location']} fetched={len(items)} total_unique={len(all_results)}")
            except Exception as e:
                print(f"[apify] error for location={query['location']}: {e}")

    return all_results


def normalize_job(raw: dict) -> dict:
    title = (
        raw.get("positionName") or
        raw.get("title") or
        raw.get("jobTitle") or
        ""
    ).strip()

    company = (
        raw.get("company") or
        raw.get("companyName") or
        raw.get("employer") or
        "Unknown"
    )

    location = (
        raw.get("location") or
        raw.get("jobLocation") or
        raw.get("locationName") or
        "Ireland"
    )
    if isinstance(location, dict):
        location = location.get("label") or location.get("city") or "Ireland"

    job_id = str(
        raw.get("id") or
        raw.get("jobId") or
        raw.get("url") or
        ""
    )

    redirect_url = (
        raw.get("externalApplyLink") or
        raw.get("url") or
        raw.get("jobUrl") or
        ""
    )

    salary_text = raw.get("salary") or raw.get("salaryText") or ""
    salary_min, salary_max = parse_salary(salary_text)

    job_type = raw.get("jobType") or []
    if isinstance(job_type, list):
        job_type = job_type[0] if job_type else None
    contract_time = None
    if job_type:
        jt = str(job_type).lower()
        if "full" in jt:
            contract_time = "full_time"
        elif "part" in jt:
            contract_time = "part_time"
        elif "contract" in jt:
            contract_time = "contract"

    description = raw.get("description") or raw.get("jobDescription") or ""
    # Strip HTML tags from description
    description = re.sub(r"<[^>]+>", " ", description).strip()

    return {
        "adzuna_id": f"indeed_{job_id}",
        "title": title,
        "company": company,
        "location": location,
        "county": extract_county(location),
        "category": classify_category(title),
        "category_tag": None,
        "contract_type": None,
        "contract_time": contract_time,
        "salary_min": salary_min,
        "salary_max": salary_max,
        "salary_predicted": False,
        "description": description,
        "redirect_url": redirect_url,
        "posted_date": parse_indeed_date(raw.get("postedAt") or raw.get("datePosted")),
        "raw_data": raw,
    }
