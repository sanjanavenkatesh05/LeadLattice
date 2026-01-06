from agent.models import Lead

class ProbabilityEngine:
    def rank_leads(self, leads: list[Lead]) -> list[Lead]:
        """
        Applies scoring logic to a list of leads and sorts them by score descending.
        """
        for lead in leads:
            self._calculate_score(lead)
        
        # Sort by score descending
        return sorted(leads, key=lambda x: x.score, reverse=True)

    def _calculate_score(self, lead: Lead):
        score = 0
        breakdown = []

        # 1. Role Fit (+30)
        # Criteria: Title contains Toxicology, Safety, Hepatic, 3D
        # We also check the Company Name (Department)
        role_keywords = ["toxicology", "safety", "hepatic", "3d", "liver", "preclinical", "discovery", "researcher", "scientist"]
        text_to_check = (lead.title + " " + lead.company.name).lower()
        
        if any(k in text_to_check for k in role_keywords):
            score += 30
            match = next(k for k in role_keywords if k in text_to_check)
            breakdown.append(f"Role Fit (+30): Found '{match}'")

        # 2. Company Intent (+20)
        # Criteria: Recently raised Series A/B
        if lead.company.funding_stage in ["Series A", "Series B"]:
            score += 20
            breakdown.append(f"Company Intent (+20): Funding match '{lead.company.funding_stage}'")
        
        # 3. Technographic (+15 & +10)
        # Uses similar tech (+15)
        if lead.company.uses_invitro_tech:
            score += 15
            breakdown.append("Technographic (+15): Uses in-vitro tech")
        # Open to NAMs (+10)
        if lead.company.open_to_nams:
            score += 10
            breakdown.append("Technographic (+10): Open to NAMs")

        # 4. Location (+10)
        # Hubs: Boston, Cambridge, Bay Area, Basel, UK Golden Triangle + Intl
        hubs = [
            "boston", "cambridge", "bay area", "basel", "uk", "london", "oxford", "golden triangle", "san francisco", 
            "switzerland", "germany", "usa", "china", "japan", "new york", "san diego", "shanghai", "beijing", "tokyo"
        ]
        # Check both person location and HQ
        person_loc = lead.location_person.lower()
        hq_loc = lead.company.location_hq.lower()
        
        if any(h in person_loc for h in hubs) or any(h in hq_loc for h in hubs):
            score += 10
            match = next((h for h in hubs if h in person_loc or h in hq_loc), "Hub")
            breakdown.append(f"Location (+10): In Hub '{match}'")

        # 5. Scientific Intent (+40)
        # Paper on DILI in last 2 years (simulated by keyword presence in publications)
        scientific_keywords = [
            "drug-induced liver injury", "dili", "liver toxicity", "hepatotoxicity", 
            "hepatic spheroids", "organ-on-chip", "3d cell culture", "spheroid", "microphysiological"
        ]
        has_paper = False
        for paper in lead.publications:
            paper_lower = paper.lower()
            if any(k in paper_lower for k in scientific_keywords):
                has_paper = True
                match = next(k for k in scientific_keywords if k in paper_lower)
                breakdown.append(f"Scientific Intent (+40): Published on '{match}'")
                score += 40
                break 
        
        # Cap score at 100
        lead.score = min(score, 100)
        lead.score_breakdown = breakdown
        
        # Assign Tier
        if lead.score >= 80:
            lead.rank_tier = "Highest"
        elif lead.score >= 60:
            lead.rank_tier = "High"
        elif lead.score >= 40:
            lead.rank_tier = "Medium"
        else:
            lead.rank_tier = "Low"
            
        return lead.score
