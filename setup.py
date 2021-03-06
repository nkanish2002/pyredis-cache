from sys import version_info, exit
from setuptools import setup, find_packages
from os import path

if version_info[0] < 3 and version_info[1] < 5:
    exit("Sorry, support only for Python 3.5 and above.")

here = path.abspath(path.dirname(__file__))
# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="pyredis-cache",
    version="0.1.3",
    description="Cache client for redis",
    url="https://github.com/nkanish2002/pyredis-cache",
    author="Anish Gupta",
    author_email="nkanish2002@gmail.com",
    license="MIT",
    install_requires=["redis", "hiredis"],
    package_dir={'tornado_razorpay': 'tornado_razorpay'},
    packages=find_packages(),
    keywords='redis cache client asyncio tornado',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.5",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ]
)
