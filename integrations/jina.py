"""GitHub-based Document & Log Fetcher for demo purposes."""
import requests
from typing import Dict, Optional, List

class DocumentFetcher:
    """Fetches and parses runbooks from GitHub for demo."""

    def __init__(self):
        # Base URL of your GitHub raw repo
        self.github_base = "https://raw.githubusercontent.com/mak372/agentic-sre-sim-data/main"

    def fetch_runbook(self, service_name: str, incident_type: str) -> Dict[str, str]:
        """Fetch runbook documentation from GitHub repo."""

        runbook_files = {
            "latency_spike": f"{self.github_base}/runbooks/latency_spike.md",
            "error_rate_increase": f"{self.github_base}/runbooks/error_rate_increase.md",
            "resource_saturation": f"{self.github_base}/runbooks/resource_saturation.md",
            "queue_depth_growth": f"{self.github_base}/runbooks/queue_depth_growth.md",
        }

        url = runbook_files.get(incident_type)
        if not url:
            print(f"No runbook URL for incident type: {incident_type}")
            return self._get_default_runbooks()

        try:
            print(f"Fetching runbook from: {url}")
            content = self._fetch_from_github(url)

            if content:
                print(f"Fetched {len(content)} characters from runbook")
                return self._parse_runbook_content(content, incident_type)
            else:
                print(f"Failed to fetch runbook, using defaults")
                return self._get_default_runbooks()

        except Exception as e:
            print(f"Error fetching runbook: {e}")
            return self._get_default_runbooks()

    def _fetch_from_github(self, url: str) -> Optional[str]:
        """Fetch raw file content from GitHub."""
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                return resp.text
            else:
                print(f"GitHub returned {resp.status_code}")
                return None
        except Exception as e:
            print(f"GitHub fetch error: {e}")
            return None

    def _parse_runbook_content(self, content: str, incident_type: str) -> Dict[str, str]:
        """Return structured runbook."""
        summary = content[:500].replace("#", "").replace("*", "").strip()
        return {
            incident_type: summary,
            "source": "GitHub Demo Runbooks",
            "full_content": content[:2000],
        }

    def _get_default_runbooks(self) -> Dict[str, str]:
        """Fallback runbooks if GitHub fetch fails."""
        return {
            "latency_spike": "Default latency runbook steps...",
            "error_rate_increase": "Default error rate runbook steps...",
            "resource_saturation": "Default resource saturation runbook steps...",
            "queue_depth_growth": "Default queue depth runbook steps...",
            "source": "Default Demo Runbooks"
        }


class LogFetcher:
    """Fetch logs from GitHub for demo purposes."""

    def __init__(self):
        self.github_base = "https://raw.githubusercontent.com/mak372/agentic-sre-sim-data/main"

    def fetch_logs(self, service_name: str, incident_type: str) -> List[str]:
        """Fetch log file lines from GitHub."""
        url = f"{self.github_base}/{service_name}/{incident_type}.log"
        print(f"Fetching logs from: {url}")
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                return resp.text.splitlines()
            else:
                return [f"No logs found for {service_name} / {incident_type}"]
        except Exception as e:
            return [f"Log fetch error: {e}"]
