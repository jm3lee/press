from setuptools import setup, find_packages

setup(
    name="magicbar",
    version="0.1.0",
    packages=find_packages(),
    entry_points={'console_scripts': ['magicbar-index=magicbar.index:main']},
)
