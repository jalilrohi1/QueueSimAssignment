from setuptools import setup, find_packages

setup(
    name="storage_sim",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "humanfriendly",
        "numpy",
        # add other dependencies here
    ],
)