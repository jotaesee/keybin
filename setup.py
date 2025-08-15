from setuptools import setup

setup(
    name="keybin",
    version="0.1",
    packages=["keybin"],
    install_requires=["typer[all]"],
    entry_points={
        "console_scripts": [
            "keybin = keybin.cli:app",
        ],
    },
)
