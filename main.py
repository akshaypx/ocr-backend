import os
from typing import List
import uuid
from pathlib import Path
import mimetypes
from datetime import datetime
import hashlib
import asyncio  # Import asyncio for the delay

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# from practice.handwritten_service import read_file
# from practice.qdrant_service import search_products
from src.service.pdf_reader_service import extract_text_from_pdf
from src.service.anthropic_service import get_anthropic_result, get_anthropic_result_handwritten
from src.service.ocr_service import get_ocr_result
from src.service.handwritten_textract import handwritten_ocr_data_process
from src.service.search_service import search_product

app = FastAPI()

# Directory to save uploaded files
UPLOAD_DIRECTORY = "uploads"

# Creating dir if it doesn't exist
Path(UPLOAD_DIRECTORY).mkdir(parents=True, exist_ok=True)

# Cache to store results
cache = {}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def is_image(filename: str) -> bool:
    return any(filename.endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff'])

def is_pdf(filename: str) -> bool:
    return filename.endswith('.pdf')

def generate_file_hash(file_content: bytes) -> str:
    """Generate a hash for the file content to use as a cache key."""
    return hashlib.md5(file_content).hexdigest()

@app.get("/test")
async def test():
    return JSONResponse(content={"hello": "world"})

class Item(BaseModel):
    name: str
    quantity: str

class Payload(BaseModel):
    products: List[Item]

@app.post("/search")
async def search_ocr(data: Payload):
    
    products_with_details = []
    
    for item in data.products:
        data = search_product(name=item.name)
        
        if not data:
            raise HTTPException(status_code=404, detail=f"No data found for product : {item.name}")
        
        search_details = data["detail"]
        new_data_list = []
        for entry in search_details:
            new_data = {
                "product_name": entry["_source"]["Name"]["en"],
                "product_code": entry["_source"]["Code"],
                "score": entry["_score"],
                "price": next((price["value"] for price in entry["_source"]["Price"] if price["currency"] == "US Dollar"), None),
                "description":entry["_source"]["Description"]["en"],
                "summary":entry["_source"]["Summary"]["en"],
                "image_link":entry["_source"]["Image"],
            }
            new_data_list.append(new_data)
        
        product_details = {
            "name": item.name,
            "quantity": item.quantity,
            "search_results": new_data_list
        }
        
        products_with_details.append(product_details)
    
    return JSONResponse(content={'products':products_with_details})
            

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No File provided")
    
    try:
        file_content = await file.read()
        file_hash = generate_file_hash(file_content)
        
        # Check if the file's result is already cached
        if file_hash in cache:
            print("Returning cached result")
            await asyncio.sleep(5)  # Add a 2-second delay before returning the cached response
            return JSONResponse(content={"result": cache[file_hash]})
        
        # If not cached, proceed with saving and processing the file
        file_path = os.path.join(UPLOAD_DIRECTORY, f"{uuid.uuid4()}_{file.filename}")
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        result = ""
        
        # Check file type and call the corresponding function
        if is_image(file.filename):
            start_time = datetime.now()
            result = get_ocr_result(file_path)
            print("OCR results fetched")
            end_time = datetime.now()
            print('Duration: {}'.format(end_time - start_time))
            
            start_time = datetime.now()
            anthropic_result = get_anthropic_result(data=result)
            print("Anthropic results fetched")
            end_time = datetime.now()
            print('Duration: {}'.format(end_time - start_time))
            
        elif is_pdf(file.filename):
            result = extract_text_from_pdf(file_path)
            anthropic_result = get_anthropic_result(data=result)
        else:
            os.remove(file_path)
            raise HTTPException(status_code=400, detail="Unsupported file type. Only images and PDFs are supported.")
        
        # Store the result in the cache
        cache[file_hash] = anthropic_result
        
        os.remove(file_path)
        
        return JSONResponse(content={"result": anthropic_result})
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

# from google.auth.transport.requests import Request
# from google.oauth2.service_account import Credentials
# from fastapi.middleware.cors import CORSMiddleware
# service_account_file = "C://Users//akshaysrivastava//Downloads//pdftocsv//googlFile//service_keys_buretail.json"
# scopes = ['https://www.googleapis.com/auth/cloud-platform']
# credentials = Credentials.from_service_account_file(service_account_file, scopes=scopes)
# @app.get("/api/get-access-token")
# async def get_access_token():
#     try:
#         credentials.refresh(Request())
#         return {"access_token": credentials.token}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/send-ocr-image")
# async def send_ocr_test(uploaded_file: UploadFile):
#     print("API /send-ocr-file")
#     print('inside send_ocr_test')
#     result_text = await read_file(uploaded_file)
#     return result_text

@app.post("/handwritten-ocr-data")
async def send_handwritten_ocr_data(uploaded_file: UploadFile):
    print("API //handwritten-ocr-data invoked")
    result=await handwritten_ocr_data_process(uploaded_file)
    print("result from textract received",result)
    anthropic_result = get_anthropic_result_handwritten(data=result)
    return anthropic_result