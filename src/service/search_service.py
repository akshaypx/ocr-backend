import json
import requests

def search_product(name:str):

    url = "http://13.235.83.90:8000/searchocr"

    payload = json.dumps({
    "query": name,
    "language": "en"
    })
    headers = {
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return response.json()
