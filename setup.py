"""
Setup script for FaceAuth - Local Face Authentication System
"""

from setuptools import setup, find_packages
import os

# Read README file
def read_readme():
    try:
        with open('README.md', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "FaceAuth - Local Face Authentication System"

# Read requirements
def read_requirements():
    try:
        with open('requirements.txt', 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except FileNotFoundError:
        return []

setup(
    name="faceauth",
    version="1.0.0",
    author="FaceAuth Team",
    description="A privacy-first local face authentication system",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/faceauth",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Security :: Cryptography",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0"
        ]
    },
    entry_points={
        "console_scripts": [
            "faceauth=main:cli",
        ],
    },
    include_package_data=True,
    package_data={
        "faceauth": ["*.txt", "*.md"],
    },
    keywords="face recognition, authentication, security, privacy, local, biometrics",
    project_urls={
        "Bug Reports": "https://github.com/your-username/faceauth/issues",
        "Source": "https://github.com/your-username/faceauth",
        "Documentation": "https://github.com/your-username/faceauth/wiki",
    },
)