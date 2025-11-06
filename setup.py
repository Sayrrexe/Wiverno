from setuptools import setup, find_packages
from pathlib import Path

version = "0.1.1"

with open(Path(__file__).resolve().parent / 'wiverno' / '__init__.py') as f:
    for line in f:
        if line.startswith('__version__'):
            version = line.split('=')[1].strip().strip('"')
            break

setup(
    name='wiverno',
    version=version,
    packages=find_packages(),
    install_requires=[
        'Jinja2==3.1.6',
        'MarkupSafe==3.0.3'
    ],
    python_requires='>=3.8',
    description='A lightweight WSGI framework',
)
