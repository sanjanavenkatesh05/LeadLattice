from googlesearch import search
import time
import random

class LinkedInDiscoverer:
    """
    Uses Google Search to find LinkedIn profiles for names and companies.
    Note: This depends on the 'googlesearch-python' library.
    """
    
    def find_profile(self, name: str, company: str = "", keywords: str = "") -> str:
        """
        Returns the best matching LinkedIn URL or None.
        """
        # Construct a targeted query
        query = f'site:linkedin.com/in "{name}"'
        if company:
            query += f' "{company}"'
        if keywords:
            query += f' "{keywords}"'
            
        print(f"🕵️ Searching for: {name} at {company}...")
        
        try:
            # Pause to be polite and avoid rate limits
            time.sleep(random.uniform(2.0, 5.0))
            
            # Search for top 1 result
            # num_results=1 is part of the generator config in newer versions, or we just take next()
            results = search(query, num_results=1, advanced=True)
            
            for result in results:
                # result is usually an object with .url, .title, .description in googlesearch-python
                # or just a string in the older googlesearch
                url = result.url if hasattr(result, 'url') else result
                
                if "linkedin.com/in" in url:
                    print(f"   -> Found: {url}")
                    return url
                    
            print("   -> No LinkedIn profile found.")
            return None
            
        except Exception as e:
            print(f"   -> Search error: {e}")
            return None

    def find_company_linkedin(self, company_name: str) -> str:
        query = f'site:linkedin.com/company "{company_name}"'
        try:
            time.sleep(random.uniform(1.5, 3.0))
            results = search(query, num_results=1)
            for url in results:
                if "linkedin.com/company" in url:
                    return url
            return None
        except:
            return None
