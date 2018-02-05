import os
from setuptools import find_packages, setup
from setuptools.command.install import install

import subprocess
dirname = os.path.dirname(os.path.realpath(__file__)) 

README_rst = os.path.join(dirname, 'README.md')

with open(README_rst, 'r') as f:
    long_description = f.read()

setup(
    name="twitch-betbot",
    version="1.0.0",
    packages=find_packages(),
    description="BetBot is an open source twitch bot for viewers to bet streamer game issue.",
    long_description=long_description,
    author="Tefa",
    author_email="tefa.devweb@gmail.com",
    url="",
    install_requires = [
        'tornado',
        'pyee',
        'pytest-runner'
    ],
    tests_require = [
        'pytest'
    ],
    keywords = [
        "twitch",
        "bot",
        "game",
        "IRC",
        "battleroyale"
    ],
    classifiers = [
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 2.7",
        "Environment :: Web Environment",
        "Topic :: Games/Entertainment",
        "Intended Audience :: Developers",
        "Intended Audience :: Telecommunications Industry"
    ]
)
