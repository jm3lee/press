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
            'update-index=pie.update_index:main',
            'update-pubdate=pie.update_pubdate:main',
            'update-author=pie.update_author:main',
            'picasso=pie.picasso:main',
            'render-jinja-template=pie.render_jinja_template:main',
            'render-study-json=pie.render_study_json:main',
            'include-filter=pie.include_filter:main',
            'process-yaml=pie.process_yaml:main',
            'detect-html-dicts=pie.detect_html_dicts:main',
            'indextree-json=pie.indextree_json:main',
            'gen-markdown-index=pie.gen_markdown_index:main',
            'check-page-title=pie.check_page_title:main',
            'check-post-build=pie.check_post_build:main',
            'create-post=pie.create_post:main',
        ],
    },
)
