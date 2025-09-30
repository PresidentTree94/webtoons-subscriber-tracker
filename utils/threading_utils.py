"""Simple threading utilities for GUI operations."""

import threading

def run_in_background(function):
  """Run a function in a background thread."""
  thread = threading.Thread(target=function, daemon=True)
  thread.start()
  return thread