"""
Setup configuration for AI-SDLC package.
"""

from setuptools import find_packages, setup

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = [
        line.strip() for line in f if line.strip() and not line.startswith("#")
    ]

setup(
    name="ai-sdlc",
    version="0.1.0",
    description="AI-Driven Software Development Life Cycle for Databricks",
    long_description=open("../AI_SDLC_IMPLEMENTATION_PLAN.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Databricks Platform Team",
    author_email="platform-team@company.com",
    url="https://github.com/vivekgana/databricks-platform-marketplace",
    packages=find_packages(exclude=["tests", "tests.*"]),
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "ai-sdlc=ai_sdlc.cli.commands:cli",
        ],
    },
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Code Generators",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="ai sdlc databricks code-generation requirements llm claude",
)
