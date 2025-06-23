import argparse
import sys
from typing import List
import pdfplumber
import re


def is_ecss_reference(text: str) -> bool:
    pattern = r"(\d+\s+)?ECSS-E-ST-\d+-\d+[A-Za-z]?\s+\d+\s+[A-Za-z]+\s+\d+"
    return bool(re.match(pattern, text))


def begins_with_chapter_number(line: str) -> bool:
    if bool(re.match(r"^\d+\.\d+\s", line)):
        return True
    if bool(re.match(r"^\d+\.\d+\.\d+\s", line)):
        return True
    return False


def is_paragraph_delimiter(previous: List[str], line: str) -> bool:
    return (
        # Previous is not empty, does not stop with a dot, but this starts with an upper case letter
        (len(line) > 0 and line[0].isupper() and previous and previous[-1][-1] != ".")
        or
        # Line contains only a number (a page number...)
        line.strip().isdigit()
        or
        # Line begins with chapter number
        begins_with_chapter_number(line)
        or
        # Line begins with a letter followed by a dot and space (e.g. "A. " - list item)
        (len(line) >= 3 and line[0].isalpha() and line[1:3] == ". ")
        or
        # Line begins with a number followed by a dot and space (e.g., "12. " - list item)
        bool(re.match(r"^\d+\.\s", line))
        or
        # Line begins with list item symbol
        line.startswith("• ")
        or
        # Line starts with NOTE
        line.startswith("NOTE ")
    )


def append_group(lines: List[str], group: List[str]):
    text = " ".join(group)
    # Remove bad symbols
    text = text.replace("‐", "-")
    # Prepend chapters with a newline
    if begins_with_chapter_number(text):
        text = f"\n{text}"
    # Ignore page numbers
    if text.isdigit():
        return
    # Ignore ECSS headers and footers
    if is_ecss_reference(text):
        return
    lines.append(text)


def group_lines(lines: List[str]) -> List[str]:
    result = []
    current_group = []

    for line in lines:
        if is_paragraph_delimiter(current_group, line):
            if current_group:
                append_group(result, current_group)
                current_group = []
            current_group.append(line.strip())
        else:
            current_group.append(line.strip())
    if current_group:
        append_group(result, current_group)

    return result


def extract_all_text_from_pdf(
    pdf_path: str, start_page: int, end_page: int
) -> List[str]:
    all_lines = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            count = 0
            for page in pdf.pages:
                count = count + 1
                if count < start_page:
                    continue
                if count > end_page:
                    break
                text = page.extract_text()
                if text:
                    lines = text.split("\n")
                    all_lines.extend([line.strip() for line in lines if line.strip()])
        return all_lines
    except Exception as e:
        print(f"Error extracting text from PDF {pdf_path}: {e}")
        return []


def write_text_to_file(file_path: str, text: str) -> None:
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text)
    except Exception as e:
        print(f"Error writing to file {file_path}: {e}")


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Extract data from the input ECSS PDF file to the output text file."
    )
    parser.add_argument(
        "--input", "-i", required=True, help="Path to the input PDF file"
    )
    parser.add_argument(
        "--output", "-o", required=True, help="Path to the output text file"
    )
    parser.add_argument(
        "--preamble", "-p", required=True, help="Preamble to start the output file with"
    )
    parser.add_argument(
        "--start-page",
        "-s",
        type=int,
        default=1,
        help="Page number to start extraction from (default: 1)",
    )
    parser.add_argument(
        "--end-page",
        "-e",
        type=int,
        default=1,
        help="Page number to end extraction at (default: 1)",
    )
    return parser.parse_args()


def main():
    args = parse_arguments()
    input_path = args.input
    output_path = args.output
    start_page = args.start_page
    end_page = args.end_page
    preamble = args.preamble

    lines = extract_all_text_from_pdf(input_path, start_page, end_page)
    grouped_lines = group_lines(lines)
    extracted_text = " \n".join(grouped_lines)
    if preamble:
        extracted_text = f"{preamble}{extracted_text}"
    write_text_to_file(output_path, extracted_text)

    return 0


if __name__ == "__main__":
    sys.exit(main())
