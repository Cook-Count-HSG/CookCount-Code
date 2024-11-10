import http.client
import requests

# Establish HTTPS connection with Tasty API
conn = http.client.HTTPSConnection("tasty.p.rapidapi.com")

headers = {
    'x-rapidapi-key': "ecc1488b07msh461cab2c4a46cfap1084ecjsn7a46b99f3586",
    'x-rapidapi-host': "tasty.p.rapidapi.com"
}

# Request to fetch recipes
conn.request("GET", "/recipes/list?from=0&size=20&tags=under_30_minutes", headers=headers)

res = conn.getresponse()
data = res.read()

# Display data from the response
print(data.decode("utf-8"))  # Removed max_tokens argument

# Define a function to search API
def searchapi():
    url = "https://tasty.p.rapidapi.com/recipes/list"
    querystring = {"from": "0", "size": "20", "tags": "under_30_minutes"}

    headers = {
        "x-rapidapi-key": "ecc1488b07msh461cab2c4a46cfap1084ecjsn7a46b99f3586",
        "x-rapidapi-host": "tasty.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    
    # Print JSON response from API
    print(response.json())
