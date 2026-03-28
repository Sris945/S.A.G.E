#!/usr/bin/env python3
"""
Backward-compatible install shim — project metadata lives in ``pyproject.toml`` (PEP 621).

``pip install .`` / legacy tooling that still invoke ``setup.py`` will delegate to setuptools,
which reads ``pyproject.toml`` when using setuptools >= 61.
"""
from setuptools import setup

if __name__ == "__main__":
    setup()
