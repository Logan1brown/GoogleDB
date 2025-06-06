"""Setup file for GoogleDB package."""
from setuptools import setup, find_packages

setup(
    name="googledb",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0",
    ],
    python_requires=">=3.9",
)
