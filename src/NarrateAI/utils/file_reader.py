import os
from pdfreader import SimplePDFViewer, PageDoesNotExist
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from loguru import logger

class FileReader:
    def __init__(self):
        self.supported_extensions = {
            '.txt': self._read_txt,
            '.pdf': self._read_pdf,
            '.epub': self._read_epub,
            '.docx': self._read_docx,
            '.html': self._read_html,
            '.htm': self._read_html,
        }
    
    def _read_txt(self, path_to_file: str) -> str:
        logger.debug(f"Reading TXT file: {path_to_file}")
        with open(path_to_file, "r", encoding='utf-8') as file:
            return file.read()

    def _read_pdf(self, path_to_file: str) -> str:
        logger.debug(f"Reading PDF file: {path_to_file}")
        with open(path_to_file, "rb") as file:
            viewer = SimplePDFViewer(file)
            content = ""
            try:
                while True:
                    viewer.render()
                    content += "".join(viewer.canvas.strings)
                    viewer.next()
            except PageDoesNotExist:
                logger.debug("Reached end of PDF document.")
            except Exception as e:
                logger.error(f"Error reading PDF page in '{path_to_file}': {e}", exc_info=True)
            return content

    def _read_epub(self, path_to_file: str) -> str:
        logger.debug(f"Reading EPUB file: {path_to_file}")
        book = epub.read_epub(path_to_file)
        content_parts = []
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                soup = BeautifulSoup(item.get_content(), 'html.parser')
                text = soup.get_text(separator='\n')
                content_parts.append(text)
        return '\n'.join(content_parts)

    def _read_docx(self, path_to_file: str) -> str:
        logger.debug(f"Reading DOCX file: {path_to_file}")
        try:
            from docx import Document  # Requires `pip install python-docx`
            doc = Document(path_to_file)
            full_text_parts = []
            for para in doc.paragraphs:
                full_text_parts.append(para.text)
            return '\n'.join(full_text_parts)
        except ImportError:
            logger.error("The 'python-docx' library is required to read DOCX files. Please install it (e.g., `pip install python-docx`).")
            raise NotImplementedError("DOCX reading requires the 'python-docx' library. Please install it.")
        except Exception as e:
            logger.error(f"Error reading DOCX file '{path_to_file}': {e}", exc_info=True)
            raise ValueError(f"Could not read DOCX file '{path_to_file}'.")

    def _read_html(self, path_to_file: str) -> str:
        logger.debug(f"Reading HTML file: {path_to_file}")
        try:
            with open(path_to_file, "r", encoding='utf-8') as file:
                soup = BeautifulSoup(file, 'html.parser')
                # Attempt to get meaningful text, often from the body
                body = soup.find('body')
                if body:
                    return body.get_text(separator='\n')
                else:
                    # Fallback to all text if body tag is not found
                    return soup.get_text(separator='\n')
        except Exception as e:
            logger.error(f"Error reading HTML file '{path_to_file}': {e}", exc_info=True)
            raise ValueError(f"Could not read HTML file '{path_to_file}'.")

    def read_file(self, path_to_file: str) -> str:
        if not os.path.isfile(path_to_file):
            logger.error(f"File not found: '{path_to_file}'")
            raise FileNotFoundError(f"No such file: '{path_to_file}'")

        file_extension = os.path.splitext(path_to_file)[1].lower()
        logger.info(f"Attempting to read file: '{path_to_file}' with extension '{file_extension}'")

        reader_method = self.supported_extensions.get(file_extension)

        if reader_method:
            try:
                content = reader_method(path_to_file)
                logger.info(f"Successfully read file: '{path_to_file}'")
                return content
            except NotImplementedError as nie:
                logger.error(f"{nie} for file '{path_to_file}'")
                raise nie 
            except Exception as e:
                logger.error(f"Failed to read file '{path_to_file}' with extension '{file_extension}': {e}", exc_info=True)
                raise ValueError(f"Error processing file '{os.path.basename(path_to_file)}': {e}")
        else:
            logger.warning(f"Unsupported file extension: '{file_extension}' for file '{path_to_file}'")
            supported_ext_str = ", ".join(self.supported_extensions.keys())
            raise ValueError(f"Unsupported file extension: '{file_extension}'. Supported extensions are: {supported_ext_str}")
