"""Text formatting utilities."""

from datetime import datetime

def normalize_title_for_sorting(title: str) -> str:
  """Normalize title for consistent sorting. Removes punctuation and converts to lowercase."""
  no_punc = title.translate(str.maketrans("", "", "'\u2019,"))
  return "".join(no_punc.split()).lower()

def get_current_month_key() -> str:
  """Get the current month in YYYY-MM format for data storage."""
  return datetime.now().strftime("%Y-%m")

def get_current_date_key() -> str:
  """Get the current date in YYYY-MM-DD format for reports."""
  return datetime.now().strftime("%Y-%m-%d")