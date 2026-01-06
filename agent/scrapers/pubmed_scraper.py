import requests
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Dict, Optional

class PubMedScraper:
    """
    Scrapes PubMed for recent articles to identify active researchers and companies
    in specific toxicology/biology fields.
    """
    
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    
    def __init__(self, email: str = "agent@leadlattice.ai"):
        # NCBI requires an email parameter for contact if we hit rate limits
        self.email = email

    def search_articles(self, keywords: List[str], max_results: int = 20) -> List[str]:
        """
        Search for articles matching keywords and return list of PubMed IDs (PMIDs).
        Focuses on last 2 years.
        """
        # Construct query: (Keyword1 OR Keyword2) AND ("2024"[Date - Publication] : "3000"[Date - Publication])
        # Using a simpler date filter for last 2 years approx
        term = "(" + " OR ".join(keywords) + ")"
        term += ' AND ("2023/01/01"[Date - Publication] : "3000"[Date - Publication])'
        
        params = {
            "db": "pubmed",
            "term": term,
            "retmode": "json",
            "retmax": max_results,
            "email": self.email
        }
        
        try:
            response = requests.get(f"{self.BASE_URL}/esearch.fcgi", params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("esearchresult", {}).get("idlist", [])
        except Exception as e:
            print(f"Error searching PubMed: {e}")
            return []

    def fetch_details(self, pmids: List[str]) -> List[Dict]:
        """
        Fetch detailed info for a list of PMIDs.
        Extracts: Title, Authors, Affiliation (Company/Uni).
        """
        if not pmids:
            return []
            
        all_articles = []
        chunk_size = 200
        
        for i in range(0, len(pmids), chunk_size):
            chunk = pmids[i:i + chunk_size]
            
            params = {
                "db": "pubmed",
                "id": ",".join(chunk),
                "retmode": "xml",
                "email": self.email
            }
            
            try:
                response = requests.post(f"{self.BASE_URL}/efetch.fcgi", data=params) # Use POST for large ID lists
                response.raise_for_status()
                
                # Parse XML
                root = ET.fromstring(response.content)
                
                for article in root.findall(".//PubmedArticle"):
                    try:
                        title_node = article.find(".//ArticleTitle")
                        title = title_node.text if (title_node is not None and title_node.text) else "No Title"
                        
                        authors_list = []
                        affiliations = set()
                        
                        
                        for author in article.findall(".//Author"):
                            last_name = author.find("LastName")
                            fore_name = author.find("ForeName")
                            
                            if last_name is not None and fore_name is not None:
                                full_name = f"{fore_name.text} {last_name.text}"
                                authors_list.append(full_name)
                                
                                # Get affiliation info to find Companies & Emails
                                aff_node = author.find(".//Affiliation")
                                if aff_node is not None:
                                    aff_text = aff_node.text
                                    affiliations.add(aff_text)
                                    
                                    # Try to find email in affiliation
                                    # Regex for simple email extraction
                                    emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', aff_text)
                                    if emails:
                                        found_email = emails[0]
                                        # Map author to email (simple heuristic: associate with current author)
                                        # In a strict sense we should store this better, but for now let's just 
                                        # add it to a list or a map. Simpler: just return a list of emails found.

                        # Extract emails from all affiliations collected
                        all_emails = []
                        for aff in affiliations:
                             found = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', aff)
                             all_emails.extend(found)
                        
                        # Remove trailing dot if present (common in pubmed data like "email@domain.com.")
                        all_emails = [e.rstrip('.') for e in all_emails]
    
                        all_articles.append({
                            "title": title,
                            "authors": authors_list,
                            "affiliations": list(affiliations),
                            "emails": list(set(all_emails)), # Return unique emails found
                            "source": "PubMed",
                            "url": f"https://pubmed.ncbi.nlm.nih.gov/{article.find('.//PMID').text}/"
                        })
                        
                    except Exception as parse_e:
                        continue
                        
            except Exception as e:
                print(f"Error fetching details for chunk {i}: {e}")
                continue
                
        return all_articles

    def get_leads_from_papers(self, keywords: List[str], limit: int = 10):
        print(f"Searching PubMed for: {keywords}...")
        pmids = self.search_articles(keywords, max_results=limit)
        print(f"Found {len(pmids)} articles. Fetching details...")
        details = self.fetch_details(pmids)
        return details
