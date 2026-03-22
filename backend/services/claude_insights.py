from __future__ import annotations
import anthropic
from config import get_settings

settings = get_settings()


def get_client():
    return anthropic.Anthropic(api_key=settings.anthropic_api_key)


async def generate_market_insight(
    category: str,
    top_skills: list[str],
    job_count: int,
    avg_salary: float | None,
    county_breakdown: list[dict],
) -> dict:
    client = get_client()

    county_str = ", ".join(
        f"{c['county']} ({c['count']})" for c in county_breakdown[:5]
    )
    skills_str = ", ".join(top_skills[:15])
    salary_str = f"€{avg_salary:,.0f}" if avg_salary else "not available"

    prompt = f"""You are analyzing the Irish job market. Here is current data:

Category: {category}
Total jobs listed: {job_count}
Average salary: {salary_str}
Top locations: {county_str}
Most in-demand skills: {skills_str}

Based on this data, provide a concise Irish job market insight in JSON format with these exact keys:
- summary: 2-3 sentence market overview (be specific, mention Ireland context)
- top_skills: list of 5 most critical skills from the data
- skill_gaps: list of 3-4 skills likely to grow in demand based on current trends
- market_note: one sentence practical tip for job seekers in this category

Return only valid JSON, no markdown wrapping."""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}],
    )

    import json
    text = message.content[0].text.strip()
    return json.loads(text)


async def analyze_job_description(description: str, title: str) -> dict:
    client = get_client()

    prompt = f"""Analyze this Irish job posting and extract structured insight.

Job Title: {title}
Description: {description[:3000]}

Return JSON with:
- key_requirements: list of top 5 hard requirements
- nice_to_have: list of 3 nice-to-have skills
- seniority: one of junior/mid/senior/lead based on description
- remote_friendly: true/false based on description
- summary: 1 sentence plain-English summary of the role

Return only valid JSON."""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}],
    )

    import json
    text = message.content[0].text.strip()
    return json.loads(text)
