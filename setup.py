from os import path
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))
with open(path.join(here, "README.md"), encoding="utf-8") as file:
    read_me = file.read()

setup(
    name="kit-dl",
    version="1.0.2",
    description="An unofficial assignments downloader for the KIT Ilias website.",
    long_description=read_me,
    long_description_content_type="text/markdown",
    url="https://github.com/jonasstr/kit-assignments-downloader",
    license="MIT",
    author="Jonas Strittmatter",
    author_email="uzxhf@student.kit.edu",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Utilities",
    ],
    packages=find_packages(),
    package_data={"": ["LICENSE", "config.yml", "geckodriver.exe"]},
    test_suite="tests",
    include_package_data=True,
    install_requires=["click", "colorama", "ruamel.yaml>0.15", "selenium>=3"],
    entry_points={"console_scripts": ["kit-dl=kit_dl.cli:cli"]},
)
