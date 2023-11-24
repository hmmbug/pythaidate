from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

short_description = "Date classes for Thai calendar systems."
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="pythaidate",
    version="0.1.5",  # major, minor, fix
    description=short_description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hmmbug/pythaidate",
    author="Mark Hollow",
    author_email="dev@hmmbug.com",
    # For a list of valid classifiers, see https://pypi.org/classifiers/
    classifiers=[
        "Development Status :: 3 - Alpha",
        # Indicate who your project is intended for
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Localization",
        "License :: OSI Approved :: MIT License",
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate you support Python 3. These classifiers are *not*
        # checked by 'pip install'. See instead 'python_requires' below.
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords="date, calendar, thai, development, library",
    packages=find_packages(
        include=['pythaidate'], 
    ),
    python_requires=">=3.8, <4",
    install_requires=[],
    extras_require={
        "dev": ["check-manifest"],
        "test": ["coverage"],
    },
    include_package_data=True,
    package_data={
        "tests.data": [
            "cs.min.json",
            "julian.json",
            "pak.min.data",
        ]
    },
    entry_points={
        "console_scripts": [
            "paktoday=pythaidate.cli:paktoday",
            "cstoday=pythaidate.cli:cstoday",
        ],
    },
    project_urls={  # Optional
        # https://packaging.python.org/specifications/core-metadata/#project-url-multiple-use
        "Bug Reports": "https://github.com/hmmbug/pythaidate/issues",
        "Source": "https://github.com/hmmbug/pythaidate/",
    },
)
