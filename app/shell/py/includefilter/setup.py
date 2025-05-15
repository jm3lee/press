from setuptools import find_packages, setup

setup(
    name="includefilter",
    version="1.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "includefilter=includefilter:main",
        ],
    },
    install_requires=["PyYAML>=6.0"],
)
