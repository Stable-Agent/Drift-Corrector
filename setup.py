"""Setup configuration for drift-corrector package."""

from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="drift-corrector",
    version="0.1.0",
    author="Stable-Agent Contributors",
    author_email="bradyt2215@gmail.com",
    description="Automatic correction prompts for drifting LLM agents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Stable-Agent/Drift-Corrector",
    project_urls={
        "Bug Tracker": "https://github.com/Stable-Agent/Drift-Corrector/issues",
        "Documentation": "https://github.com/Stable-Agent/Drift-Corrector/tree/main/docs",
        "Source Code": "https://github.com/Stable-Agent/Drift-Corrector",
        "Stable-Agent Ecosystem": "https://github.com/Stable-Agent",
    },
    packages=["drift_corrector"],
    package_dir={"drift_corrector": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
    ],
    python_requires=">=3.9",
    install_requires=[
        # No required deps - pure Python
    ],
    extras_require={
        "detector": [
            "drift-detector>=0.1.0",  # For integration
        ],
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "ruff>=0.1.0",
        ],
    },
    keywords=[
        "llm", "drift", "correction", "agents", "multi-turn",
        "stability", "ai-safety", "prompt-engineering",
    ],
)
