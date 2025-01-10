# setup.py
from setuptools import setup, find_packages

setup(
    name="shekaracode",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'dash>=2.14.2',
        'PyGithub>=2.1.1',
        'openai>=1.3.7',
        'python-dotenv>=1.0.0',
        'pydantic>=2.5.2',
        'pydantic-settings>=2.1.0',
        'pandas>=2.1.3',
        'plotly>=5.18.0',
        'asyncio>=3.4.3',
        'aiohttp>=3.9.1',
        'tenacity>=8.2.3',
        'loguru>=0.7.2'
    ],
)