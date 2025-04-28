from typing import List, Set
import logging
from .vallminterface import Chat
from .vallminterface import Llm


def main():
    """
    The main entry point of Virtual Assistant.
    """
    logging.basicConfig(level=logging.DEBUG)
    template = "### History\n{0}### Context information\n{1}\n### Instruction\n{2}"
    context = ""
    llm = Llm()
    chat = Chat(llm)
    while True:
        query = input()
        if len(query) == 0:
            break
        answer = chat.chat(template, context, query)
        print(answer)


if __name__ == "__main__":
    main()
