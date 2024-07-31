from requests import get
import threading
import dotenv
import os

# Construct the absolute path to the .env file
current_dir = os.path.dirname(os.path.abspath(__file__))  
dotenv_path = os.path.join(current_dir, '.env')

CONFIG = dotenv.dotenv_values(dotenv_path=dotenv_path)

def send_alert(message:str)->None:
  url = f"{CONFIG['BOT_URL']}{message}"
  threading.Thread(target=get, args=(url,)).start()
  
  # Send alerts to developer
  url = f"{CONFIG['BOT_URL_DEV']}{message}"
  threading.Thread(target=get, args=(url,)).start()