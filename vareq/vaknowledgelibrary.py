from typing import List, Set, Dict
import logging
import docx
import pathlib
import pdfplumber

class KnowledgeLibrary:

    def __init__(self):
        pass

    def read_docx(self, file_path : str) -> str:
        lines = []
        document = docx.Document(file_path)
        for paragraph in document.paragraphs:
            paragrapth_text = paragraph.text
            lines.append(paragrapth_text)
            logging.debug(f"Retrieved paragraph: {paragrapth_text}")
        return "\n".join(lines)

    def read_txt(self, file_path : str) -> str:
        with open(file_path) as file:
            content = file.read()
            logging.debug(f"Retrieved content: {content}")
            return content 

    def read_pdf(self, file_path : str) -> str:
        lines = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text_simple()
                lines.append(page_text)
                logging.debug(f"Retrieved page: {page_text}")
        return "\n".join(lines)

    def read_document(self, file_path : str) -> str:
        extension = pathlib.Path(file_path).suffix.lower()
        if extension == ".docx":
            return self.read_docx(file_path)
        elif extension == ".pdf":
            return self.read_pdf(file_path)
        else:
            return self.read_txt(file_path)