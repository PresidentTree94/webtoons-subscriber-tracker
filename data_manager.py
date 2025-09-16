import os
import requests
from bs4 import BeautifulSoup
import json
import tkinter.messagebox as tkmb

DATA_FOLDER = "./data"
DATA_FILE = "data.json"
DATA_PATH = os.path.join(DATA_FOLDER, DATA_FILE)

def load_data():
  try:
    with open(DATA_PATH, "r") as f:
      return json.load(f)
  except FileNotFoundError:
    return {}
  except json.decoder.JSONDecodeError:
    tkmb.showerror("Error", "Data file is corrupted. Edit the file or delete it.")

def save_data(data):
  os.makedirs(DATA_FOLDER, exist_ok=True)
  with open(DATA_PATH, "w") as f:
    json.dump(data, f, indent=2)

def get_webtoon_info(url):
  if url:
    try:
      headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
      }
      response = requests.get(url, headers=headers)
      response.raise_for_status()
      soup = BeautifulSoup(response.text, "html.parser")
      title_element = soup.select_one("h1")
      if title_element is None:
        title_element = soup.select_one("h3.subj")
      subscribers_element = soup.find(class_="ico_subscribe").find_next_sibling()
      if title_element and subscribers_element:
        title = title_element.get_text(separator=" ", strip=True)
        subscribers = int(subscribers_element.text.strip().replace(",", ""))
        return title, subscribers
      else:
        return None, None
    except requests.RequestException:
      tkmb.showerror("Error", "Data not found. Try again.")
      return None, None
  else:
    return None, None