import os

from setuptools import setup

__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "4.2.1"

name = "pyngrok" if os.environ.get("BUILD_PACKAGE_AS_NGROK", "False") != "True" else "ngrok"

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name=name,
    version=__version__,
    packages=["pyngrok"],
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*",
    install_requires=[
        "future",
        "PyYAML"
    ],
    entry_points="""
        [console_scripts]
        ngrok=pyngrok.ngrok:main
        pyngrok=pyngrok.ngrok:main
    """,
    include_package_data=True,
    description="A Python wrapper for Ngrok.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Alex Laird",
    author_email="contact@alexlaird.com",
    url="https://github.com/alexdlaird/pyngrok",
    download_url="https://github.com/alexdlaird/pyngrok/archive/{}.tar.gz".format(__version__),
    project_urls={
        "Documentation": "https://pyngrok.readthedocs.io",
        "Changelog": "https://github.com/alexdlaird/pyngrok/blob/master/CHANGELOG.md",
        "Sponsor": "https://www.paypal.me/alexdlaird"
    },
    keywords=["ngrok", "tunnel", "tunneling", "webhook", "localhost", "reverse-proxy", "localtunnel"],
    license="MIT",
    classifiers=[
        "Environment :: Console",
        "Environment :: Web Environment",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Operating System :: POSIX :: BSD :: FreeBSD",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Unix",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Database :: Database Engines/Servers",
        "Topic :: Internet",
        "Topic :: Internet :: Proxy Servers",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ]
)
