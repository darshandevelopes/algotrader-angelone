import sqlite3
import requests
from threading import Lock
from logzero import logger
import os

db_lock = Lock()

# Construct the absolute path to the database
current_dir = os.path.dirname(os.path.abspath(__file__))    
db_path = os.path.join(current_dir, 'stocks.db')

def init_db():
    with db_lock:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stocks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token TEXT NOT NULL,
                symbol TEXT NOT NULL,
                name TEXT NOT NULL,
                expiry TEXT,
                strike REAL,
                lotsize INTEGER,
                instrumenttype TEXT,
                exch_seg TEXT NOT NULL,
                tick_size REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

        # Check if the stocks table is empty
        cursor.execute("SELECT COUNT(*) FROM stocks")
        result = cursor.fetchone()
        conn.close()

    if result[0] == 0: #"Database is empty.
        # Perform initial data insertion
        update_stock_data()

def update_stock_data():
    try:
        url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
        response = requests.get(url, timeout=120)
        response.raise_for_status()  # Raise an error for bad status codes

        data = response.json()

        with db_lock:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Delete all existing rows from the table
            cursor.execute("DELETE FROM stocks")

            # Filter and insert data
            for entry in data:
                if entry['exch_seg'] in ['NSE', 'NFO']:
                    cursor.execute('''
                        INSERT INTO stocks (token, symbol, name, expiry, strike, lotsize, instrumenttype, exch_seg, tick_size)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        entry['token'],
                        entry['symbol'],
                        entry['name'],
                        entry.get('expiry', ''),
                        float(entry.get('strike', -1)),
                        int(entry.get('lotsize', 1)),
                        entry.get('instrumenttype', ''),
                        entry['exch_seg'],
                        float(entry.get('tick_size', 1))
                    ))
            
            conn.commit()
            conn.close()
            logger.info("Database updated with new stock data.")

    except requests.exceptions.Timeout:
        logger.error("The request timed out when downloading the stocks data.")
    except:
        logger.exception(f"An exception ocurred")

def get_stocks():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''SELECT symbol, token, lotsize, instrumenttype, exch_seg, strike FROM stocks 
                   where symbol like "%FUT"
                   or symbol like "%-EQ"
                   and exch_seg = "NSE" or exch_seg = "NFO"
                   and strike = -1;
                   ''')
    trades = cursor.fetchall()
    conn.close()
    # [('SPAL-EQ', '18252', 1, '', 'NSE', -1.0), ('SPCENET-EQ', '19372', 1, '', 'NSE', -1.0)]
    return trades

if __name__ == '__main__':
    # init_db()
    # update_stock_data()
    print(get_stocks())
