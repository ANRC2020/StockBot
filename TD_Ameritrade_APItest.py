from td.client import TDClient
# Import the client
from td.client import TDClient
from config import CONSUMER_KEY, REDIRECT_URI, JSON_PATH
from my_account import TD_ACCOUNT
import pprint


TDSession = TDClient(client_id=CONSUMER_KEY, redirect_uri=REDIRECT_URI, credentials_path=JSON_PATH)

# Login to the session
TDSession.login()
