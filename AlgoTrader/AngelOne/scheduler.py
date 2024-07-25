import schedule
from AngelOne.db import update_stock_data
import time

# Run the scheduler continuously
def run_continuously(interval=1):
    while(True):
        schedule.run_pending()
        time.sleep(interval)

def schedule_daily_update():
    # Schedule the daily update of stock data
    schedule.every().day.at("03:00").do(update_stock_data)
    run_continuously()
