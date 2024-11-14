# Use the native inference API to send a text message to Anthropic Claude.
# configure aws before calling this method
import boto3
import json

from botocore.exceptions import ClientError

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Retrieve the AWS credentials from environment variables
aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
region_name = os.getenv("AWS_DEFAULT_REGION")

# Create a boto3 client using the environment variables
client = boto3.client(
    "bedrock-runtime", 
    region_name=region_name, 
    aws_access_key_id=aws_access_key_id, 
    aws_secret_access_key=aws_secret_access_key
)


model_id = "anthropic.claude-3-haiku-20240307-v1:0"

# for standard templates only
def get_anthropic_result(data):
    prompt = """i have a result of ocr from easy ocr and i want you to convert it into the json of following format-
    {
    "client_gst": {
    value: "", score: ""},
    "vendor_gst": {
    value: "", score: ""},
    "date": {
    value: "", score: ""},
    "po_number": {
    value: "", score: ""},
    "client_name": {
    value: "", score: ""},
    "client_address": {
    value: "", score: ""},
    "client_city": {
    value: "", score: ""},
    "client_postcode": {
    value: "", score: ""},
    "client_contact": {
    value: "", score: ""},
    "products": [
        {
        "item": {
        value: "", score: ""},
        "price": {
        value: "", score: ""},
        "quantity": {
        value: "", score: ""},
        "total": {
        value: "", score: ""}
        },]}

    and here is the result of ocr-
    """ + data + """

    The final json will consist of each key containing a list of string value and it's respective confidence score only.
    Return only the final json and nothing else.
    """

    # Format the request payload using the model's native structure.
    native_request = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 2000,
        "temperature": 0,
        "messages": [
            {
                "role": "user",
                "content": [{"type": "text", "text": prompt}],
            }
        ],
    }

    # Convert the native request to JSON.
    request = json.dumps(native_request)

    try:
        # Invoke the model with the request.
        response = client.invoke_model(modelId=model_id, body=request)

    except (ClientError, Exception) as e:
        print(f"ERROR: Can't invoke '{model_id}'. Reason: {e}")
        exit(1)

    # Decode the response body.
    model_response = json.loads(response["body"].read())

    # Extract and print the response text.
    response_text = model_response["content"][0]["text"]
    # print(response_text)
    return response_text

# for handwritten slips
def get_anthropic_result_handwritten(data):
    prompt = """I have a result of OCR from AWS Textract and I want you to convert it into a JSON of the following format:
    
    [
        {
            "Material": string,
            "Quantity": string,
            "Confidence": string
        }
    ]
    
    Each key should contain a single string value, and the "Confidence" key should only contain one confidence score (not multiple). Ensure each line has one confidence score associated with its corresponding data.
    
    Here is the result of the OCR:
    """ + data + """
    
    Please return only the final JSON in the specified format, with each data item containing one confidence score per line.
    Give only the JSON, nothing else.
    """

    # Format the request payload using the model's native structure.
    native_request = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 2000,
        "temperature": 0,
        "messages": [
            {
                "role": "user",
                "content": [{"type": "text", "text": prompt}],
            }
        ],
    }

    # Convert the native request to JSON.
    request = json.dumps(native_request)

    try:
        # Invoke the model with the request.
        response = client.invoke_model(modelId=model_id, body=request)

    except (ClientError, Exception) as e:
        print(f"ERROR: Can't invoke '{model_id}'. Reason: {e}")
        exit(1)

    # Decode the response body.
    model_response = json.loads(response["body"].read())

    # Extract and print the response text.
    response_text = model_response["content"][0]["text"]
    # print(response_text)
    return response_text

