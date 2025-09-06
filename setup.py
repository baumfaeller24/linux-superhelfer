from setuptools import setup, find_packages

setup(
    name="linux-superhelfer",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0",
        "pydantic==2.5.0",
        "pyyaml==6.0.1",
        "requests==2.31.0",
        "ollama==0.1.7",
        "chromadb==0.4.18",
        "streamlit==1.28.2",
    ],
    python_requires=">=3.10",
)