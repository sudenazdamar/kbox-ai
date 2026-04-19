import time
import logging
from dataclasses import dataclass
from serpapi import GoogleSearch
from config import config

logger = logging.getLogger(__name__)

@dataclass
class ScholarResult:
    title: str
    authors: str
    year: str
    abstract: str
    link: str
    citations: int

class ScholarTool:
    def __init__(self, max_retries: int = 3, retry_delay: float = 2.0):
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def search(self, query: str, num_results: int = None) -> list[ScholarResult]:
        num_results = num_results or config.MAX_SCHOLAR_RESULTS
        for attempt in range(self.max_retries):
            try:
                return self._fetch_results(query, num_results)
            except Exception as e:
                wait_time = self.retry_delay * (2 ** attempt)
                logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
                if attempt < self.max_retries - 1:
                    time.sleep(wait_time)
                else:
                    logger.error("All retries exhausted.")
                    return []

    def _fetch_results(self, query: str, num_results: int) -> list[ScholarResult]:
        params = {
            "engine": "google_scholar",
            "q": query,
            "num": num_results,
            "api_key": config.SERPAPI_KEY,
        }
        search = GoogleSearch(params)
        raw = search.get_dict().get("organic_results", [])
        return [self._parse_result(r) for r in raw]

    def _parse_result(self, raw: dict) -> ScholarResult:
        pub_info = raw.get("publication_info", {})
        return ScholarResult(
            title=raw.get("title", "Unknown Title"),
            authors=pub_info.get("authors", [{}])[0].get("name", "Unknown Author")
                   if pub_info.get("authors") else "Unknown",
            year=pub_info.get("summary", "").split()[-1] if pub_info.get("summary") else "N/A",
            abstract=raw.get("snippet", "No abstract available."),
            link=raw.get("link", ""),
            citations=raw.get("inline_links", {}).get("cited_by", {}).get("total", 0),
        )

    def format_for_llm(self, results: list[ScholarResult]) -> str:
        if not results:
            return "No academic results found for this query."
        formatted = []
        for i, r in enumerate(results, 1):
            formatted.append(
                f"[{i}] {r.title}\n"
                f"    Authors: {r.authors} ({r.year})\n"
                f"    Abstract: {r.abstract}\n"
                f"    Citations: {r.citations} | URL: {r.link}"
            )
        return "\n\n".join(formatted)