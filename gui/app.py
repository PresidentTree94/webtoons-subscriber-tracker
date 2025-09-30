"""Main GUI application for Webtoon Subscriber Tracker."""

import customtkinter as ctk
import tkinter.messagebox as tkmb
import matplotlib.pyplot as plt
from core.webtoon_manager import WebtoonManager
from core.report_generator import ReportGenerator
from gui.dialogs import show_top_webtoons
from utils.threading_utils import run_in_background

class App(ctk.CTk):
  """Main application window."""
  
  def __init__(self):
    super().__init__()
    
    # Initialize business logic components
    self.webtoon_manager = WebtoonManager()
    self.report_generator = ReportGenerator(self.webtoon_manager)
    
    # Setup GUI
    self._setup_window()
    self._create_layout()
    self._populate_webtoon_list()
  
  def _setup_window(self):
    """Configure the main window."""
    self.title("Webtoon Subscriber Tracker")
    self.geometry("800x405")
    self.grid_columnconfigure(0, weight=1)
    self.grid_columnconfigure(1, weight=2)
  
  def _create_layout(self):
    """Create the main GUI layout."""
    self._create_left_panel()
    self._create_right_panel()
  
  def _create_left_panel(self):
    """Create the left panel with controls."""
    self.left_frame = ctk.CTkFrame(self, fg_color="white")
    self.left_frame.grid(row=0, column=0, sticky="nsew", padx=(20, 10), pady=20)
    self.left_frame.grid_columnconfigure(0, weight=1)
    
    # Title
    ctk.CTkLabel(self.left_frame, text="ACTIONS", font=("Arial", 18, "bold")).grid(row=0, column=0, pady=10)
    
    # URL input
    self.input_entry = ctk.CTkEntry(self.left_frame, placeholder_text="Enter Webtoons URL...")
    self.input_entry.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))
    
    # Action buttons
    self._create_action_buttons()
    
    # Progress bar
    self.progress_bar = ctk.CTkProgressBar(self.left_frame)
    self.progress_bar.grid(row=8, column=0, sticky="ew", padx=20, pady=(10, 20))
    self.progress_bar.set(0)
    self.progress_bar.configure(mode="determinate")
  
  def _create_action_buttons(self):
    """Create the action buttons."""
    buttons_info = [
      ("Add Webtoon", self._on_add_webtoon),
      ("Remove Webtoon", self._on_remove_webtoon),
      ("Update Webtoons", self._on_update_all_webtoons),
      ("Top 15 Webtoons", self._on_show_top_webtoons),
      ("Plot Subscriber Activity", self._on_plot_activity),
      ("Generate Report", self._on_generate_report)
    ]
    
    for i, (text, command) in enumerate(buttons_info, start=2):
      ctk.CTkButton(self.left_frame, text=text, command=command).grid(row=i, column=0, sticky="ew", padx=20, pady=(0, 10))
  
  def _create_right_panel(self):
    """Create the right panel with webtoon list."""
    self.right_frame = ctk.CTkFrame(self, fg_color="white")
    self.right_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 20), pady=20)
    self.right_frame.grid_columnconfigure(0, weight=1)
    self.right_frame.grid_rowconfigure(1, weight=1)
    
    # Title
    ctk.CTkLabel(self.right_frame, text="LIST", font=("Arial", 18, "bold")).grid(row=0, column=0, pady=10)
    
    # Scrollable list
    self.list_frame = ctk.CTkScrollableFrame(self.right_frame)
    self.list_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(10, 20))
    self.list_frame.grid_columnconfigure(0, weight=1)
  
  def _populate_webtoon_list(self):
    """Populate the webtoon list with buttons."""
    # Clear existing widgets
    for widget in self.list_frame.winfo_children():
      widget.destroy()
    
    # Get sorted webtoons and create buttons
    sorted_webtoons = self.webtoon_manager.get_all_webtoons_sorted()
    for i, (url, webtoon_data) in enumerate(sorted_webtoons):
      button = ctk.CTkButton(self.list_frame, text=webtoon_data.title, command=lambda u=url: self._set_input_entry(u))
      button.grid(row=i, column=0, sticky="ew", pady=2)
  
  def _set_input_entry(self, url: str):
    """Set the input entry to the given URL."""
    self.input_entry.delete(0, ctk.END)
    self.input_entry.insert(0, url)
  
  def _set_buttons_state(self, state: str):
    """Enable or disable all action buttons."""
    for widget in self.left_frame.winfo_children():
      if isinstance(widget, ctk.CTkButton):
        widget.configure(state=state)
  
  def _run_background_task_with_progress(self, task_func):
    """Run a background task with progress bar and button state management."""
    def wrapper():
      # Disable buttons and show initial progress
      self.after(0, lambda: self._set_buttons_state("disabled"))
      self.after(0, lambda: self.progress_bar.set(0.3))
      
      # Run the actual task
      success = task_func()
      
      # Show completion progress if successful
      if success:
        self.after(0, lambda: self.progress_bar.set(0.7))
      
      # Reset UI state
      self.after(0, lambda: self.progress_bar.set(1.0))
      self.after(1000, lambda: self.progress_bar.set(0))
      self.after(0, lambda: self._set_buttons_state("normal"))
    
    run_in_background(wrapper)
  
  # Button event handlers
  
  def _on_add_webtoon(self):
    """Handle add webtoon button click."""
    def add_webtoon_task():
      url = self.input_entry.get().strip()
      success = self.webtoon_manager.add_webtoon(url)
      
      if success:
        self.after(0, lambda: self.input_entry.delete(0, ctk.END))
        self.after(0, self._populate_webtoon_list)
      
      return success
    
    self._run_background_task_with_progress(add_webtoon_task)
  
  def _on_remove_webtoon(self):
    """Handle remove webtoon button click."""
    url = self.input_entry.get().strip()
    if self.webtoon_manager.remove_webtoon(url):
      self.input_entry.delete(0, ctk.END)
      self._populate_webtoon_list()
  
  def _on_update_all_webtoons(self):
    """Handle update all webtoons button click."""
    def update_all_task():
      self.webtoon_manager.update_all_webtoons()
      
      # Update UI and show success message
      self.after(0, self._populate_webtoon_list)
      self.after(0, lambda: tkmb.showinfo("Info", "All Webtoons updated."))
      
      return True  # Always consider successful since method handles errors internally
    
    self._run_background_task_with_progress(update_all_task)
  
  def _on_show_top_webtoons(self):
    """Handle show top webtoons button click."""
    top_webtoons = self.webtoon_manager.get_top_webtoons(15)
    show_top_webtoons(self, top_webtoons)
  
  def _on_plot_activity(self):
    """Handle plot activity button click."""
    url = self.input_entry.get().strip()
    webtoon_data = self.webtoon_manager.database.get_webtoon(url)
    
    if webtoon_data and webtoon_data.monthly_data:
      months = sorted(webtoon_data.monthly_data.keys())
      subscribers = [webtoon_data.monthly_data[month] for month in months]
      
      plt.figure(figsize=(10, 6))
      plt.plot(months, subscribers, marker="o", linestyle="-", color="b")
      plt.title(f"Subscriber Activity for {webtoon_data.title}")
      plt.xlabel("Month")
      plt.ylabel("Subscribers")
      plt.grid(True)
      plt.xticks(rotation=45, ha="right")
      plt.tight_layout()
      plt.show()
    else:
      tkmb.showwarning("Warning", "No data available for plotting.")
  
  def _on_generate_report(self):
    """Handle generate report button click."""
    if self.report_generator.save_report():
      tkmb.showinfo("Success", "Report generated successfully!")
    else:
      tkmb.showerror("Error", "Failed to generate report.")