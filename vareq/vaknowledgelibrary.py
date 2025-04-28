from typing import List, Set, Dict
import logging
import docx
import pathlib

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
        pass

    def read_pdf(self, file_path : str) -> str:
        pass

    def read_document(self, file_path : str) -> str:
        extension = pathlib.Path(file_path).suffix.lower()
        if extension == ".docx":
            return self.read_docx(file_path)
        elif extension == ".pdf":
            return self.read_pdf(file_path)
        else:
            return self.read_txt(file_path)