import os
import customtkinter as ctk
import tkinter.messagebox as tkmb
import threading
import matplotlib.pyplot as plt
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from data_manager import DATA_FOLDER, load_data, save_data, get_webtoon_info

class App(ctk.CTk):
  def __init__(self):
    super().__init__()
    self.title("Webtoon Subscriber Tracker")
    self.geometry("800x405")
    self.grid_columnconfigure(0, weight=1)
    self.grid_columnconfigure(1, weight=2)
    self.webtoon_data = load_data()

    self.left_frame = ctk.CTkFrame(self, fg_color="white")
    self.left_frame.grid(row=0, column=0, sticky="nsew", padx=(20, 10), pady=20)
    self.left_frame.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(self.left_frame, text="ACTIONS", font=("Arial", 18, "bold")).grid(row=0, column=0, pady=10)
    
    self.input_entry = ctk.CTkEntry(self.left_frame, placeholder_text="Enter Webtoons URL...")
    self.input_entry.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))

    buttons_info = [
      ("Add Webtoon", self.add_webtoon_gui),
      ("Remove Webtoon", self.remove_webtoon_gui),
      ("Update Webtoons", self.update_all_webtoons_gui),
      ("Top 15 Webtoons", self.get_top_webtoons_gui),
      ("Plot Subscriber Activity", self.plot_subscriber_activity_gui),
      ("Generate Report", self.generate_report_gui)
    ]

    for i, (text, command) in enumerate(buttons_info, start=2):
      ctk.CTkButton(self.left_frame, text=text, command=command).grid(row=i, column=0, sticky="ew", padx=20, pady=(0, 10))

    self.progress_bar = ctk.CTkProgressBar(self.left_frame)
    self.progress_bar.grid(row=len(buttons_info) + 2, column=0, sticky="ew", padx=20, pady=(10, 20))
    self.progress_bar.set(0)
    self.progress_bar.configure(mode="determinate")

    self.right_frame = ctk.CTkFrame(self, fg_color="white")
    self.right_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 20), pady=20)
    self.right_frame.grid_columnconfigure(0, weight=1)
    self.right_frame.grid_rowconfigure(1, weight=1)

    ctk.CTkLabel(self.right_frame, text="LIST", font=("Arial", 18, "bold")).grid(row=0, column=0, pady=10)

    self.list_frame = ctk.CTkScrollableFrame(self.right_frame)
    self.list_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(10, 20))
    self.list_frame.grid_columnconfigure(0, weight=1)

    self.populate_list()

  def run_in_thread(self, target, *args):
    threading.Thread(target=target, args=args, daemon=True).start()

  def set_buttons_state(self, state):
    for widget in self.left_frame.winfo_children():
      if isinstance(widget, ctk.CTkButton):
        widget.configure(state=state)

  def normalize_sorting(self, title):
    return "".join(title.split()).lower()

  def populate_list(self):
    for widget in self.list_frame.winfo_children():
      widget.destroy()
      
    webtoon_items = sorted(self.webtoon_data.items(), key=lambda item: self.normalize_sorting(item[1]["title"]))
    for i, (url, data) in enumerate(webtoon_items):
      title = data["title"]
      button = ctk.CTkButton(self.list_frame, text=title, command=lambda u=url: self.set_input_entry(u))
      button.grid(row=i, column=0, sticky="ew", pady=2)

  def set_input_entry(self, input):
    self.input_entry.delete(0, ctk.END)
    self.input_entry.insert(0, input)

  def add_webtoon_gui(self):
    self.run_in_thread(self._add_webtoon_thread)

  def _add_webtoon_thread(self):
    self.after(0, lambda: self.set_buttons_state("disabled"))
    self.after(0, lambda: self.progress_bar.set(0.3))
    self.update_idletasks()

    url = self.input_entry.get().strip()
    title, subscribers = get_webtoon_info(url)
    if title and subscribers is not None:
      if url not in self.webtoon_data:
        self.webtoon_data[url] = {"title": title, "data": {}}
      current_month = datetime.now().strftime("%Y-%m")
      self.webtoon_data[url]["data"][current_month] = subscribers
      save_data(self.webtoon_data)

      self.after(0, lambda: self.progress_bar.set(0.7))
      self.after(0, lambda: self.input_entry.delete(0, ctk.END))
      self.after(0, self.populate_list)

    self.after(0, lambda: self.progress_bar.set(1.0))
    self.after(1000, lambda: self.progress_bar.set(0))
    self.after(0, lambda: self.set_buttons_state("normal"))

  def remove_webtoon_gui(self):
    url = self.input_entry.get().strip()
    if url in self.webtoon_data:
      del self.webtoon_data[url]
      save_data(self.webtoon_data)
      self.input_entry.delete(0, ctk.END)
      self.populate_list()

  def update_all_webtoons_gui(self):
    self.run_in_thread(self._update_all_webtoons_thread)

  def _update_all_webtoons_thread(self):
    self.after(0, lambda: self.set_buttons_state("disabled"))
    current_month = datetime.now().strftime("%Y-%m")
    urls = list(self.webtoon_data.keys())
    total = len(urls)

    def fetch_and_update(url):
      title, subscribers = get_webtoon_info(url)
      if title and subscribers is not None:
        self.webtoon_data[url]["data"][current_month] = subscribers
      return url

    with ThreadPoolExecutor(max_workers=5) as executor:
      for i, url in enumerate(executor.map(fetch_and_update, urls), start=1):
        progress = i / total
        self.after(0, lambda p=progress: self.progress_bar.set(p))
        self.update_idletasks()

    save_data(self.webtoon_data)
    self.after(0, self.populate_list)
    self.after(0, lambda: tkmb.showinfo("Info", "All Webtoons updated."))
    self.after(0, lambda: self.progress_bar.set(1.0))
    self.after(1000, lambda: self.progress_bar.set(0))
    self.after(0, lambda: self.set_buttons_state("normal"))

  def get_top_webtoons_list(self, num_results=15):
    top_list = []
    for url, data in self.webtoon_data.items():
      if data["data"]:
        latest_month = sorted(data["data"].keys())[-1]
        latest_subscribers = data["data"][latest_month]
        top_list.append({"title": data["title"], "subscribers": latest_subscribers})
    top_list.sort(key=lambda x: x["subscribers"], reverse=True)
    return top_list[:num_results]

  def get_top_webtoons_gui(self):
    top_list = self.get_top_webtoons_list()

    top_list_window = ctk.CTkToplevel(self)
    top_list_window.title("Top 15 Webtoons")
    top_list_window.geometry("500x400")
    top_list_window.grab_set()

    table_frame = ctk.CTkFrame(top_list_window)
    table_frame.pack(padx=10, pady=10, fill="both", expand=True)
    table_frame.grid_columnconfigure(0, weight=1)
    table_frame.grid_columnconfigure(1, weight=3)
    table_frame.grid_columnconfigure(2, weight=1)

    headers = ["Rank", "Title", "Subscribers"]
    for i, text in enumerate(headers):
      ctk.CTkLabel(table_frame, text=text, font=("Arial", 14, "bold")).grid(row=0, column=i, padx=5, pady=5, sticky="ew")

    for i, item in enumerate(top_list[:15], start=1):
      ctk.CTkLabel(table_frame, text=f"{i}").grid(row=i, column=0, padx=5, pady=2, sticky="ew")
      ctk.CTkLabel(table_frame, text=item["title"], wraplength=300).grid(row=i, column=1, padx=5, pady=2, sticky="ew")
      ctk.CTkLabel(table_frame, text=f"{item["subscribers"]:,}").grid(row=i, column=2, padx=5, pady=2, sticky="ew")

    close_button = ctk.CTkButton(top_list_window, text="Close", command=top_list_window.destroy)
    close_button.pack(pady=(0, 10))

  def plot_subscriber_activity_gui(self):
    url = self.input_entry.get().strip()
    if url in self.webtoon_data:
      data = self.webtoon_data[url]["data"]
      months = sorted(data.keys())
      subscribers = [data[month] for month in months]
      plt.figure(figsize=(10, 6))
      plt.plot(months, subscribers, marker="o", linestyle="-", color="b")
      plt.title(f"Subscriber Activity for {self.webtoon_data[url]["title"]}")
      plt.xlabel("Month")
      plt.ylabel("Subscribers")
      plt.grid(True)
      plt.xticks(rotation=45, ha="right")
      plt.tight_layout()
      plt.show()

  def generate_report_gui(self):
    report_date = datetime.now().strftime("%Y-%m-%d")
    report_name = f"report-{report_date}.txt"
    data_path = os.path.join(DATA_FOLDER, report_name)
    with open(data_path, "w") as f:
      f.write(f"--- Webtoon Subscriber Report (Generated: {report_date}) ---\n")
      
      top_list = self.get_top_webtoons_list()
      f.write("\n## Top 15 Webtoons by Subscribers\n\n")
      for i, item in enumerate(top_list[:15], start=1):
        f.write(f"{i}. {item['title']}: {item['subscribers']:,}\n")

      f.write("\n" + "-"*50 + "\n")

      f.write("\n## Detailed Breakdown\n")
      sorted_webtoons = sorted(self.webtoon_data.items(), key=lambda item: self.normalize_sorting(item[1]["title"]))
      for url, data in sorted_webtoons:
        title = data["title"]
        monthly_data = data["data"]
        f.write(f"\n{title}\n")
        latest_subscribers = monthly_data[sorted(monthly_data.keys())[-1]]
        f.write(f"  - Current Subscribers: {latest_subscribers:,}\n")

        f.write("  - Monthly Data:\n")
        sorted_months = sorted(monthly_data.keys())
        previous_subscribers = None
        for month in sorted_months:
          current_subscribers = monthly_data[month]
          change_text = ""
          if previous_subscribers is not None:
            change = current_subscribers - previous_subscribers
            if change > 0:
              change_text = f" (+{change:,})"
            elif change < 0:
              change_text = f" ({change:,})"
            else:
              change_text = " (No change)"
          f.write(f"    - {month}: {current_subscribers:,}{change_text}\n")
          previous_subscribers = current_subscribers