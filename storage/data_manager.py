"""File I/O operations for webtoon data persistence."""

import os
import json
import tkinter.messagebox as tkmb
from storage.models import WebtoonDatabase

# Constants
DATA_FOLDER = "./data"
DATA_FILE = "data.json"
DATA_PATH = os.path.join(DATA_FOLDER, DATA_FILE)

class DataManager:
  """Handles loading and saving webtoon data to/from JSON files."""
  
  @staticmethod
  def load_database() -> WebtoonDatabase:
    """Load webtoon database from JSON file."""
    try:
      with open(DATA_PATH, "r") as f:
        raw_data = json.load(f)
      
      database = WebtoonDatabase()
      database.load_from_dict(raw_data)
      return database
        
    except FileNotFoundError:
      # File doesn't exist yet - return empty database
      return WebtoonDatabase()
    except json.JSONDecodeError:
      tkmb.showerror("Error", "Data file is corrupted. Edit the file or delete it.")
      return WebtoonDatabase()
    except Exception as e:
      tkmb.showerror("Error", f"Failed to load data: {str(e)}")
      return WebtoonDatabase()
  
  @staticmethod
  def save_database(database: WebtoonDatabase) -> bool:
    """Save webtoon database to JSON file."""
    try:
      # Ensure data folder exists
      os.makedirs(DATA_FOLDER, exist_ok=True)
      
      # Convert database to dictionary and save as JSON
      data = database.to_dict()
      with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=2)
      
      return True
        
    except Exception as e:
      tkmb.showerror("Error", f"Failed to save data: {str(e)}")
      return False
  
  @staticmethod
  def save_report(report_content: str, filename: str) -> bool:
    """Save a text report to the data folder."""
    try:
      # Ensure data folder exists
      os.makedirs(DATA_FOLDER, exist_ok=True)
      
      report_path = os.path.join(DATA_FOLDER, filename)
      with open(report_path, "w") as f:
        f.write(report_content)
      
      return True
        
    except Exception as e:
      tkmb.showerror("Error", f"Failed to save report: {str(e)}")
      return False