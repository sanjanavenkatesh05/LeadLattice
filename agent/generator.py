import random
import uuid
from agent.models import Lead, Company

class DataGenerator:
    def generate_sample_leads(self, count=500) -> list[Lead]:
        leads = []
        
        # Data Pools
        titles_high = ["Director of Toxicology", "Head of Preclinical Safety", "VP Safety Assessment", "Senior Scientist, Hepatic Models", "Principal Investigator, 3D Biology"]
        titles_low = ["Junior Researcher", "Lab Technician", "Postdoc Fellow", "Research Assistant", "intern"]
        
        companies_high = [
            {"name": "Vertex Pharma", "hq": "Boston, MA", "funding": "Public", "invitro": True},
            {"name": "Moderna", "hq": "Cambridge, MA", "funding": "Public", "invitro": True},
            {"name": "Hepatx Bio", "hq": "San Francisco, CA", "funding": "Series A", "invitro": True},
            {"name": "LiverChip Inc", "hq": "Basel, Switzerland", "funding": "Series B", "invitro": True},
        ]
        companies_low = [
            {"name": "Generic Chem Corp", "hq": "Austin, TX", "funding": None, "invitro": False},
            {"name": "OldSchool Meds", "hq": "Chicago, IL", "funding": "Public", "invitro": False},
            {"name": "Uni Research Lab", "hq": "Columbus, OH", "funding": "Grant", "invitro": False},
        ]
        
        locations = ["Boston, MA", "Cambridge, MA", "San Francisco, CA", "Remote, TX", "Remote, FL", "London, UK", "Basel, Switzerland", "Denver, CO"]
        
        papers = [
            "Assessment of Drug-Induced Liver Injury using 3D Spheroids",
            "Novel Organ-on-chip models for Toxicity",
            "General chemistry related to something else",
            "Study of lung cells in 2D",
            "Hepatic toxicity markers in rat models"
        ]

        for _ in range(count):
            # Weigh randomness to ensure we have some "Good" leads (approx 20%)
            is_good_target = random.random() < 0.2
            
            if is_good_target:
                title = random.choice(titles_high)
                comp_data = random.choice(companies_high)
                company = Company(
                    name=comp_data["name"],
                    industry="Biotech",
                    location_hq=comp_data["hq"],
                    funding_stage=comp_data["funding"],
                    uses_invitro_tech=comp_data["invitro"],
                    open_to_nams=True
                )
                publications = [random.choice(papers[:2])] if random.random() < 0.6 else [] # 60% chance of paper
            else:
                title = random.choice(titles_low)
                comp_data = random.choice(companies_low)
                company = Company(
                    name=comp_data["name"],
                    industry="Pharma",
                    location_hq=comp_data["hq"],
                    funding_stage=comp_data["funding"],
                    uses_invitro_tech=comp_data["invitro"],
                    open_to_nams=random.random() < 0.3
                )
                publications = [random.choice(papers[2:])] if random.random() < 0.1 else []

            # Randomize Person Location logic
            if "Remote" in random.choice(locations):
                loc_person = random.choice(["Remote, TX", "Remote, CO", "Remote, FL"])
            else:
                # Often same as HQ for non-remote
                loc_person = company.location_hq if random.random() < 0.7 else random.choice(locations)

            first_name = random.choice(["Sarah", "John", "Emily", "Michael", "David", "Jessica", "Robert", "Jennifer"])
            last_name = random.choice(["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"])
            
            lead = Lead(
                id=str(uuid.uuid4()),
                name=f"{first_name} {last_name}",
                title=title,
                company=company,
                location_person=loc_person,
                email=f"{first_name.lower()}.{last_name.lower()}@{company.name.lower().replace(' ', '')}.com",
                linkedin_url=f"linkedin.com/in/{first_name.lower()}{last_name.lower()}",
                publications=publications
            )
            leads.append(lead)
            
        return leads
