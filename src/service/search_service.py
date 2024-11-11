import json
import requests

def search_product(name:str):

    url = "http://127.0.0.1:8001/searchProduct"

    payload = json.dumps({
    "query": name,
    "language": "en"
    })
    headers = {
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return response.json()
