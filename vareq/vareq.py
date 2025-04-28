from typing import List, Set
import logging
from .vallminterface import Chat
from .vallminterface import Llm


def main():
    """
    The main entry point of Virtual Assistant.
    """
    logging.basicConfig(level=logging.DEBUG)
    # TODO - this is a temporary CLI, used only for testing
    context = ""
    llm = Llm()
    chat = Chat(llm)
    while True:
        query = input()
        if len(query) == 0:
            break
        answer = chat.chat(context, query)
        print(answer)


if __name__ == "__main__":
    main()
