from requests import get
import random

#free public apis
def get_random_quote():
    resp = get("https://type.fit/api/quotes")
    data = resp.json()
    quotes_all = len(data)
    random_quote = data[random.randrange(quotes_all)]
    return random_quote
