from typing import List, Optional
from pydantic import BaseModel

class Company(BaseModel):
    name: str
    industry: str
    location_hq: str
    funding_stage: Optional[str] = None # e.g., "Series A", "Series B", "Public"
    uses_invitro_tech: bool = False
    open_to_nams: bool = False # New Approach Methodologies

class Lead(BaseModel):
    id: str
    name: str
    title: str
    company: Company
    location_person: str # "Remote, TX" or "Cambridge, MA"
    email: str
    linkedin_url: str
    phone: Optional[str] = None
    
    # Logic specific fields
    publications: List[str] = [] # List of paper titles/keywords
    
    # Output fields
    score: float = 0.0
    score_breakdown: List[str] = []
    rank_tier: str = "Low" # Low, Medium, High, Very High

class GeneratedData(BaseModel):
    leads: List[Lead]
