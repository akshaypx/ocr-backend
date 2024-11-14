from fastapi import UploadFile
import boto3

async def handwritten_ocr_data_process(uploaded_file: UploadFile):
    
    print("handwritten_ocr_data_process() invoked")
    
    # Read file in bytes
    file_bytes = uploaded_file.file.read()
    
    # Initialize Textract client
    textract = boto3.client('textract')
    response = textract.detect_document_text(Document={'Bytes': file_bytes})
    print("//------------------------//")
    
    print(response,"//")
    # Extract words with their confidence scores
    words_with_confidence = []
    
    # Iterate over the blocks in the response
    for block in response.get('Blocks', []):
        if block['BlockType'] == 'WORD':
            word = block['Text']
            confidence = block['Confidence']
            # Append word and confidence score as a formatted string
            words_with_confidence.append(f"{word} {confidence:.2f}")
    
    # Join words and confidence scores into a single string with spaces
    result_string = ' '.join(words_with_confidence)
    
    return result_string

