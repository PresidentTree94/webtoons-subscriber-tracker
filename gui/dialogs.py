"""Dialog windows for the Webtoon Subscriber Tracker GUI."""

import customtkinter as ctk
from typing import List, Dict

class TopWebtoonsDialog:
    """Dialog to display top webtoons in a table format."""
    
    def __init__(self, parent, webtoons_data: List[Dict[str, any]]):
      """Initialize the top webtoons dialog."""
      self.dialog = ctk.CTkToplevel(parent)
      self.dialog.title("Top 15 Webtoons")
      self.dialog.geometry("500x400")
      self.dialog.grab_set()  # Make dialog modal
      
      self._create_table(webtoons_data)
      self._create_close_button()
    
    def _create_table(self, webtoons_data: List[Dict[str, any]]) -> None:
      """Create the table showing webtoons data."""
      table_frame = ctk.CTkFrame(self.dialog)
      table_frame.pack(padx=10, pady=10, fill="both", expand=True)
      table_frame.grid_columnconfigure(0, weight=1)
      table_frame.grid_columnconfigure(1, weight=3)
      table_frame.grid_columnconfigure(2, weight=1)
      
      # Headers
      headers = ["Rank", "Title", "Subscribers"]
      for i, text in enumerate(headers):
        ctk.CTkLabel(table_frame, text=text, font=("Arial", 14, "bold")).grid(row=0, column=i, padx=5, pady=5, sticky="ew")
      
      # Data rows
      for i, item in enumerate(webtoons_data[:15], start=1):
        # Rank
        ctk.CTkLabel(table_frame, text=f"{i}").grid(row=i, column=0, padx=5, pady=2, sticky="ew")
        
        # Title
        ctk.CTkLabel(table_frame, text=item["title"], wraplength=300).grid(row=i, column=1, padx=5, pady=2, sticky="ew")
        
        # Subscribers
        ctk.CTkLabel(table_frame, text=f"{item['subscribers']:,}").grid(row=i, column=2, padx=5, pady=2, sticky="ew")
    
    def _create_close_button(self) -> None:
      """Create the close button."""
      close_button = ctk.CTkButton(self.dialog, text="Close", command=self.dialog.destroy)
      close_button.pack(pady=(0, 10))
    
    def show(self) -> None:
      """Show the dialog (blocks until closed)."""
      self.dialog.wait_window()

def show_top_webtoons(parent, webtoons_data: List[Dict[str, any]]) -> None:
  """Convenience function to show the top webtoons dialog."""
  dialog = TopWebtoonsDialog(parent, webtoons_data)
  dialog.show()