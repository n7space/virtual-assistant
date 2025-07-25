from setuptools import setup
from setuptools import find_packages

import vareq

setup(
    name="vareq",
    description="Virtual Assistant, created as a part of \"Model-Based Execution Platform for Space Applications\" project (contract 4000146882/24/NL/KK) financed by the European Space Agency",
    version=vareq.__version__,
    packages=find_packages(),
    author="Michał Kurowski",
    author_email="mkurowski@n7space.com",
    url="https://github.com/n7space/virtualassistant",
    install_requires=[
        "pytest==7.4.2",
        "openpyxl==3.1.5",
        "python-docx==1.1.2",
        "requests==2.32.4",
        "langchain==0.3.24",
        "langchain-core==0.3.56",
        "langchain-ollama==0.3.2",
        "pdfplumber==0.11.6",
        "chromadb==1.0.7",
        "mako==1.3.10",
        "flask==3.1.1"
        ],
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python",
        "License :: ESA-PL Permissive v2.3",
        "Operating System :: Linux"
    ],
    entry_points={
        'console_scripts': [
            'vareq = vareq.vareq:main'
        ]
    }
)