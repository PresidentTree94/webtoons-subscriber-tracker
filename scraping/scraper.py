"""Web scraping functionality for webtoon data."""

import requests
from bs4 import BeautifulSoup
import tkinter.messagebox as tkmb
from typing import Optional
from storage.models import WebtoonInfo

class WebtoonScraper:
  """Handles web scraping of webtoon information."""
  
  def __init__(self):
    self.session = requests.Session()
    self.session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    })
  
  def scrape_webtoon_info(self, url: str) -> Optional[WebtoonInfo]:
    """Scrape webtoon information from a URL."""
    if not url:
      return None
        
    try:
      response = self.session.get(url)
      response.raise_for_status()
      
      soup = BeautifulSoup(response.text, "html.parser")
      
      # Extract title
      title_element = soup.select_one("h1") or soup.select_one("h3.subj")
      if not title_element:
        tkmb.showerror("Error", "Could not find webtoon title.")
        return None
      
      title = title_element.get_text(separator=" ", strip=True)
      
      # Extract subscriber count
      subscribers_element = soup.find(class_="ico_subscribe")
      if not subscribers_element:
        tkmb.showerror("Error", "Could not find subscriber information.")
        return None
      
      subscribers_text = subscribers_element.find_next_sibling().text.strip()
      subscribers = self._parse_subscriber_count(subscribers_text)
      
      if subscribers is None:
        tkmb.showerror("Error", "Could not parse subscriber count.")
        return None
      
      return WebtoonInfo(title=title, subscribers=subscribers, url=url)
        
    except requests.RequestException as e:
      tkmb.showerror("Error", f"Failed to fetch data: {str(e)}")
      return None
    except Exception as e:
      tkmb.showerror("Error", f"Unexpected error: {str(e)}")
      return None
  
  def _parse_subscriber_count(self, subscribers_text: str) -> Optional[int]:
    """Parse subscriber count from text like '1.2M' or '15,234'."""
    try:
      if "M" in subscribers_text:
        # Convert millions (e.g., "1.2M" -> 1200000)
        number_part = subscribers_text.replace("M", "").strip()
        return int(round(float(number_part) * 1000000))
      else:
        # Regular number with commas (e.g., "15,234" -> 15234)
        return int(subscribers_text.replace(",", ""))
    except (ValueError, AttributeError):
      return None