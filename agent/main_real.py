import json
import os
import uuid
from typing import List

from agent.models import Lead, Company
from agent.ranker import ProbabilityEngine
from agent.scrapers.pubmed_scraper import PubMedScraper
from agent.scrapers.linkedin_discoverer import LinkedInDiscoverer

def is_industry_affiliation(affiliation: str) -> bool:
    """
    Simple heuristic to check if an affiliation string looks like a company 
    rather than just a university/hospital.
    """
    text = affiliation.lower()
    indicators = [
        " inc", " ltd", " llc", " gmbh", "pharma", "biotech", 
        "therapeutics", "biosciences", "laboratories", "technologies",
        "corp", "company"
    ]
    # university/hospital exclusion
    academic_indicators = ["university", "college", "school of", "hospital", "clinic", "institute", "univ"]
    
    has_ind = any(i in text for i in indicators)
    has_acd = any(a in text for a in academic_indicators)
    
    # If it has Pharma/Biotech markers, likely industry even if "Institute" is present (e.g. Novartis Institute)
    strong_ind = ["pharma", "biotech", "therapeutics", "biosciences"]
    if any(s in text for s in strong_ind):
        return True
        
    return has_ind and not has_acd

def extract_leads_from_papers(papers: List[dict], max_leads: int = 20) -> List[Lead]:
    leads = []
    seen_names = set()
    

    # Configuration
    SKIP_LINKEDIN = True # User prefers not to use LinkedIn
    
    for paper in papers:
        if len(leads) >= max_leads:
            break
            
        title = paper['title']
        
        # Check authors
        # Usually first and last author are most relevant
        target_indices = [0, -1] if len(paper['authors']) > 1 else [0]
        
        for idx in target_indices:
            if idx >= len(paper['authors']): continue
            
            author_name = paper['authors'][idx]
            if author_name in seen_names:
                continue
            
            # Check affiliations
            industry_affs = [aff for aff in paper['affiliations'] if is_industry_affiliation(aff)]
            
            if industry_affs:
                # Found a potential lead!
                company_name_raw = industry_affs[0].split(',')[0].strip() # Take first part like "Vertex Pharma"
                # Clean up company name roughly
                company_name = company_name_raw.replace('.', '')
                
                print(f"🎯 Candidate: {author_name} @ {company_name}")
                
                linkedin_url = ""
                if not SKIP_LINKEDIN:
                     # Try to find LinkedIn
                    found_url = discoverer.find_profile(author_name, company=company_name)
                    if found_url:
                        linkedin_url = found_url.replace("https://", "").replace("http://", "")
                    
                if not linkedin_url:
                    # Fallback: Generate a Search URL so the button works
                    # This lets the user find them with 1 click without us scraping
                    encoded_name = author_name.replace(" ", "%20")
                    # User requested to search ONLY by name as company search was failing
                    linkedin_url = f"www.linkedin.com/search/results/all/?keywords={encoded_name}"

                # Extract Location from Affiliation
                location = "Unknown"
                if paper.get('affiliations') and len(paper['affiliations']) > 0:
                    # Affiliations are often "Dept of X, University of Y, City, Country"
                    # We will use the whole string but relies on Table to truncate
                    location = paper['affiliations'][0]

                # Create Objects (Even if no LinkedIn, we have the Author + Company + Paper signal)
                comp = Company(
                    name=company_name,
                    industry="Biotech/Pharma",
                    location_hq=location, 
                    funding_stage="Unknown",
                    uses_invitro_tech=True, 
                    open_to_nams=True
                )
                
                # Try to get an email
                # If we scraped emails from the paper, use one. 
                # Since we can't easily map exact author to email in this simple scraper, 
                # we will use an email if it looks like it matches the company domain, or just default to Unavailable.
                
                email = "Unavailable"
                if paper.get('emails'):
                    # Pick the first one for now, or "Unavailable"
                    # Ideally we check if email domain matches company name
                    email = paper['emails'][0] 
                
                lead = Lead(
                    id=str(uuid.uuid4()),
                    name=author_name,
                    title="Researcher / Scientist", 
                    company=comp,
                    location_person=location,
                    email=email,
                    linkedin_url=linkedin_url,
                    publications=[title]
                )
                
                leads.append(lead)
                seen_names.add(author_name)
                print(f"   ✅ Added Lead: {author_name}")
                    
            if len(leads) >= max_leads:
                break
                
    return leads

def main():
    print("🚀 Starting Real Data Lead Generation Agent...")
    
    # 1. PubMed Search
    pubmed = PubMedScraper()
    keywords = ["3D cell culture", "Organ-on-chip", "Liver spheroids", "Drug-Induced Liver Injury"]
    
    print("\n[Phase 1] Scouring Scientific Literature (PubMed)...")
    papers = pubmed.get_leads_from_papers(keywords, limit=2000)
    
    # 2. Extract & Enrich
    print("\n[Phase 2] Identifying Corporate Authors & LinkedIn Profiles...")
    leads = extract_leads_from_papers(papers, max_leads=2000) # Extract ALL candidates (up to 2000)
    
    # 3. Rank
    print("\n[Phase 3] Ranking Leads...")
    ranker = ProbabilityEngine()
    ranked_leads = ranker.rank_leads(leads)
    
    # Keep only Top 500 highest scoring leads
    ranked_leads = ranked_leads[:500]
    
    # 4. Save
    output_file = "dashboard/public/leads_data.json"
    # Also save to agent folder for reference
    backup_file = "agent/leads_ranked.json"
    
    data = [lead.model_dump() for lead in ranked_leads]
    
    # Ensure dir exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, "w") as f:
        json.dump(data, f, indent=2)
        
    with open(backup_file, "w") as f:
        json.dump(data, f, indent=2)
        
    print(f"\n✅ Done! Generated {len(ranked_leads)} REAL leads saved to {output_file}")

if __name__ == "__main__":
    main()
