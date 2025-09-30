"""Simple data models for the Webtoon Subscriber Tracker."""

from dataclasses import dataclass
from typing import Dict, Optional
from utils.formatters import get_current_month_key

@dataclass
class WebtoonInfo:
  """Basic info about a webtoon (from web scraping)."""
  title: str
  subscribers: int
  url: str

@dataclass
class WebtoonData:
  """Complete data for a tracked webtoon."""
  title: str
  url: str
  monthly_data: Dict[str, int]  # "2024-09" -> 123456
  
  def get_latest_subscribers(self) -> Optional[int]:
    """Get most recent subscriber count, or None if no data."""
    if not self.monthly_data:
      return None
    latest_month = sorted(self.monthly_data.keys())[-1]
    return self.monthly_data[latest_month]
  
  def add_current_month_data(self, subscribers: int) -> None:
    """Add subscriber data for the current month."""
    current_month = get_current_month_key()
    self.monthly_data[current_month] = subscribers

class WebtoonDatabase:
    """Manages all webtoon data."""
    
    def __init__(self):
      self._webtoons: Dict[str, WebtoonData] = {}
    
    def load_from_dict(self, data: Dict) -> None:
      """Load from your existing JSON format."""
      for url, info in data.items():
        self._webtoons[url] = WebtoonData(
          title=info["title"],
          url=url,
          monthly_data=info.get("data", {})
        )
    
    def to_dict(self) -> Dict:
      """Convert back to your JSON format."""
      result = {}
      for url, webtoon in self._webtoons.items():
        result[url] = {
          "title": webtoon.title,
          "data": webtoon.monthly_data
        }
      return result
    
    def add_webtoon(self, webtoon_info: WebtoonInfo) -> None:
      """Add a new webtoon."""
      if webtoon_info.url not in self._webtoons:
        self._webtoons[webtoon_info.url] = WebtoonData(
          title=webtoon_info.title,
          url=webtoon_info.url,
          monthly_data={}
        )
      self._webtoons[webtoon_info.url].add_current_month_data(webtoon_info.subscribers)
    
    def remove_webtoon(self, url: str) -> bool:
      """Remove a webtoon. Returns True if found and removed."""
      if url in self._webtoons:
        del self._webtoons[url]
        return True
      return False
    
    def get_all_webtoons(self) -> Dict[str, WebtoonData]:
      """Get all webtoons."""
      return self._webtoons.copy()
    
    def get_webtoon(self, url: str) -> Optional[WebtoonData]:
      """Get a specific webtoon by URL."""
      return self._webtoons.get(url)
    
    def get_urls(self) -> list:
      """Get all webtoon URLs."""
      return list(self._webtoons.keys())