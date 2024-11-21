# tasty_api.py

import requests  # <-- Make sure this is imported in tasty_api.py

def searchapi(food):
    url = "https://tasty.p.rapidapi.com/recipes/list"
    querystring = {"from": "0", "size": "20", "tags": "under_30_minutes", "q": food}

    headers = {
        "x-rapidapi-key": "ecc1488b07msh461cab2c4a46cfap1084ecjsn7a46b99f3586",
        "x-rapidapi-host": "tasty.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    data = response.json()

    return data.get("results", [])