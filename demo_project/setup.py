from setuptools import setup, find_packages

setup(
    name="demo_project",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[],
    author="Twój autor",
    description="Opis projektu",
)