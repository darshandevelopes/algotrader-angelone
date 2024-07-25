import time
from myapp.models import Trade
from AngelOne.api import AngelBrokingClient
from logzero import logger
from AngelOne.db import get_stocks

def check_and_execute_trades():
    client = AngelBrokingClient()
    client.authenticate()

    while True:
        time.sleep(0.5) # Respect API rate limit

        # Fetch all trades
        trades = Trade.objects.all()

        # Get all stocks as a dictionary
        stocks = get_stocks_as_dict()

        # Retrieve LTP for all stocks in all trades
        ltp_param = { "NSE": [], "NFO": []}
        for trade in trades:
            try:
                if stocks[trade.stock1]['exch_seg'] == 'NSE':
                    ltp_param['NSE'].append(stocks[trade.stock1]['token'])
                elif stocks[trade.stock1]['exch_seg'] == 'NFO':
                    ltp_param['NFO'].append(stocks[trade.stock1]['token'])
                
                if stocks[trade.stock2]['exch_seg'] == 'NSE':
                    ltp_param['NSE'].append(stocks[trade.stock2]['token'])
                elif stocks[trade.stock2]['exch_seg'] == 'NFO':
                    ltp_param['NFO'].append(stocks[trade.stock2]['token'])
            except:
                logger.error(f"Could not find token for stock {trade.stock1} or {trade.stock2}")

        ltp_data = client.get_ltp(ltp_param)  # {'DRREDDY-EQ': 6820.15, 'SBIN-EQ': 852.0}
        if ltp_data is None:
            time.sleep(1)
            client.authenticate()
            ltp_data = client.get_ltp(ltp_param)
            if ltp_data is None:
                logger.error("Could not fetch LTP even after reauthenticate and retrying.")
                continue
        
        try:
            for trade in trades:
                if trade.status == 'Pending':
                    # Check if the trade should be placed
                    if should_place_trade(trade, ltp_data):
                        # Place the trade
                        try:
                            orderparams = {
                                        "transactiontype":"SELL",
                                        "quantity": trade.quantity,
                                        "tradingsymbol": trade.stock2,
                                        "exchange":stocks[trade.stock2]['exch_seg'],
                                        "symboltoken": stocks[trade.stock2]['token'],
                                        "ordertype":"MARKET",
                                        "producttype":"INTRADAY",
                                        "duration":"DAY",
                                        "variety":"NORMAL",
                                        }
                            order_1 = client.smartApi.placeOrderFullResponse(orderparams)
                            logger.info(f"PlaceOrder : {order_1}")

                            if order_1 is not None and order_1['status']:
                                orderparams = {
                                        "transactiontype":"BUY",
                                        "quantity": trade.quantity,
                                        "tradingsymbol": trade.stock1,
                                        "exchange":stocks[trade.stock1]['exch_seg'],
                                        "symboltoken": stocks[trade.stock1]['token'],
                                        "ordertype":"MARKET",
                                        "producttype":"INTRADAY",
                                        "duration":"DAY",
                                        "variety":"NORMAL",
                                        }
                                order_2 = client.smartApi.placeOrderFullResponse(orderparams)
                                if order_2 is None or not order_2['status']:
                                    logger.error(f"Order placement failed: {order_2}")
                                    cancel_params = {
                                        "variety": "NORMAL",
                                        "orderid": order_1['data']['orderid']
                                    }
                                    client.smartApi.cancelOrder(cancel_params)
                                else:
                                    trade.status = 'Placed'
                                    trade.save()
                                    logger.info(f"Trade {trade.id} placed successfully.")

                        except Exception as e:
                            logger.exception(f"Order placement failed: {e}")
                      
                elif trade.status == 'Placed':
                    # Check if the trade should be exited
                    if should_exit_trade(trade, ltp_data):
                        # Exit the trade
                        try:
                            orderparams = {
                                        "transactiontype":"BUY",
                                        "quantity": trade.quantity,
                                        "tradingsymbol": trade.stock2,
                                        "exchange":stocks[trade.stock2]['exch_seg'],
                                        "symboltoken": stocks[trade.stock2]['token'],
                                        "ordertype":"MARKET",
                                        "producttype":"INTRADAY",
                                        "duration":"DAY",
                                        "variety":"NORMAL",
                                        }
                            order_1 = client.smartApi.placeOrderFullResponse(orderparams)
                            logger.info(f"PlaceOrder : {order_1}")

                            if order_1 is not None and order_1['status']:
                                orderparams = {
                                        "transactiontype":"SELL",
                                        "quantity": trade.quantity,
                                        "tradingsymbol": trade.stock1,
                                        "exchange":stocks[trade.stock1]['exch_seg'],
                                        "symboltoken": stocks[trade.stock1]['token'],
                                        "ordertype":"MARKET",
                                        "producttype":"INTRADAY",
                                        "duration":"DAY",
                                        "variety":"NORMAL",
                                        }
                                order_2 = client.smartApi.placeOrderFullResponse(orderparams)
                                if order_2 is None or not order_2['status']:
                                    logger.error(f"Order placement failed: {order_2}")
                                    cancel_params = {
                                        "variety": "NORMAL",
                                        "orderid": order_1['data']['orderid']
                                    }
                                    client.smartApi.cancelOrder(cancel_params)
                                else:
                                    trade.status = 'Exited'
                                    trade.save()
                                    logger.info(f"Trade {trade.id} exited successfully")

                        except Exception as e:
                            logger.exception(f"Order placement failed: {e}")


                        
        except Exception as e:
            logger.error(f"Error processing trade {trade.id}: {e}")

        # Wait before the next round of checks
        time.sleep(60)  # Adjust the interval as needed

def should_place_trade(trade:Trade, ltp_data):
    stock1_ltp = ltp_data[trade.stock1]
    stock2_ltp = ltp_data[trade.stock2]
    entry_condition = (
        trade.entry_diff == 'points' and stock2_ltp - stock1_ltp >= trade.entry or
        trade.entry_diff == 'percentage' and (stock2_ltp - stock1_ltp ) / stock1_ltp * 100 >= trade.entry
    )
    if stock2_ltp > stock1_ltp and entry_condition:
        return True
    return False

def should_exit_trade(trade:Trade, ltp_data):
    stock1_ltp = ltp_data[trade.stock1]
    stock2_ltp = ltp_data[trade.stock2]
    exit_condition = (
        trade.exit_diff == 'points' and abs(stock2_ltp - stock1_ltp) >= trade.exit or
        trade.exit_diff == 'percentage' and abs(stock2_ltp - stock1_ltp ) / stock1_ltp * 100 >= trade.exit
    )
    stoploss_condition = (
        trade.stop_loss_diff == 'points' and abs(stock2_ltp - stock1_ltp) >= trade.stop_loss or
        trade.stop_loss_diff == 'percentage' and abs(stock2_ltp - stock1_ltp ) / stock1_ltp * 100 >= trade.stop_loss
    )
    if exit_condition or stoploss_condition:
        return True
    return False

def get_stocks_as_dict()->dict:
    tuples_list = get_stocks()
    # Initialize an empty dictionary to store the result
    result = {}

    # Iterate over each tuple in the list
    for item in tuples_list:
        # Unpack each tuple into variables
        symbol, token, lotsize, instrumenttype, exch_seg, strike = item
        
        # Populate the dictionary with symbol as the key
        # and a dictionary of other values as the value
        result[symbol] = {
            'token': token,
            'lotsize': lotsize,
            'instrumenttype': instrumenttype,
            'exch_seg': exch_seg,
            'strike': strike
        }
    
    return result