import time
from pytrends.request import TrendReq
from pytrends.exceptions import TooManyRequestsError

# Establish a connection to Google Trends
pytrends = TrendReq(hl='en-US', tz=360)

# Define your keyword list
kw_list = ["python"]

# Build the payload
pytrends.build_payload(kw_list, cat=0, timeframe='today 12-m', geo='', gprop='')

try:
    data = pytrends.interest_over_time()
    print(data)
except TooManyRequestsError:
    print("Rate limit exceeded. Waiting for 30 seconds before retrying...")
    time.sleep(30)
    try:
        data = pytrends.interest_over_time()
        print(data)
    except TooManyRequestsError:
        print("Request failed again. Consider reducing request frequency or using proxies.")
