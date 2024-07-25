# myapp/logging_setup.py
import os
import time
import logzero
import logging

def setup_logging():
    # Create a log folder based on the current date
    log_folder = time.strftime("%Y-%m-%d", time.localtime())
    log_folder_path = os.path.join("logs", log_folder)  # Construct the full path to the log folder
    os.makedirs(log_folder_path, exist_ok=True)  # Create the log folder if it doesn't exist
    log_path = os.path.join(log_folder_path, "app.log")  # Construct the full path to the log file

    # Configure logzero to output logs to a date-wise log file
    logzero.logfile(log_path, loglevel=logging.INFO)
