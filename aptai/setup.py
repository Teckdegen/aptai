
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="aptai",
    version="1.2.2",
    author="Teck",
    author_email="teckdegen@gmail.com", 
    description="Advanced AI-powered SDK for DeFi & NFT analytics on Aptos",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Teck/aptai",
    project_urls={
        "X": "https://x.com/Teckdegen",
        "Telegram": "https://t.me/Teck_degen",
    },
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
    install_requires=[
        "requests>=2.25.0",
        "groq>=0.4.0",
    ],
)

