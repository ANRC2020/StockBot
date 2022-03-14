from td.client import TDClient
from config import CONSUMER_KEY, REDIRECT_URI, JSON_PATH
from my_account import TD_ACCOUNT
import pprint
import pandas as pd

# Create a new session, credentials path is required.

TDSession = TDClient(client_id=CONSUMER_KEY, redirect_uri=REDIRECT_URI, credentials_path=JSON_PATH)

# Login to the session
TDSession.login()

msft_quotes = TDSession.get_quotes(instruments=['MSFT'])

# Grab real-time quotes for 'AMZN' (Amazon) and 'SQ' (Square)
multiple_quotes = TDSession.get_quotes(instruments=['AMZN','SQ'])
# pprint.pprint(msft_quotes)
pprint.pprint(msft_quotes['MSFT']["askPrice"])