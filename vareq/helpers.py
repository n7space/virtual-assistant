from typing import List
import numpy
import re

def cosine_similarity(embedding_1 : List[float], embedding_2 : List[float]):
    embedding_1 = numpy.array(embedding_1)
    embedding_2 = numpy.array(embedding_2)
    norm_1 = numpy.linalg.norm(embedding_1)
    norm_2 = numpy.linalg.norm(embedding_2)
    if norm_1 == 0 or norm_2 == 0:
        return 0.0
    return numpy.dot(embedding_1, embedding_2) / (norm_1 * norm_2)

def remove_think_markers(text: str) -> str:
    if text is None:
        return text  
    pattern = re.compile(r'<think>.*?</think>', re.IGNORECASE | re.DOTALL)
    return pattern.sub('', text)

def extract_number(text : str) -> float:
    if text is None:
        return 0.0
    match = re.search(r'[-+]?\d*\.\d+|[-+]?\d+', text)
    if match:
        return float(match.group())
    return 0.0