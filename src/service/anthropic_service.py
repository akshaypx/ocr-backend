# Use the native inference API to send a text message to Anthropic Claude.
# configure aws before calling this method
import boto3
import json

from botocore.exceptions import ClientError

client = boto3.client("bedrock-runtime", region_name="ap-south-1")


model_id = "anthropic.claude-3-haiku-20240307-v1:0"

# for standard templates only
def get_anthropic_result(data):
    # prompt = """i have a result of ocr from easy ocr and i want you to convert it into the json of following format-
    # {
    # "client_gst": ["", ],
    # "client_name": ["", ],
    # "client_address": ["", ],
    # "client_city": ["", ],
    # "client_postcode": ["", ],
    # "client_contact": ["", ],
    # "products": [
    #     {
    #     "item": ["", ],
    #     "price": ["", ],
    #     "quantity": ["", ],
    #     "total": ["", ]
    #     },]}

    # and here is the result of ocr-
    # """ + data + """

    # The final json will consist of each key containing a list of string value and it's respective confidence score only.
    # Return only the final json and nothing else.
    # """
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
    # prompt = """i have a result of ocr from easy ocr and i want you to convert it into the json of following format-
    # {
    # "client_gst": ["", ],
    # "client_name": ["", ],
    # "client_address": ["", ],
    # "client_city": ["", ],
    # "client_postcode": ["", ],
    # "client_contact": ["", ],
    # "products": [
    #     {
    #     "item": ["", ],
    #     "price": ["", ],
    #     "quantity": ["", ],
    #     "total": ["", ]
    #     },]}

    # and here is the result of ocr-
    # """ + data + """

    # The final json will consist of each key containing a list of string value and it's respective confidence score only.
    # Return only the final json and nothing else.
    # """
    prompt = """i have a result of ocr from easy ocr and i want you to convert it into the json of following format-
    
    [
        {
    Material: string;
    Quantity: string;
    Confidence: string;
            },
        ]
    

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



# # SAMPLE PROMPT