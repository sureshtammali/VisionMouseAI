import requests
import webbrowser
import urllib.parse

class GoogleSearchComplete:
    def __init__(self):
        self.base_url = "http://suggestqueries.google.com/complete/search"
    
    def get_suggestions(self, query):
        """Get Google search suggestions for a query"""
        try:
            params = {
                'client': 'firefox',
                'q': query
            }
            response = requests.get(self.base_url, params=params, timeout=3)
            if response.status_code == 200:
                suggestions = response.json()[1][:5]  # Top 5 suggestions
                return suggestions
        except:
            pass
        return []
    
    def search_with_completion(self, query):
        """Search with auto-completion"""
        suggestions = self.get_suggestions(query)
        if suggestions:
            # Use first suggestion for auto-search
            search_query = suggestions[0]
        else:
            search_query = query
        
        url = f"https://www.google.com/search?q={urllib.parse.quote(search_query)}"
        webbrowser.open(url)
        return search_query, suggestions

# Global instance
google_complete = GoogleSearchComplete()