from io import BytesIO
# import io
import os
from typing import List
import uuid
from pathlib import Path
import mimetypes
from datetime import datetime
import hashlib
import asyncio  # Import asyncio for the delay
import base64

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import pdfplumber
from pydantic import BaseModel
# from src.service.pdf_reader_service import extract_text_from_pdf
from src.service.anthropic_service import get_anthropic_result, get_anthropic_result_handwritten
# from src.service.ocr_service import get_ocr_result
from src.service.handwritten_textract import handwritten_ocr_data_process
from src.service.search_service import search_product
# from src.utils.detect_file_type import detect_file_type
# from src.utils.pdf_to_image import convert_pdf_to_image


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
    cache_key = str(data)
   
    # Check if result is already in the cache
    if cache_key in cache:
        await asyncio.sleep(3)
        return JSONResponse(content={'products': cache[cache_key]})
    
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
    
    cache[cache_key] = products_with_details
    return JSONResponse(content={'products':products_with_details})     

# @app.post("/upload")
# async def upload_file(file: UploadFile = File(...)):
#     if not file.filename:
#         raise HTTPException(status_code=400, detail="No File provided")
    
#     try:
#         file_content = await file.read()
#         file_hash = generate_file_hash(file_content)
        
#         # Check if the file's result is already cached
#         if file_hash in cache:
#             print("Returning cached result")
#             await asyncio.sleep(5)  # Add a 2-second delay before returning the cached response
#             return JSONResponse(content={"result": cache[file_hash]})
        
#         # If not cached, proceed with saving and processing the file
#         file_path = os.path.join(UPLOAD_DIRECTORY, f"{uuid.uuid4()}_{file.filename}")
#         with open(file_path, "wb") as f:
#             f.write(file_content)
        
#         result = ""
        
#         # Check file type and call the corresponding function
#         if is_image(file.filename):
#             start_time = datetime.now()
#             result = get_ocr_result(file_path)
#             print("OCR results fetched")
#             end_time = datetime.now()
#             print('Duration: {}'.format(end_time - start_time))
            
#             start_time = datetime.now()
#             anthropic_result = get_anthropic_result(data=result)
#             print("Anthropic results fetched")
#             end_time = datetime.now()
#             print('Duration: {}'.format(end_time - start_time))
            
#         elif is_pdf(file.filename):
#             result = extract_text_from_pdf(file_path)
#             anthropic_result = get_anthropic_result(data=result)
#         else:
#             os.remove(file_path)
#             raise HTTPException(status_code=400, detail="Unsupported file type. Only images and PDFs are supported.")
        
#         # Store the result in the cache
#         cache[file_hash] = anthropic_result
        
#         os.remove(file_path)
        
#         return JSONResponse(content={"result": anthropic_result})
    
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

    
def convert_pdf_to_image2(file_path: str) -> bytes:
    try:
        # Open the PDF using pdfplumber
        with pdfplumber.open(file_path) as pdf:
            if len(pdf.pages) == 0:
                raise ValueError("The uploaded PDF is empty.")
            
            # Get the first page
            first_page = pdf.pages[0]
            
            # Convert the first page to an image
            pil_image = first_page.to_image()

            # Save the image to a BytesIO object in PNG format
            image_bytes = BytesIO()
            pil_image.save(image_bytes, format="PNG")
            image_bytes.seek(0)  # Move the pointer to the start of the BytesIO object
            return image_bytes.getvalue()  # Return the image as bytes

    except Exception as e:
        raise ValueError(f"Error processing PDF: {e}")

def encode_bytesio_to_base64(image_bytesio: BytesIO) -> str:
    # Read the raw bytes from the BytesIO object
    image_bytes = image_bytesio.read()

    # Base64 encode the bytes
    base64_encoded = base64.b64encode(image_bytes).decode('utf-8')  # Convert to string

    return base64_encoded

@app.post("/ocr")
async def send_standard_ocr_data(file: UploadFile = File(...)):
    file_content = await file.read()
    file_path = os.path.join(UPLOAD_DIRECTORY, f"{uuid.uuid4()}_{file.filename}")

    # Save the file locally (if needed)
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    result_from_textract = ""
    
    # Check file type and process accordingly
    if is_image(file.filename):
        # Directly send the image bytes to OCR processing
        result_from_textract = await handwritten_ocr_data_process(file_content)
    
    elif is_pdf(file.filename):
        # Convert PDF to image bytes
        new_file_content = convert_pdf_to_image2(file_path)
        result_from_textract = await handwritten_ocr_data_process(new_file_content)
    
    print(">> Result from Textract received ->>", result_from_textract)
    
    # Assume `get_anthropic_result_handwritten` processes the OCR result
    final_result = get_anthropic_result_handwritten(result_from_textract)
    print(">> Result from Anthropic received ->>", final_result)
    
    return final_result
    

# @app.post("/handwritten-ocr-data")
# async def send_handwritten_ocr_data(uploaded_file: UploadFile):
#     print("API //handwritten-ocr-data invoked")
#     result=await handwritten_ocr_data_process(uploaded_file)
#     print("result from textract received",result)
#     anthropic_result = get_anthropic_result_handwritten(data=result)
#     return anthropic_result




