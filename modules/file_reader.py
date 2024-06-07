import os
from pdfreader import SimplePDFViewer, PDFDocument, PageDoesNotExist
import modules.logging_config as lf

logger = lf.configure_logger(__name__)

def read_pdf(path_to_file) -> str:
    if not os.path.isfile(path_to_file):
        raise FileNotFoundError(f"No such file: '{path_to_file}'")
    
    if not path_to_file.lower().endswith('.pdf'):
        raise ValueError(f"Invalid file extension for PDF: '{path_to_file}'")
    
    with open(path_to_file, "rb") as file:
        viewer = SimplePDFViewer(file)
        content = ""
        
        while True:
            try:
                viewer.render()
                content += "".join(viewer.canvas.strings)
                viewer.next()
            except PageDoesNotExist:
                break
        
        return content

def read_txt(path_to_file) -> str:
    if not os.path.isfile(path_to_file):
        raise FileNotFoundError(f"No such file: '{path_to_file}'")
    
    if not path_to_file.lower().endswith('.txt'):
        raise ValueError(f"Invalid file extension for TXT: '{path_to_file}'")
    
    with open(path_to_file, "r") as file:
        return file.read()