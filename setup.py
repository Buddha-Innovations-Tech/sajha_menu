from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

# get version from __version__ variable in sajha_menu/__init__.py
from sajha_menu import __version__ as version

setup(
    name="sajha_menu",
    version=version,
    description="OMS",
    author="akash",
    author_email="akashk@tunatechnology.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires
)
