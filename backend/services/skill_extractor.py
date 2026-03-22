from __future__ import annotations
import spacy
from functools import lru_cache

# irish job market skill taxonomy
TECH_SKILLS = {
    "python", "javascript", "typescript", "java", "c#", "c++", "go", "rust",
    "react", "angular", "vue", "node.js", "django", "fastapi", "flask",
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ansible",
    "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
    "machine learning", "deep learning", "nlp", "data science", "tensorflow",
    "pytorch", "scikit-learn", "pandas", "sql", "spark", "kafka",
    "git", "ci/cd", "devops", "microservices", "rest api", "graphql",
    "linux", "bash", "jenkins", "github actions",
}

FINANCE_SKILLS = {
    "excel", "vba", "bloomberg", "sap", "oracle", "sage", "xero", "quickbooks",
    "ifrs", "gaap", "cpa", "acca", "cfa", "aml", "kyc", "risk management",
    "financial modelling", "investment banking", "audit", "tax", "treasury",
    "accounts payable", "accounts receivable", "management accounts",
}

HEALTHCARE_SKILLS = {
    "nursing", "midwifery", "physiotherapy", "occupational therapy",
    "speech therapy", "pharmacy", "clinical", "hse", "nmbi", "coru",
    "icu", "a&e", "theatre", "oncology", "paediatrics", "geriatrics",
    "mental health", "community care", "primary care", "gdpr healthcare",
}

CONSTRUCTION_SKILLS = {
    "autocad", "revit", "bim", "civil 3d", "project management",
    "quantity surveying", "structural engineering", "mechanical engineering",
    "electrical engineering", "h&s", "cdm", "riai", "engineers ireland",
    "site management", "planning permission", "building regulations",
}

GENERAL_SKILLS = {
    "project management", "agile", "scrum", "lean", "six sigma",
    "stakeholder management", "communication", "teamwork", "leadership",
    "salesforce", "microsoft 365", "sharepoint", "power bi", "tableau",
    "customer service", "account management", "business development",
}

ALL_SKILLS = (
    TECH_SKILLS | FINANCE_SKILLS | HEALTHCARE_SKILLS |
    CONSTRUCTION_SKILLS | GENERAL_SKILLS
)


@lru_cache(maxsize=1)
def get_nlp():
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        # model not downloaded yet
        return None


def extract_skills(text: str) -> list[str]:
    if not text:
        return []

    text_lower = text.lower()
    found = set()

    # simple substring matching for known skills
    for skill in ALL_SKILLS:
        if skill in text_lower:
            found.add(skill)

    # also run spacy ner for ORG entities (catches company-specific tech names)
    nlp = get_nlp()
    if nlp:
        doc = nlp(text[:2000])  # limit to 2k chars, descriptions can be long
        for ent in doc.ents:
            if ent.label_ in ("ORG", "PRODUCT") and len(ent.text) > 2:
                found.add(ent.text.lower())

    return sorted(found)
