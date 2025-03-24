from setuptools import setup, find_packages

setup(
    name="article_dryer",
    version="0.1.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "aiohttp",
        "beautifulsoup4",
        "python-dotenv"
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="A Python library for article summarization",
    keywords="article, summarization, nlp",
    python_requires=">=3.7",
)
