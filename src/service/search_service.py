import json
import requests
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

def search_product(name:str):

    url = "http://"+os.getenv("SEARCH_URL")+":8000/searchocr"

    payload = json.dumps({
    "query": name,
    "language": "en"
    })
    headers = {
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return response.json()
