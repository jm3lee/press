from setuptools import setup, find_packages

setup(
    name="distbuild",
    version="0.1.0",
    packages=find_packages(where="py"),
    package_dir={"": "py"},
    install_requires=[
        "fabric",
        "invoke",
    ],
    entry_points={
        "console_scripts": [
            "distbuild=distbuild.cli:main",
        ],
    },
)
