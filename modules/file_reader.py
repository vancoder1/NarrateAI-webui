import os
import PyPDF2

def read_pdf(path_to_file) -> str:
    if not os.path.isfile(path_to_file):
        raise FileNotFoundError(f"No such file: '{path_to_file}'")
    
    if not path_to_file.lower().endswith('.pdf'):
        raise ValueError(f"Invalid file extension for PDF: '{path_to_file}'")
    
    with open(path_to_file, "rb") as file:
        reader = PyPDF2.PdfFileReader(file)
        content = ""
        for page in range(reader.getNumPages()):
            content += reader.getPage(page).extract_text()
        return content

def read_txt(path_to_file) -> str:
    if not os.path.isfile(path_to_file):
        raise FileNotFoundError(f"No such file: '{path_to_file}'")
    
    if not path_to_file.lower().endswith('.txt'):
        raise ValueError(f"Invalid file extension for TXT: '{path_to_file}'")
    
    with open(path_to_file, "r") as file:
        return file.read()