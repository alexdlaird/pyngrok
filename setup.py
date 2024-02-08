import os

from setuptools import setup, find_packages

__author__ = "Alex Laird"
__copyright__ = "Copyright 2024, Alex Laird"
__version__ = "7.1.1"

name = "pyngrok" if os.environ.get("BUILD_PACKAGE_AS_NGROK", "False") != "True" else "ngrok"

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name=name,
    version=__version__,
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "PyYAML"
    ],
    entry_points="""
        [console_scripts]
        ngrok=pyngrok.ngrok:main
        pyngrok=pyngrok.ngrok:main
    """,
    description="A Python wrapper for ngrok.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Alex Laird",
    author_email="contact@alexlaird.com",
    url="https://github.com/alexdlaird/pyngrok",
    project_urls={
        "Documentation": "https://pyngrok.readthedocs.io",
        "Changelog": "https://github.com/alexdlaird/pyngrok/blob/main/CHANGELOG.md",
        "Sponsor": "https://github.com/sponsors/alexdlaird"
    },
    license="MIT",
    classifiers=[
        "Development Status :: 6 - Mature",
        "Environment :: Console",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: OS Independent",
        "Operating System :: POSIX",
        "Operating System :: POSIX :: BSD :: FreeBSD",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Unix",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Database :: Database Engines/Servers",
        "Topic :: Internet :: Proxy Servers",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ]
)
