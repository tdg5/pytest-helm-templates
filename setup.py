from os import path
from typing import Dict, List, Tuple

from setuptools import find_packages, setup


VERSION_PATH = path.join(path.abspath(path.dirname(__file__)), "VERSION")

with open(VERSION_PATH, encoding="utf-8", mode="r") as f:
    VERSION = f.read().strip()

_dependencies = [
    "PyYaml~=6.0.1",
]

_dev_dependencies = [
    "black~=23.12.1",
    "build==1.0.3",
    "coverage==7.4.4",
    "coverage-badge==1.1.0",
    "dlint==0.14.1",
    "flake8-comprehensions==3.14.0",
    "flake8-eradicate==1.5.0",
    "flake8-spellcheck==0.28.0",
    "flake8-typing-imports==1.15.0",
    "flake8==7.0.0",
    "isort==5.13.2",
    "mypy~=1.8.0",
    "pep8-naming==0.13.3",
    "pre-commit==3.6.0",
    "pytest-mock~=3.12.0",
    "pytest-watch~=4.2.0",
    "pytest~=7.4.0",
    "safety==2.3.4",
    "twine==4.0.2",
    "types-PyYAML==6.0.12.20240311",
    "wheel>=0.42.0",
]


def _setup_packages() -> List:
    default_packages = [
        "pytest_helm_templates",
        "pytest_helm_templates.commands",
    ]
    return find_packages(
        ".",
        exclude=["*.__pycache__.*"],
        include=default_packages,
    )


def _setup_extras() -> Dict:
    return {
        "all": [
            _dependencies,
            _dev_dependencies,
        ],
        "deps": _dependencies,
        "dev": _dev_dependencies,
    }


def _setup_install_requires() -> List:
    return _dependencies


def _setup_entry_points() -> Dict:
    return {}


def _setup_long_description() -> Tuple[str, str]:
    return open("README.md", "r", encoding="utf-8").read(), "text/markdown"


setup(
    author="Danny Guinther",
    author_email="dannyguinther@gmail.com",
    classifiers=[
        "Framework :: Pytest",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    description="Pytest fixtures for unit testing the output of helm templates",
    entry_points=_setup_entry_points(),
    extras_require=_setup_extras(),
    include_package_data=True,
    install_requires=_setup_install_requires(),
    keywords="[TODO]",
    license="MIT",
    long_description=_setup_long_description()[0],
    long_description_content_type=_setup_long_description()[1],
    name="pytest-helm-templates",
    packages=_setup_packages(),
    python_requires=">=3.9.0",
    url="https://github.com/tdg5/pytest-helm-templates",
    version=VERSION,
)