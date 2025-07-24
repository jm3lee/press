from setuptools import setup, find_packages

setup(
    name="pie",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],
    author="",
    author_email="",
    description="",
    url="",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'build-index=pie.build_index:main',
            'picasso=pie.picasso:main',
            'render-template=pie.render_template:main',
            'render-study-json=pie.render_study_json:main',
            'include-filter=pie.include_filter:main',
        ],
    },
)
