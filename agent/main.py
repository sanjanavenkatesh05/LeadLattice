import json
import os
from agent.generator import DataGenerator
from agent.ranker import ProbabilityEngine

def main():
    print("🚀 Starting LogicLattice Lead Generation Agent...")
    
    # 1. Generate Lead Data (Mock of scraping)
    print("\n[Phase 1] Scanning Professional Networks & Scientific Databases...")
    generator = DataGenerator()
    leads = generator.generate_sample_leads(count=500)
    print(f"   -> Identified {len(leads)} raw profiles.")

    # 2. Score & Rank
    print("\n[Phase 2] Analyzing & Ranking Candidates...")
    ranker = ProbabilityEngine()
    ranked_leads = ranker.rank_leads(leads)
    
    # 3. Export
    output_file = "dashboard/public/leads_data.json"
    # Also save to agent folder for reference
    backup_file = "agent/leads_ranked.json"
    
    data = [lead.model_dump() for lead in ranked_leads]
    
    # Ensure dir exists in case dashboard not init
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, "w") as f:
        json.dump(data, f, indent=2)
        
    with open(backup_file, "w") as f:
        json.dump(data, f, indent=2)
        
    print(f"\n✅ Done! Processed and ranked {len(ranked_leads)} leads.")
    print(f"   -> Saved to: {output_file}")

if __name__ == "__main__":
    main()
