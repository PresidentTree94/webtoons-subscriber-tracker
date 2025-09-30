"""Report generation functionality for webtoon data."""

from typing import List
from storage.data_manager import DataManager
from utils.formatters import get_current_date_key

class ReportGenerator:
  """Generates text reports from webtoon data."""
  
  def __init__(self, webtoon_manager):
    """Initialize with a WebtoonManager instance."""
    self.webtoon_manager = webtoon_manager
  
  def _generate_full_report(self) -> str:
    """Generate a comprehensive report with top webtoons and detailed breakdown."""
    report_date = get_current_date_key()
    report_lines = []
    
    # Header
    report_lines.append(f"--- Webtoon Subscriber Report (Generated: {report_date}) ---")
    
    # Top 15 webtoons section
    report_lines.append("")
    report_lines.append("## Top 15 Webtoons by Subscribers")
    report_lines.append("")
    
    top_webtoons = self.webtoon_manager.get_top_webtoons(15)
    for i, webtoon in enumerate(top_webtoons, start=1):
      report_lines.append(f"{i}. {webtoon['title']}: {webtoon['subscribers']:,}")
    
    # Separator
    report_lines.append("")
    report_lines.append("-" * 57)
    
    # Detailed breakdown section
    report_lines.append("")
    report_lines.append("## Detailed Breakdown")
    
    sorted_webtoons = self.webtoon_manager.get_all_webtoons_sorted()
    for url, webtoon_data in sorted_webtoons:
      report_lines.extend(self._generate_webtoon_detail(webtoon_data))
    
    return "\n".join(report_lines)
  
  def _generate_webtoon_detail(self, webtoon_data) -> List[str]:
    """Generate detailed breakdown for a single webtoon."""
    lines = []
    
    # Webtoon title
    lines.append("")
    lines.append(webtoon_data.title)
    
    # Current subscribers
    latest_subscribers = webtoon_data.get_latest_subscribers()
    if latest_subscribers is not None:
      lines.append(f"  - Current Subscribers: {latest_subscribers:,}")
    
    # Monthly data breakdown
    if webtoon_data.monthly_data:
      lines.append("  - Monthly Data:")
      sorted_months = sorted(webtoon_data.monthly_data.keys())
      previous_subscribers = None
        
      for month in sorted_months:
        current_subscribers = webtoon_data.monthly_data[month]
        change_text = ""
        
        if previous_subscribers is not None:
          change = current_subscribers - previous_subscribers
          if change > 0:
            change_text = f" (+{change:,})"
          elif change < 0:
            change_text = f" ({change:,})"
          else:
            change_text = " (No change)"
        
        lines.append(f"    - {month}: {current_subscribers:,}{change_text}")
        previous_subscribers = current_subscribers
    
    return lines
  
  def save_report(self) -> bool:
    """Generate and save a full report to file."""
    report_content = self._generate_full_report()
    report_date = get_current_date_key()
    filename = f"report-{report_date}.txt"
    
    return DataManager.save_report(report_content, filename)