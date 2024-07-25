from SmartApi import SmartConnect
import pyotp
from logzero import logger
import dotenv
import os

# Construct the absolute path to the .env file
current_dir = os.path.dirname(os.path.abspath(__file__))    
dotenv_path = os.path.join(current_dir, '.env')

CONFIG = dotenv.dotenv_values(dotenv_path=dotenv_path)

class AngelBrokingClient:
    def __init__(self):
        self.smartApi = None

    def authenticate(self):
        smartApi = SmartConnect(CONFIG['ANGEL_API_KEY'])
        totp = pyotp.TOTP(CONFIG['TOTP_TOKEN']).now()
        correlation_id = "abcde"
        data = smartApi.generateSession(CONFIG['ANGEL_USERNAME'], CONFIG['ANGEL_PASSWORD'], totp)

        if data['status'] == False:
            logger.error(data)
        else:
            self.smartApi = smartApi

    def get_ltp(self, exchangeTokens) -> dict|None:
        # exchangeTokens={ "NSE": ["3045","881"], "NFO": ["58662"]}
        ltp_dict = {}       
        try:
            response = self.smartApi.getMarketData(mode='LTP', exchangeTokens=exchangeTokens)
            if response['status'] and 'fetched' in response['data']:
                for item in response['data']['fetched']:
                    token = item['tradingSymbol']
                    ltp = item['ltp']
                    ltp_dict[token] = ltp
                return ltp_dict
            else:
                logger.warning(f"Could not fetch LTP {response['message']}")
        except Exception as e:
            logger.error(f"An error occurred while fetching LTP: {e}")    
    
if __name__ == "__main__":
    abc = AngelBrokingClient()
    abc.authenticate()
    data = abc.get_ltp({"NSE": ["3045","881"], "NFO": ["58662"]})
    print(data)
