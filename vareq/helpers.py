from typing import List
import numpy
import re

from vareq.vaqueries import BatchResponseElement


def cosine_similarity(embedding_1: List[float], embedding_2: List[float]):
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
    pattern = re.compile(r"<think>.*?</think>", re.IGNORECASE | re.DOTALL)
    return pattern.sub("", text).strip()


def extract_number(text: str) -> float:
    if text is None:
        return 0.0
    match = re.search(r"[-+]?\d*\.\d+|[-+]?\d+", text)
    if match:
        return float(match.group())
    return 0.0


def extract_unique_detections(
    response: List[BatchResponseElement],
) -> List[BatchResponseElement]:
    unique_pairs = {}
    result = []

    for element in response:
        for applied_requirement in element.applied_requirements:
            if element.message:
                pair = (element.requirement, applied_requirement)
                reversed_pair = (applied_requirement, element.requirement)

                if pair not in unique_pairs:
                    # The same pair will not be generated again,
                    # However, we want to prevent the reversed duplicate
                    unique_pairs[reversed_pair] = True
                    result.append(element)

    return result
