"""TinyFish/Yutori integration for web agent capabilities.

TinyFish provides intelligent web browsing for:
- Pulling runbooks from internal wikis
- Scraping status pages
- Fetching documentation
- Extracting structured data from web sources
"""
import os
from typing import Dict, List, Optional


class TinyFishClient:
    """Client for TinyFish web agent API."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("TINYFISH_API_KEY", "")
        self.base_url = "https://api.tinyfish.io/v1"
    
    def fetch_runbook(self, service_name: str, incident_type: str) -> Dict[str, str]:
        """Fetch relevant runbooks for a service and incident type.
        
        Args:
            service_name: Name of the service
            incident_type: Type of incident
            
        Returns:
            Dict mapping runbook sections to content
        """
        # In production, use TinyFish to scrape internal wiki/docs
        # For demo, return simulated runbook
        
        runbooks = {
            "latency_spike": """
## Latency Spike Runbook

### Investigation Steps
1. Check database query performance in past 15 minutes
2. Review recent deployments
3. Check connection pool utilization
4. Review downstream service health

### Common Causes
- Slow database queries from recent code changes
- Connection pool exhaustion
- Downstream service degradation
- Missing indexes on frequently queried tables

### Mitigation Steps
1. Rollback recent deployment if correlation found
2. Scale up service replicas to distribute load
3. Add database query timeout if missing
4. Enable connection pool monitoring
            """,
            "error_rate": """
## Error Rate Spike Runbook

### Investigation Steps
1. Check error logs for common patterns
2. Verify downstream service health
3. Review recent configuration changes
4. Check network connectivity

### Common Causes
- Downstream dependency failure
- Configuration errors in recent deploy
- Network issues
- Database connection failures

### Mitigation Steps
1. Enable fallback mechanisms for failed dependencies
2. Rollback if configuration error identified
3. Scale up if capacity issue
4. Implement circuit breaker if not present
            """
        }
        
        return {
            "runbook": runbooks.get(incident_type, "No specific runbook found"),
            "source": f"Internal Wiki - {service_name}",
            "last_updated": "2026-01-10"
        }
    
    def scrape_status_page(self, url: str) -> Dict[str, str]:
        """Scrape a status page for service health information.
        
        Args:
            url: URL of the status page
            
        Returns:
            Structured status information
        """
        # In production, use TinyFish to scrape and extract structured data
        return {
            "status": "operational",
            "incidents": [],
            "last_checked": "2026-01-16T12:00:00Z"
        }
    
    def search_documentation(self, query: str) -> List[Dict[str, str]]:
        """Search documentation for relevant information.
        
        Args:
            query: Search query
            
        Returns:
            List of relevant documentation snippets
        """
        # In production, use TinyFish to search internal docs
        return [
            {
                "title": f"Documentation for: {query}",
                "snippet": "Relevant documentation content...",
                "url": "https://docs.internal.com/..." 
            }
        ]

