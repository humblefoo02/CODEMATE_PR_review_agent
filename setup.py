#!/usr/bin/env python3
"""
Setup script for PR Review Agent
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="pr-review-agent",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="AI-powered pull request review system",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/pr-review-agent",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.11.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
            "isort>=5.12.0",
            "pre-commit>=3.5.0",
        ],
        "web": [
            "fastapi>=0.104.0",
            "uvicorn[standard]>=0.24.0",
            "jinja2>=3.1.0",
            "python-multipart>=0.0.6",
        ],
        "ai": [
            "openai>=1.0.0",
            "anthropic>=0.7.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "pr-review=main:main",
            "pr-review-cli=demo.cli_demo:main",
            "pr-review-web=demo.web_demo:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yml", "*.yaml", "*.json", "*.html", "*.css", "*.js"],
    },
    keywords="pull-request, code-review, ai, github, gitlab, bitbucket, code-quality, security, linting",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/pr-review-agent/issues",
        "Source": "https://github.com/yourusername/pr-review-agent",
        "Documentation": "https://github.com/yourusername/pr-review-agent/wiki",
    },
)
