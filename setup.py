from setuptools import setup

__author__ = "Alex Laird"
__copyright__ = "Copyright 2018, Alex Laird"
__version__ = "1.0.0"

with open("README.md") as f:
    long_description = f.read()

setup(
    name="pyngrok",
    version=__version__,
    packages=["pyngrok"],
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
    install_requires=[
        "future",
    ],
    description="A Python wrapper for Ngrok.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Alex Laird",
    author_email="contact@alexlaird.com",
    url='https://github.com/alexdlaird/pyngrok',
    download_url='https://github.com/alexdlaird/pyngrok/archive/{}.tar.gz'.format(__version__),
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
