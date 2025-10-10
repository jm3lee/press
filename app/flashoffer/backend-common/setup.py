# Copyright (c) Flashoffer Developers
# Released under the MIT license.

from setuptools import setup, find_packages

setup(
    name="backend-common",
    version="0.1.0",
    description="Shared helpers for backend Flask services.",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "psycopg[pool]>=3.2,<4",
    ],
)
