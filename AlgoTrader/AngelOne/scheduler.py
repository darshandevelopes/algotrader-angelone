import schedule
from AngelOne.db import update_stock_data
import time
from AngelOne.db import init_db

# Run the scheduler continuously
def run_continuously(interval=1):
    while(True):
        schedule.run_pending()
        time.sleep(interval)

def schedule_daily_update():
    # Initial wait to let Django apps load before starting the thread
    time.sleep(10)

    # Initialize the database if not already done
    init_db()
    
    # Schedule the daily update of stock data
    schedule.every().day.at("03:00").do(update_stock_data)
    run_continuously()
