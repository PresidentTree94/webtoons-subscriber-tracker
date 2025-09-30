"""Business logic for managing webtoon operations."""

from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor
from storage.data_manager import DataManager
from scraping.scraper import WebtoonScraper
from utils.formatters import normalize_title_for_sorting

class WebtoonManager:
  """Manages webtoon operations and business logic."""
  
  def __init__(self):
    self.database = DataManager.load_database()
    self.scraper = WebtoonScraper()
  
  def add_webtoon(self, url: str) -> bool:
    """Add a new webtoon by URL."""
    webtoon_info = self.scraper.scrape_webtoon_info(url)
    if webtoon_info:
      self.database.add_webtoon(webtoon_info)
      self._save_database()
      return True
    return False
  
  def remove_webtoon(self, url: str) -> bool:
    """Remove a webtoon by URL."""
    if self.database.remove_webtoon(url):
      self._save_database()
      return True
    return False
  
  def update_all_webtoons(self) -> None:
    """Update subscriber data for all webtoons."""
    urls = self.database.get_urls()
    
    def fetch_and_update(url: str) -> None:
      webtoon_info = self.scraper.scrape_webtoon_info(url)
      if webtoon_info:
        webtoon = self.database.get_webtoon(url)
        if webtoon:
          webtoon.add_current_month_data(webtoon_info.subscribers)
    
    with ThreadPoolExecutor(max_workers=5) as executor:
      list(executor.map(fetch_and_update, urls))
    
    self._save_database()
  
  def get_top_webtoons(self, num_results: int = 15) -> List[Dict[str, any]]:
    """Get top webtoons by subscriber count."""
    top_list = []
    
    for webtoon in self.database.get_all_webtoons().values():
      latest_subscribers = webtoon.get_latest_subscribers()
      if latest_subscribers is not None:
        top_list.append({
          "title": webtoon.title,
          "subscribers": latest_subscribers
        })
    
    # Sort by subscribers (descending) and return top N
    top_list.sort(key=lambda x: x["subscribers"], reverse=True)
    return top_list[:num_results]
  
  def get_all_webtoons_sorted(self) -> List[tuple]:
    """Get all webtoons sorted alphabetically by title."""
    webtoons = self.database.get_all_webtoons()
    return sorted(webtoons.items(), key=lambda item: normalize_title_for_sorting(item[1].title))
  
  def _save_database(self) -> bool:
    """Save the current database state."""
    return DataManager.save_database(self.database)