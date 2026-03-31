from __future__ import annotations
import httpx
import asyncio
import re
from datetime import datetime, timedelta
from config import get_settings

settings = get_settings()

APIFY_BASE = "https://api.apify.com/v2"
ACTOR_ID = "bebity~linkedin-jobs-scraper"

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

# Ireland geoId on LinkedIn = 104738515
# Tech-first, then general Ireland searches
SEARCH_QUERIES = [
    {"searchUrl": "https://www.linkedin.com/jobs/search/?keywords=software+developer&location=Ireland&geoId=104738515", "count": 100},
    {"searchUrl": "https://www.linkedin.com/jobs/search/?keywords=data+engineer&location=Ireland&geoId=104738515",      "count": 80},
    {"searchUrl": "https://www.linkedin.com/jobs/search/?keywords=devops+cloud&location=Ireland&geoId=104738515",       "count": 80},
    {"searchUrl": "https://www.linkedin.com/jobs/search/?keywords=&location=Ireland&geoId=104738515",                   "count": 200},
    {"searchUrl": "https://www.linkedin.com/jobs/search/?keywords=&location=Dublin%2C+Ireland&geoId=104737327",         "count": 150},
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


def parse_linkedin_date(posted_at) -> datetime:
    if not posted_at:
        return None
    s = str(posted_at).lower().strip()
    if "just now" in s or "today" in s or "moment" in s:
        return datetime.utcnow()
    match = re.search(r"(\d+)\s*(second|minute|hour|day|week|month)", s)
    if match:
        n = int(match.group(1))
        unit = match.group(2)
        delta_map = {
            "second": timedelta(seconds=n),
            "minute": timedelta(minutes=n),
            "hour":   timedelta(hours=n),
            "day":    timedelta(days=n),
            "week":   timedelta(weeks=n),
            "month":  timedelta(days=n * 30),
        }
        return datetime.utcnow() - delta_map.get(unit, timedelta(0))
    try:
        return datetime.fromisoformat(str(posted_at).replace("Z", ""))
    except Exception:
        return None


def parse_salary(salary_text: str):
    if not salary_text:
        return None, None
    numbers = re.findall(r"[\d]+", salary_text.replace(",", ""))
    numbers = [int(n) for n in numbers if n and int(n) > 1000]
    if len(numbers) >= 2:
        return float(min(numbers)), float(max(numbers))
    elif len(numbers) == 1:
        return float(numbers[0]), float(numbers[0])
    return None, None


async def _run_actor(client: httpx.AsyncClient, input_data: dict) -> str:
    resp = await client.post(
        f"{APIFY_BASE}/acts/{ACTOR_ID}/runs",
        params={"token": settings.apify_api_token},
        json=input_data,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["data"]["id"]


async def _wait_for_run(client: httpx.AsyncClient, run_id: str, timeout_secs: int = 600) -> bool:
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
            print(f"[apify-linkedin] run {run_id} ended with status: {status}")
            return False
        await asyncio.sleep(15)
    print(f"[apify-linkedin] run {run_id} timed out")
    return False


async def _fetch_dataset(client: httpx.AsyncClient, run_id: str) -> list:
    resp = await client.get(
        f"{APIFY_BASE}/actor-runs/{run_id}/dataset/items",
        params={"token": settings.apify_api_token, "format": "json"},
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()


async def fetch_all_jobs() -> list:
    seen_ids: set = set()
    all_results: list = []

    async with httpx.AsyncClient() as client:
        for query in SEARCH_QUERIES:
            try:
                print(f"[apify-linkedin] starting run: {query['searchUrl'][:80]}")
                run_id = await _run_actor(client, query)
                success = await _wait_for_run(client, run_id)
                if not success:
                    continue
                items = await _fetch_dataset(client, run_id)
                for item in items:
                    jid = str(
                        item.get("id") or
                        item.get("jobId") or
                        item.get("linkedinUrl") or
                        item.get("url") or
                        ""
                    )
                    if jid and jid not in seen_ids:
                        seen_ids.add(jid)
                        all_results.append(item)
                print(f"[apify-linkedin] fetched={len(items)} total_unique={len(all_results)}")
            except Exception as e:
                print(f"[apify-linkedin] error: {e}")

    return all_results


def normalize_job(raw: dict) -> dict:
    title = (
        raw.get("title") or
        raw.get("positionName") or
        raw.get("jobTitle") or
        ""
    ).strip()

    company = (
        raw.get("company") or
        raw.get("companyName") or
        "Unknown"
    )

    location = raw.get("location") or raw.get("jobLocation") or "Ireland"
    if isinstance(location, dict):
        location = location.get("label") or location.get("city") or "Ireland"

    job_id = str(
        raw.get("id") or
        raw.get("jobId") or
        raw.get("linkedinUrl") or
        raw.get("url") or
        ""
    )

    redirect_url = (
        raw.get("applyUrl") or
        raw.get("url") or
        raw.get("linkedinUrl") or
        ""
    )

    salary_text = raw.get("salary") or raw.get("salaryInfo") or ""
    if isinstance(salary_text, list):
        salary_text = " ".join(salary_text)
    salary_min, salary_max = parse_salary(str(salary_text))

    contract_time = None
    emp_type = str(raw.get("contractType") or raw.get("employmentType") or "").lower()
    if "full" in emp_type:
        contract_time = "full_time"
    elif "part" in emp_type:
        contract_time = "part_time"
    elif "contract" in emp_type:
        contract_time = "contract"

    description = raw.get("description") or raw.get("descriptionHtml") or ""
    description = re.sub(r"<[^>]+>", " ", str(description)).strip()

    return {
        "adzuna_id": f"linkedin_{job_id}",
        "title": title,
        "company": company,
        "location": location,
        "county": extract_county(location),
        "category": classify_category(title),
        "category_tag": raw.get("sector") or raw.get("industries"),
        "contract_type": None,
        "contract_time": contract_time,
        "salary_min": salary_min,
        "salary_max": salary_max,
        "salary_predicted": False,
        "description": description,
        "redirect_url": redirect_url,
        "posted_date": parse_linkedin_date(raw.get("postedAt") or raw.get("publishedAt")),
        "raw_data": raw,
    }
