import easyocr as ez
reader = ez.Reader(['en'])

def get_ocr_result(img_path):
    # result = reader.readtext('C://Users//akshaysrivastava//Downloads//pdftocsv//poc//image.jpg')
    result = reader.readtext(img_path)
    
    # same line concatenated string
    es = ''.join(f'[[{item[1]}, {item[2]}]]' for item in result)

    return es
