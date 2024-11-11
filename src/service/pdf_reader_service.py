import pdfplumber

def extract_text_from_pdf(pdf_path):
    try:
        # Open the PDF file using pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            all_text = []
            # Iterate through each page
            for page in pdf.pages:
                # Extract text from the page
                text = page.extract_text()
                if text:
                    all_text.append(text.strip())

            # Join all the text from each page into a single string
            final_text = "\n".join(all_text)
            return final_text
            
    except Exception as e:
        return f"Error processing PDF: {e}"
